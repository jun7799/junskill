#!/usr/bin/env python3
"""
每日热门文章猎手 - 热度计算脚本

热度计算算法：
1. 时间衰减因子：越新的文章权重越高
2. 关键词匹配：标题匹配目标领域关键词
3. 平台权重：不同平台的权重不同
4. 综合热度分数 = (归一化指标加权) * 平台权重
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import os

SCRIPT_DIR = Path(__file__).parent


class TrendingCalculator:
    """热度计算器"""

    def __init__(self, config: Dict):
        self.config = config
        self.keywords = self._load_keywords()
        self.platform_weights = config.get("trending", {}).get("platform_weights", {
            "公众号": 1.2,
            "HackerNews": 1.0,
            "dev.to": 0.9,
            "掘金": 1.1
        })
        self.min_score = config.get("trending", {}).get("min_score", 50)
        self.time_decay_hours = config.get("trending", {}).get("time_decay_hours", 72)

    def _load_keywords(self) -> Dict[str, List[str]]:
        """加载关键词配置"""
        keywords_config = self.config.get("keywords", {
            "AI工具": ["Claude", "Gemini", "Trae", "ChatGPT", "AI写作", "AI编程", "Copilot", "Cursor"],
            "网页开发": ["Vercel", "部署", "前端", "React", "Next.js", "Node.js", "CSS", "HTML", "JavaScript", "TypeScript"],
            "内容创作": ["公众号", "爆文", "写作", "SEO", "内容营销", "标题优化", "流量"]
        })
        return keywords_config

    def calculate_time_decay(self, published_at: str) -> float:
        """
        计算时间衰减因子

        越新的文章权重越高，使用指数衰减
        """
        try:
            published_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            hours_ago = (datetime.now() - published_time).total_seconds() / 3600

            # 指数衰减：越新越接近1
            decay_factor = 1.0 / (1.0 + (hours_ago / self.time_decay_hours) * 0.5)
            return decay_factor
        except:
            return 0.5  # 解析失败给中等权重

    def calculate_keyword_score(self, title: str) -> tuple[float, List[str]]:
        """
        计算关键词匹配分数

        返回：(匹配分数, 匹配到的关键词列表)
        """
        title_lower = title.lower()
        matched_keywords = []
        total_matches = 0

        for domain, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    matched_keywords.append(f"{domain}:{keyword}")
                    total_matches += 1

        # 匹配分数 = 匹配数 / 总关键词数的加权
        total_keywords = sum(len(kws) for kws in self.keywords.values())
        keyword_score = min(1.0, total_matches / max(1, total_keywords * 0.3))

        return keyword_score, matched_keywords

    def normalize_metrics(self, raw_metrics: Dict, source: str) -> Dict[str, float]:
        """
        归一化热度指标

        不同平台的指标量级不同，需要归一化到0-1范围
        """
        # 定义各指标的"高热度"基准值（经验值）
        baselines = {
            "HackerNews": {"likes": 200, "comments": 100, "views": 0},
            "dev.to": {"likes": 50, "comments": 20, "views": 5000},
            "掘金": {"likes": 100, "comments": 50, "views": 10000},
            "公众号": {"likes": 0, "comments": 0, "views": 0}
        }

        baseline = baselines.get(source, baselines["HackerNews"])

        normalized = {}
        for metric, value in raw_metrics.items():
            max_value = baseline.get(metric, 100)
            if max_value > 0:
                # 使用对数平滑，避免极端值
                normalized[metric] = min(1.0, value / max_value)
            else:
                normalized[metric] = 0

        return normalized

    def classify_domain(self, title: str, matched_keywords: List[str]) -> List[str]:
        """根据匹配的关键词分类文章领域"""
        domains = set()

        for keyword_entry in matched_keywords:
            if ":" in keyword_entry:
                domain, _ = keyword_entry.split(":", 1)
                domains.add(domain)

        # 如果没有匹配到关键词，根据标题推断
        if not domains:
            title_lower = title.lower()
            if any(kw in title_lower for kw in ["api", "代码", "programming", "开发", "deployment"]):
                domains.add("网页开发")
            elif any(kw in title_lower for kw in ["ai", "claude", "gemini", "chatgpt", "llm"]):
                domains.add("AI工具")

        return list(domains) if domains else ["其他"]

    def calculate_article_score(self, article: Dict) -> Dict:
        """
        计算单篇文章的综合热度分数

        返回包含额外字段的增强文章数据
        """
        # 1. 提取基础数据
        title = article.get("title", "")
        source = article.get("source", "")
        raw_metrics = article.get("raw_metrics", {})
        published_at = article.get("published_at", "")

        # 2. 计算时间衰减
        time_decay = self.calculate_time_decay(published_at)

        # 3. 计算关键词匹配
        keyword_score, matched_keywords = self.calculate_keyword_score(title)

        # 4. 归一化指标
        normalized = self.normalize_metrics(raw_metrics, source)

        # 5. 计算综合热度分数
        # 权重分配：点赞30%、浏览20%、评论20%、关键词20%、时间10%
        trending_score = (
            normalized.get("likes", 0) * 0.3 +
            normalized.get("views", 0) * 0.2 +
            normalized.get("comments", 0) * 0.2 +
            keyword_score * 0.2 +
            time_decay * 0.1
        ) * 100  # 转换为0-100分制

        # 6. 应用平台权重
        platform_weight = self.platform_weights.get(source, 1.0)
        final_score = trending_score * platform_weight

        # 7. 限制在0-100范围
        final_score = min(100, max(0, final_score))

        # 8. 分类文章领域
        domains = self.classify_domain(title, matched_keywords)

        # 返回增强后的文章数据
        result = article.copy()
        result.update({
            "trending_score": round(final_score, 2),
            "domains": domains,
            "matched_keywords": matched_keywords,
            "time_decay": round(time_decay, 3),
            "keyword_score": round(keyword_score, 3),
            "fetched_at": datetime.now().isoformat()
        })

        return result

    def calculate_batch(self, articles: List[Dict]) -> List[Dict]:
        """批量计算文章热度"""
        results = []

        for article in articles:
            scored_article = self.calculate_article_score(article)

            # 过滤低热度文章
            if scored_article["trending_score"] >= self.min_score:
                results.append(scored_article)

        # 按热度分数排序
        results.sort(key=lambda x: x["trending_score"], reverse=True)

        return results


def load_config(config_path: str = None) -> Dict:
    """加载配置文件"""
    if config_path is None:
        config_path = SCRIPT_DIR.parent / "assets" / "config.json"

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "keywords": {
            "AI工具": ["Claude", "Gemini", "Trae", "ChatGPT"],
            "网页开发": ["Vercel", "部署", "前端", "React"],
            "内容创作": ["公众号", "爆文", "写作"]
        },
        "trending": {
            "min_score": 50,
            "time_decay_hours": 72,
            "platform_weights": {
                "公众号": 1.2,
                "HackerNews": 1.0,
                "dev.to": 0.9,
                "掘金": 1.1
            }
        }
    }


def load_articles(input_path: str = None) -> List[Dict]:
    """加载原始文章数据"""
    if input_path is None:
        input_path = SCRIPT_DIR.parent / "data" / "articles_raw.json"

    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def save_scored_articles(articles: List[Dict], output_path: str = None):
    """保存计算热度的文章数据"""
    if output_path is None:
        output_path = SCRIPT_DIR.parent / "data" / "articles_scored.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(articles)} 篇文章到: {output_path}")


if __name__ == "__main__":
    # 加载配置和数据
    config = load_config()
    articles = load_articles()

    if not articles:
        print("没有找到文章数据，请先运行 fetch_articles.py")
        exit(1)

    # 计算热度
    calculator = TrendingCalculator(config)
    scored_articles = calculator.calculate_batch(articles)

    print(f"\n热度计算完成:")
    print(f"  原始文章数: {len(articles)}")
    print(f"  高热度文章数: {len(scored_articles)} (热度 >= {config.get('trending', {}).get('min_score', 50)})")

    # 显示TOP 10
    print(f"\nTOP 10 热门文章:")
    for i, article in enumerate(scored_articles[:10], 1):
        title_safe = article['title'][:50].encode('gbk', errors='ignore').decode('gbk')
        print(f"  {i}. [{article['trending_score']:.1f}fen] {title_safe}... ({article['source']})")

    # 保存结果
    save_scored_articles(scored_articles)
