#!/usr/bin/env python3
"""
每日热门文章猎手 - 多数据源文章抓取脚本

支持的数据源：
- HackerNews API
- dev.to API
- 掘金 API
- we-mp-rss (公众号RSS)
"""

import requests
import json
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from pathlib import Path

# 添加当前脚本目录到Python路径
SCRIPT_DIR = Path(__file__).parent


class ArticleFetcher:
    """文章抓取器基类"""

    def __init__(self, config: Dict):
        self.config = config

    def fetch(self) -> List[Dict]:
        """抓取文章，返回统一格式的数据"""
        raise NotImplementedError


class HackerNewsFetcher(ArticleFetcher):
    """HackerNews API 抓取器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_url = config.get("api_url", "https://hacker-news.firebaseio.com/v0")
        self.limit = config.get("top_stories_limit", 30)

    def fetch(self) -> List[Dict]:
        """获取HackerNews热门文章"""
        articles = []

        try:
            # 获取热门故事ID列表
            response = requests.get(f"{self.api_url}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()[:self.limit]

            for story_id in story_ids:
                try:
                    # 获取故事详情
                    story_response = requests.get(f"{self.api_url}/item/{story_id}.json")
                    story_response.raise_for_status()
                    story = story_response.json()

                    # 只保留有URL的文章（过滤掉Ask HN等讨论帖）
                    if story.get("url"):
                        articles.append({
                            "title": story.get("title", ""),
                            "url": story.get("url", ""),
                            "source": "HackerNews",
                            "author": story.get("by", ""),
                            "published_at": datetime.fromtimestamp(story.get("time", 0)).isoformat(),
                            "raw_metrics": {
                                "likes": story.get("score", 0),
                                "comments": story.get("descendants", 0),
                                "views": 0  # HN不提供浏览量
                            }
                        })
                except Exception as e:
                    print(f"获取HN故事 {story_id} 失败: {e}")
                    continue

        except Exception as e:
            print(f"HackerNews抓取失败: {e}")

        return articles


class DevToFetcher(ArticleFetcher):
    """dev.to API 抓取器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_url = config.get("api_url", "https://dev.to/api")
        self.limit = config.get("top_articles_limit", 20)

    def fetch(self) -> List[Dict]:
        """获取dev.to热门文章"""
        articles = []

        try:
            # 获取热门文章（按过去一周的点赞数排序）
            response = requests.get(
                f"{self.api_url}/articles",
                params={
                    "top": "7",
                    "per_page": self.limit
                },
                headers={"User-Agent": "Daily-Trending-Articles-Hunter/1.0"}
            )
            response.raise_for_status()

            for post in response.json():
                published_at = datetime.fromisoformat(
                    post.get("published_at", "").replace("Z", "+00:00")
                ).isoformat()

                articles.append({
                    "title": post.get("title", ""),
                    "url": post.get("url", ""),
                    "source": "dev.to",
                    "author": post.get("user", {}).get("name", ""),
                    "published_at": published_at,
                    "raw_metrics": {
                        "likes": post.get("positive_reactions_count", 0),
                        "comments": post.get("comments_count", 0),
                        "views": post.get("page_views_count", 0)
                    }
                })

        except Exception as e:
            print(f"dev.to抓取失败: {e}")

        return articles


