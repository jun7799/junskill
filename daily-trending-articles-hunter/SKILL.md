---
name: daily-trending-articles-hunter
description: 每日从多个数据源（公众号、HackerNews、dev.to、掘金）抓取热门技术文章，计算热度分数并输出到飞书多维表格。支持手动触发和定时自动运行。适用于需要跟踪AI工具、网页开发、内容创作等领域最新热点的用户。
license: MIT
---

# Daily Trending Articles Hunter

每天自动收集和整理技术领域的热门文章，帮你追踪行业热点。

## 核心功能

1. **多源数据抓取**：从微信公众号、HackerNews、dev.to、掘金等平台抓取最新技术文章
2. **智能热度计算**：基于阅读量、点赞数、发布时间、关键词匹配度计算综合热度分数
3. **飞书表格输出**：自动将结果写入飞书多维表格，支持去重和增量更新
4. **定时自动运行**：支持cron表达式配置定时任务，每天自动抓取

## 首次使用配置

### 步骤1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2：配置文件

复制配置模板并修改：

```bash
cp assets/config_template.json assets/config.json
```

编辑 `assets/config.json`，配置：

1. **数据源开关**：启用/禁用各数据源
2. **关键词配置**：根据你的关注领域调整关键词
3. **热度参数**：调整最低热度分数、时间衰减等参数

### 步骤3：配置飞书

1. 创建飞书应用并获取凭证
   - 访问 [飞书开放平台](https://open.feishu.cn/)
   - 创建企业自建应用
   - 开通 `bitable:app` 权限

2. 创建多维表格
   - 按照 `assets/feishu_schema.json` 创建字段
   - 获取 `app_token` 和 `table_id`

3. 设置环境变量（推荐方式）：

```bash
# Windows PowerShell
$env:FEISHU_APP_ID="your_app_id"
$env:FEISHU_APP_SECRET="your_app_secret"
$env:FEISHU_BITABLE_APP_TOKEN="your_app_token"
$env:FEISHU_TABLE_ID="your_table_id"
```

或者在 `config.json` 中直接填入凭证。

## 使用方式

### 方式1：通过Claude Code调用

直接告诉Claude你的需求：

```
帮我抓取今天的热门文章
```

```
查看最新的技术文章热点
```

### 方式2：手动运行脚本

```bash
# 执行完整流程（抓取 + 计算 + 写入）
python scripts/scheduler.py --mode manual
```

### 方式3：设置定时任务

#### Windows任务计划程序

```powershell
schtasks /create /tn "每日热门文章猎手" /tr "python scheduler.py --mode schedule" /sc daily /st 09:00
```

#### Python schedule库

```bash
python scripts/scheduler.py --mode schedule --cron "0 9 * * *"
```

## 工作流程

1. **抓取阶段** (`fetch_articles.py`)
   - 从各数据源获取最新文章列表
   - 提取文章元数据（标题、链接、发布时间、热度指标）
   - 保存到 `data/articles_raw.json`

2. **计算阶段** (`calculate_trending.py`)
   - 基于关键词匹配和时间衰减计算热度分数
   - 过滤低热度文章（默认分数 < 50）
   - 按热度排序
   - 保存到 `data/articles_scored.json`

3. **输出阶段** (`feishu_client.py`)
   - 写入飞书多维表格
   - 基于URL自动去重
   - 生成执行报告

## 脚本说明

### fetch_articles.py

多数据源文章抓取器

**功能**：
- HackerNews API：获取热门技术讨论
- dev.to API：获取开发博客热门文章
- 掘金 API：获取中文技术社区热门文章
- we-mp-rss：获取已订阅公众号的最新文章

**输出格式**：
```json
{
  "title": "文章标题",
  "url": "文章链接",
  "source": "数据来源",
  "author": "作者",
  "published_at": "发布时间(ISO格式)",
  "raw_metrics": {
    "views": 阅读量,
    "likes": 点赞数,
    "comments": 评论数
  }
}
```

### calculate_trending.py

热度评分算法

**计算公式**：
```
热度分数 = (
    归一化点赞数 × 0.3 +
    归一化浏览量 × 0.2 +
    归一化评论数 × 0.2 +
    关键词匹配度 × 0.2 +
    时间衰减因子 × 0.1
) × 平台权重
```

**平台权重**：
- 公众号：1.2
- 掘金：1.1
- HackerNews：1.0
- dev.to：0.9

### feishu_client.py

飞书API封装

**功能**：
- 认证管理
- 批量写入记录
- URL去重
- 字段映射和数据类型转换

### scheduler.py

任务调度器

**运行模式**：
- `--mode manual`：手动触发，立即执行
- `--mode schedule`：定时模式，持续运行
- `--cron "0 9 * * *"`：设置执行时间

## 数据输出格式

飞书多维表格字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | 文本 | 文章标题 |
| 链接 | URL | 文章链接（唯一标识） |
| 来源 | 单选 | 公众号/HN/dev.to/掘金 |
| 领域 | 多选 | AI工具/网页开发/内容创作 |
| 发布时间 | 日期 | 文章发布时间 |
| 阅读量 | 数字 | 文章阅读量 |
| 点赞数 | 数字 | 点赞/在看数 |
| 评论数 | 数字 | 评论数 |
| 热度分数 | 数字 | 综合热度(0-100) |
| 关键词匹配 | 文本 | 匹配到的关键词 |
| 抓取时间 | 日期 | 数据抓取时间 |

## 自定义配置

### 调整关注领域

编辑 `assets/config.json` 中的 `keywords` 部分：

```json
{
  "keywords": {
    "新领域": ["关键词1", "关键词2", "关键词3"]
  }
}
```

### 调整热度阈值

修改 `trending.min_score` 参数：

```json
{
  "trending": {
    "min_score": 60  // 只保留热度分数 >= 60 的文章
  }
}
```

### 调整时间衰减

修改 `trending.time_decay_hours` 参数：

```json
{
  "trending": {
    "time_decay_hours": 48  // 48小时内的文章权重更高
  }
}
```

## 故障排除

### 问题1：公众号抓取失败

**原因**：we-mp-rss 服务未运行

**解决**：
1. 确认 Docker 容器是否运行
2. 检查 API 地址是否正确
3. 查看容器日志

### 问题2：飞书写入失败

**原因**：凭证配置错误或权限不足

**解决**：
1. 检查环境变量是否设置
2. 确认应用已开通 `bitable:app` 权限
3. 验证 app_token 和 table_id 是否正确
4. 检查表格字段名称是否与 schema 一致

### 问题3：热度分数偏低

**原因**：关键词匹配度低或文章较旧

**解决**：
1. 添加更多相关关键词
2. 降低 `min_score` 阈值
3. 调整 `time_decay_hours` 参数
4. 检查平台权重设置

### 问题4：定时任务不执行

**原因**：cron表达式格式错误

**解决**：
- 格式：`分 时 日 月 周`
- 示例：`0 9 * * *` = 每天早上9点
- Windows 任务计划程序使用简化格式

## 相关文件

- `references/feishu_api_docs.md`：飞书API详细文档
- `references/keywords.md`：关键词配置说明
- `assets/config_template.json`：配置文件模板
- `assets/feishu_schema.json`：飞书表结构定义
