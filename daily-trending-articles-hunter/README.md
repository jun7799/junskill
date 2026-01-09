# 每日热门文章猎手

每天自动从多个技术平台抓取热门文章，计算热度并输出到飞书多维表格。

## 数据源

- HackerNews
- dev.to
- 掘金
- 微信公众号 (需要 we-mp-rss)

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 配置飞书凭证（环境变量或 config.json）
3. 运行：`python scripts/scheduler.py --mode manual`

## 配置飞书

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_BITABLE_APP_TOKEN="your_app_token"
export FEISHU_TABLE_ID="your_table_id"
```

## 定时运行

```bash
python scripts/scheduler.py --mode schedule --cron "0 9 * * *"
```

详细说明请查看 [SKILL.md](./SKILL.md)