class JuejinFetcher(ArticleFetcher):
    """掘金 API 抓取器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_url = config.get("api_url", "https://api.juejin.cn")
        self.category = config.get("category", "backend")
        self.limit = config.get("top_articles_limit", 20)

    def fetch(self) -> List[Dict]:
        """获取掘金热门文章"""
        articles = []

        try:
            # 掘金推荐文章API（无需认证的公开接口）
            response = requests.post(
                f"{self.api_url}/recommend_api/v1/article/recommend_all_feed",
                json={
                    "id_type": 2,
                    "sort_type": 200,
                    "cursor": "0",
                    "limit": self.limit
                },
                headers={
                    "User-Agent": "Daily-Trending-Articles-Hunter/1.0"
                }
            )

            if response.status_code == 200:
                data = response.json()

                for item in data.get("data", []):
                    article = item.get("item", {}).get("article", {})
                    if not article.get("article_id"):
                        continue

                    articles.append({
                        "title": article.get("title", ""),
                        "url": article.get("article_url", f"https://juejin.cn/post/{article.get('article_id')}"),
                        "source": "掘金",
                        "author": article.get("author", {}).get("user_name", ""),
                        "published_at": datetime.fromtimestamp(article.get("ctime", 0) / 1000).isoformat(),
                        "raw_metrics": {
                            "likes": article.get("digg_count", 0),
                            "comments": article.get("comment_count", 0),
                            "views": article.get("view_count", 0)
                        }
                    })

        except Exception as e:
            print(f"掘金抓取失败: {e}")

        return articles


class WeMPRSSFetcher(ArticleFetcher):
    """微信公众号RSS抓取器 (基于WeRSS项目)"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_url = config.get("api_url", "http://localhost:8001")
        self.token = config.get("token", "")
        self.limit = config.get("limit", 50)

    def fetch(self) -> List[Dict]:
        """从WeRSS获取公众号文章"""
        articles = []

        if not self.token:
            print("  请在config.json中配置we_mp_rss.token")
            print("  获取方式: 打开 http://localhost:8001/api/docs 登录后从浏览器开发者工具获取")
            return articles

        try:
            # 调用 WeRSS API 获取文章列表
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            # 获取最近的文章
            params = {
                "limit": self.limit,
                "offset": 0
            }

            response = requests.get(
                f"{self.api_url}/api/v1/wx/articles",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                # WeRSS 返回格式: {"code": 0, "data": {"list": [...]}}
                if data.get("code") == 0:
                    articles_data = data.get("data", {})
                    posts = articles_data.get("list", []) if isinstance(articles_data, dict) else articles_data

                    if not posts:
                        print(f"  -> 没有获取到文章，请确认已订阅公众号")
                        return articles

                    print(f"  -> 获取到 {len(posts)} 篇文章")

                    for post in posts:
                        # 只获取最近24小时的文章
                        try:
                            publish_time = post.get("publish_time", 0)
                            if publish_time:
                                # WeRSS 的 publish_time 是整数时间戳（秒）
                                if isinstance(publish_time, int):
                                    published_time = datetime.fromtimestamp(publish_time)
                                else:
                                    # 字符串格式
                                    published_time = datetime.fromisoformat(str(publish_time).replace("Z", "+00:00"))
                            else:
                                continue

                            if datetime.now() - published_time > timedelta(hours=24):
                                continue

                            articles.append({
                                "title": post.get("title", ""),
                                "url": post.get("url", ""),
                                "source": "公众号",
                                "author": post.get("mp_name", post.get("author", "")),
                                "published_at": published_time.isoformat(),
                                "raw_metrics": {
                                    "likes": 0,  # 公众号API通常不提供
                                    "comments": 0,
                                    "views": 0
                                }
                            })
                        except Exception as e:
                            print(f"  处理文章出错: {e}")
                            continue
                else:
                    print(f"  API返回错误: {data.get('msg', 'Unknown error')}")
            else:
                print(f"  we-mp-rss API未响应: {response.status_code}")
                print(f"  响应内容: {response.text[:200]}")

        except requests.exceptions.ConnectionError:
            print("  we-mp-rss服务未运行，请确认服务已启动")
        except Exception as e:
            print(f"  公众号抓取失败: {e}")

        return articles


def load_config(config_path: str = None) -> Dict:
    """加载配置文件"""
    if config_path is None:
        config_path = SCRIPT_DIR.parent / "assets" / "config.json"

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 返回默认配置
    return {
        "data_sources": {
            "hackernews": {"enabled": True, "top_stories_limit": 30},
            "devto": {"enabled": True, "top_articles_limit": 20},
            "juejin": {"enabled": True, "top_articles_limit": 20},
            "we_mp_rss": {"enabled": True, "api_url": "http://localhost:3000/api"}
        }
    }


def fetch_all_articles(config: Dict = None) -> List[Dict]:
    """从所有启用的数据源抓取文章"""
    if config is None:
        config = load_config()

    all_articles = []
    sources_config = config.get("data_sources", {})

    # 定义所有可用的抓取器
    fetchers = [
        ("HackerNews", HackerNewsFetcher, "hackernews"),
        ("dev.to", DevToFetcher, "devto"),
        ("掘金", JuejinFetcher, "juejin"),
        ("公众号", WeMPRSSFetcher, "we_mp_rss"),
    ]

    for name, fetcher_class, config_key in fetchers:
        source_config = sources_config.get(config_key, {})
        if not source_config.get("enabled", False):
            continue

        print(f"正在抓取 {name}...")
        try:
            fetcher = fetcher_class(source_config)
            articles = fetcher.fetch()
            all_articles.extend(articles)
            print(f"  -> 获取到 {len(articles)} 篇文章")
        except Exception as e:
            print(f"  -> 抓取失败: {e}")

    return all_articles


def save_articles(articles: List[Dict], output_path: str = None):
    """保存抓取的文章到JSON文件"""
    if output_path is None:
        output_path = SCRIPT_DIR.parent / "data" / "articles_raw.json"

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"文章已保存到: {output_path}")


if __name__ == "__main__":
    # 执行抓取
    articles = fetch_all_articles()
    print(f"\n总共抓取到 {len(articles)} 篇文章")

    # 保存结果
    save_articles(articles)
