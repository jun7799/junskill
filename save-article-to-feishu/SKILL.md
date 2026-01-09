---
name: save-article-to-feishu
description: Save article information to Feishu multidimensional table. Use this skill when user provides an article link and asks to save it to Feishu (or says "保存到飞书", "收藏到飞书", etc.). Supports both regular web pages and WeChat Official Account articles (requires chrome-devtools-mcp for WeChat articles). Extracts title, URL, keywords, summary (markdown), source platform, and author, then saves to Feishu bitable via API.
---

# Save Article to Feishu

## Overview

Parse article URLs and extract structured information, then save to Feishu multidimensional table (Bitable). Supports regular web pages and WeChat Official Account articles.

## When to Use This Skill

Trigger this skill when user provides an article URL and asks to save/collect to Feishu. Common trigger phrases:
- "保存到飞书" / "收藏到飞书"
- "Save to Feishu" / "Save article to Feishu"
- "把这个文章存到飞书"
- User provides URL and mentions Feishu storage

## Workflow

### Step 1: Identify Article Type

First, identify the article type from the URL:

**WeChat Official Account (公众号) articles:**
- URL contains `mp.weixin.qq.com`
- Requires special handling with chrome-devtools-mcp

**Regular web pages:**
- All other URLs
- Can use webReader or direct scraping

### Step 2: Extract Article Information

Extract the following fields from the article:

| Field | Description | Notes |
|-------|-------------|-------|
| 文章标题 | Article title | From page `<title>`, `<h1>`, or og:title meta tag |
| 文章链接 | Article URL | Provided by user |
| 文章主题关键词 | 3 keywords | Extract key topics/themes from content |
| 文章梗概 | Summary (markdown) | Chinese summary in markdown format with key points |
| 来源平台 | Source platform | Detect from URL domain (e.g., "公众号", "掘金", "dev.to", "HackerNews") |
| 作者 | Author | Extract from article meta or byline |
| 发布时间 | Publish time | Extract from article meta or publication date |

### Step 3: Fetch Article Content

#### For Regular Web Pages

Use the webReader MCP tool:

```
Use webReader with:
- url: the article URL
- return_format: markdown (default)
- retain_images: false (not needed for text extraction)
```

Extract information from the returned markdown content.

#### For WeChat Official Account Articles

WeChat articles require browser rendering. Use chrome-devtools-mcp:

1. **Navigate to the article:**
   ```
   mcp__mcpServers__navigate_page with:
   - type: url
   - url: the WeChat article URL
   ```

2. **Take snapshot to get page content:**
   ```
   mcp__mcpServers__take_snapshot
   ```

3. **Extract title and content from the snapshot**

**Important:** WeChat articles may have restricted access. If the article cannot be accessed, inform the user and ask them to provide the article content manually.

### Step 4: Process and Validate Information

After extracting raw content:

1. **Title:** Clean up any suffixes like " | 公众号名称" or " - 原文链接"
2. **Keywords:** Generate 3 relevant keywords based on article content
3. **Summary:** Create a Chinese summary in markdown format with key points, capturing the main content of the article. Format example:
   ```markdown
   ## 标题

   ### 核心观点
   - 观点1
   - 观点2

   ### 关键信息
   内容描述...
   ```
4. **Source Platform:** Map domain to platform name:
   - `mp.weixin.qq.com` → "公众号"
   - `juejin.cn` → "掘金"
   - `dev.to` → "dev.to"
   - `news.ycombinator.com` → "HackerNews"
   - `anthropic.com` → "Anthropic官网"
   - Others → Use domain name or generic "网页"
5. **Author:** Extract from byline, meta author, or article footer
6. **Publish Time:** Extract publication date from article meta or page content (e.g., "2025年12月29日", "Dec 29, 2025")

### Step 5: Save to Feishu Bitable

**IMPORTANT: Use the provided Python script to avoid encoding issues on Windows.**

The `scripts/save_to_feishu.py` script handles UTF-8 encoding properly for Windows environments. Always call this script instead of writing inline Python code.

**Usage:**
```bash
python "C:\Users\44162\.claude\skills\save-article-to-feishu\scripts\save_to_feishu.py" \
  --title "文章标题" \
  --url "文章链接" \
  --keywords "关键词1,关键词2,关键词3" \
  --summary "文章摘要(markdown格式)" \
  --platform "来源平台" \
  --author "作者名" \
  --publish-time "发布时间(可选)"
```

**Feishu Configuration (embedded in script):**
```
App ID: cli_a9c593c3f6e15cb6
App Secret: NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ
Base ID: XGqVbRXijaegF0ssTFCcTQ68nRd
Table ID: tblYY3JCuszQJ0Pb
```

### Step 6: Confirm and Report

After saving:

1. Confirm success to user with the extracted information
2. Show what was saved (title, keywords, summary preview)
3. If any field is missing (e.g., author not found), mention it

## Example Usage

**User says:**
> 这篇文章保存到飞书：https://mp.weixin.qq.com/s/xxxxx

**Skill executes:**
1. Detects WeChat Official Account article
2. Uses chrome-devtools-mcp to navigate and extract content
3. Extracts: title, keywords, summary (markdown), platform (公众号), author
4. Calls Feishu API to save record
5. Reports: "已保存到飞书多维表！标题：xxx，关键词：xxx，摘要：xxx"

## Troubleshooting

**Issue: UnicodeEncodeError on Windows (GBK encoding error)**
- This happens when using inline Python code with Chinese characters in print statements
- **Solution:** Always use the provided `scripts/save_to_feishu.py` script which handles UTF-8 encoding
- The script automatically detects Windows and reconfigures stdout/stderr to UTF-8

**Issue: WeChat article returns "Not accessible"**
- Some WeChat articles may be restricted or require login
- Inform user and ask for alternative access method

**Issue: Feishu API returns "field not found"**
- The field name in the API request doesn't match the actual Bitable field
- Check the actual Bitable schema if needed

**Issue: Author not found**
- Many articles don't have clear author information
- Leave author field empty if not found - this is acceptable

**Issue: Summary generation unclear**
- Use markdown format with clear structure
- Include key points and main takeaways
- Keep it concise but comprehensive
