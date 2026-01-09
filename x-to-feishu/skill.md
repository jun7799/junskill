# X to Feishu

**从X(Twitter)采集推文并上传到飞书多维表**

## 功能描述

这个skill用于**从Feed流**采集符合特定关键词条件的推文，并通过AI生成推文主题、关键词、梗概后，上传到飞书多维表格。

**数据来源**：用户的个人Feed流（Home时间线）

支持功能：
1. **Feed流采集** - 从个人主页时间线滚动采集推文
2. **关键词过滤** - 根据主题关键词筛选推文
3. **时间筛选** - 只采集指定天数内的推文
4. **热度筛选** - 按观看数/互动数筛选
5. **AI总结** - 自动生成推文主题、提取关键词、生成梗概
6. **飞书上传** - 直接上传到飞书多维表
7. **安全增强** - 随机延迟、保守策略降低封号风险

## 使用方法

### 准备工作

1. **准备关键词文件**：在 config.json 中配置主题关键词
2. **获取Cookie**：在X网站登录后，从浏览器开发者工具中复制Cookie字符串
3. **配置飞书**：config.json 中已配置好飞书多维表信息

### 执行步骤

当用户请求采集推文时，按以下步骤执行：

#### 1. 读取Cookie和配置

首先尝试从 `cookie.txt` 文件读取Cookie：

```javascript
// 读取cookie文件
const cookiePath = '.claude/skills/x-to-feishu/cookie.txt';
let cookieContent = '';

try {
  cookieContent = await Read(cookiePath);
  // 提取非注释行的cookie内容
  const cookieLines = cookieContent
    .split('\n')
    .filter(line => line.trim() && !line.trim().startsWith('#'));

  if (cookieLines.length === 0) {
    throw new Error('Cookie文件为空，请配置cookie.txt');
  }

  cookieContent = cookieLines.join('; ');
} catch (error) {
  告知用户："未找到有效的Cookie配置，请按以下步骤配置：
  1. 在浏览器登录 https://x.com
  2. 按F12打开开发者工具，在Console输入: copy(document.cookie)
  3. 将复制的内容粘贴到 .claude/skills/x-tweet-feed/cookie.txt 文件中"

  return;
}

// 读取config.json获取默认配置
const configPath = '.claude/skills/x-to-feishu/config.json';
const configContent = await Read(configPath);
const config = JSON.parse(configContent);

// 默认配置
const defaultCount = config.collection.default_count || 10;
const defaultDaysAgo = config.collection.default_days_ago || 3;
const defaultMinViews = config.collection.default_min_views || 100;
const defaultTheme = 'AI'; // 默认AI主题
```

然后询问用户参数：

- **主题名称**（可选）：要采集的主题，默认"AI"（对应config.json中的themes）
- **推文数量**（可选）：需要采集多少条推文，默认10条
- **时间范围**（可选）：采集多少天内的推文，默认3天
- **最小观看数**（可选）：推文的最小观看数阈值，默认100

#### 2. 获取主题关键词

从 config.json 中读取主题对应的关键词列表：

```javascript
// 根据用户选择的主题获取关键词
const theme = userTheme || defaultTheme;
const keywords = config.themes[theme]?.keywords || [];

if (keywords.length === 0) {
  告知用户：`主题"${theme}"未找到关键词配置，请检查config.json`;
  return;
}

console.log(`使用主题: ${theme}，关键词数量: ${keywords.length}`);
```

#### 3. 打开X网站并设置Cookie

使用Chrome DevTools MCP工具：

```javascript
// 3.1 打开新页面 - 访问X首页（Feed流）
mcp__chrome-devtools__new_page({
  url: "https://x.com",
  timeout: 30000
})

// 3.2 设置Cookie
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const cookieStr = '${cookieContent}';
    const cookies = cookieStr.split('; ');
    cookies.forEach(cookie => {
      const [name, ...valueParts] = cookie.split('=');
      const value = valueParts.join('=');
      document.cookie = \`\${name}=\${value}; domain=.x.com; path=/\`;
    });
    return 'Cookies set successfully';
  }`
})

// 3.3 刷新页面使Cookie生效
mcp__chrome-devtools__navigate_page({
  type: "reload",
  timeout: 30000
})
```

#### 4. 采集推文数据

使用 `evaluate_script` 执行采集脚本，**使用随机延迟和保守策略**：

```javascript
mcp__chrome-devtools__evaluate_script({
  function: `async () => {
    // 关键词列表
    const keywords = ${JSON.stringify(keywords)};
    const theme = '${theme}';

    // 配置参数（保守策略）
    const targetCount = ${tweetCount || defaultCount};
    const daysAgo = ${daysAgo || defaultDaysAgo};
    const minViews = ${minViews || defaultMinViews};

    // 随机延迟配置（增加随机性，降低被封风险）
    const minDelay = 2000;
    const maxDelay = 5000;

    function getRandomDelay() {
      return minDelay + Math.random() * (maxDelay - minDelay);
    }

    const tweets = [];
    const seenTweetIds = new Set();
    const timeThreshold = Date.now() - (daysAgo * 24 * 60 * 60 * 1000);

    // 辅助函数：解析时间
    function parseTime(timeStr) {
      const now = Date.now();
      if (timeStr.includes('小时') || timeStr.includes('hour')) {
        const hours = parseInt(timeStr);
        return now - (hours * 60 * 60 * 1000);
      } else if (timeStr.includes('分钟') || timeStr.includes('minute') || timeStr.includes('min')) {
        const mins = parseInt(timeStr);
        return now - (mins * 60 * 1000);
      } else if (timeStr.includes('秒') || timeStr.includes('second') || timeStr.includes('sec')) {
        const secs = parseInt(timeStr);
        return now - (secs * 1000);
      }
      return now;
    }

    // 辅助函数：解析观看数
    function parseViews(viewStr) {
      if (!viewStr) return 0;
      viewStr = viewStr.replace(/,/g, '').replace(/\\s/g, '');

      if (viewStr.includes('万')) {
        return parseFloat(viewStr) * 10000;
      }
      if (viewStr.includes('K')) {
        return parseFloat(viewStr) * 1000;
      }
      if (viewStr.includes('M')) {
        return parseFloat(viewStr) * 1000000;
      }
      return parseInt(viewStr) || 0;
    }

    // 辅助函数：检查是否包含关键词
    function hasKeyword(text) {
      const lowerText = text.toLowerCase();
      return keywords.some(kw => lowerText.includes(kw));
    }

    // 收集推文的函数
    function collectTweets() {
      const articles = document.querySelectorAll('article[data-testid="tweet"]');
      let newCount = 0;

      articles.forEach(article => {
        try {
          const timeLink = article.querySelector('time')?.parentElement;
          if (!timeLink) return;

          const tweetUrl = timeLink.href;
          const tweetId = tweetUrl.split('/status/')[1]?.split('?')[0];
          if (!tweetId || seenTweetIds.has(tweetId)) return;

          const textElement = article.querySelector('[data-testid="tweetText"]');
          const tweetText = textElement?.innerText || '';

          // 检查是否包含关键词
          if (!hasKeyword(tweetText)) return;

          const timeElement = article.querySelector('time');
          const timeStr = timeElement?.parentElement?.innerText || '';
          const tweetTime = parseTime(timeStr);

          if (tweetTime < timeThreshold) return;

          const viewsElement = article.querySelector('[href*="/analytics"]');
          const viewsText = viewsElement?.innerText || '0';
          const views = parseViews(viewsText);

          if (views < minViews) return;

          const userLink = article.querySelector('[data-testid="User-Name"] a');
          const username = userLink?.href.split('/').pop() || '';
          const displayName = userLink?.innerText || username;

          const replyElement = article.querySelector('[data-testid="reply"]');
          const replies = parseInt(replyElement?.getAttribute('aria-label')?.match(/\\d+/)?.[0] || '0');

          const retweetElement = article.querySelector('[data-testid="retweet"]');
          const retweets = parseInt(retweetElement?.getAttribute('aria-label')?.match(/\\d+/)?.[0] || '0');

          const likeElement = article.querySelector('[data-testid="like"]');
          const likes = parseInt(likeElement?.getAttribute('aria-label')?.match(/\\d+/)?.[0] || '0');

          seenTweetIds.add(tweetId);
          tweets.push({
            id: tweetId,
            url: tweetUrl,
            text: tweetText,
            username: username,
            displayName: displayName,
            timeStr: timeStr,
            tweetTime: tweetTime,
            views: views,
            replies: replies,
            retweets: retweets,
            likes: likes,
            theme: theme  // 添加主题标识
          });
          newCount++;

        } catch (e) {
          console.error('Error processing tweet:', e);
        }
      });

      return newCount;
    }

    // 初始收集
    collectTweets();

    // 滚动并收集更多推文（保守策略）
    let scrollAttempts = 0;
    const maxScrolls = 20; // 降低滚动次数
    let noNewTweetsCount = 0;

    while (tweets.length < targetCount && scrollAttempts < maxScrolls) {
      // 使用随机延迟滚动
      const delay = getRandomDelay();
      console.log(\`滚动 \${scrollAttempts + 1}/\${maxScrolls}，等待 \${Math.round(delay)}ms...\`);

      window.scrollTo(0, document.body.scrollHeight);

      // 随机等待时间
      await new Promise(resolve => setTimeout(resolve, delay));

      const newTweets = collectTweets();
      scrollAttempts++;

      // 如果连续3次滚动都没有新推文，停止采集
      if (newTweets === 0) {
        noNewTweetsCount++;
        if (noNewTweetsCount >= 3) {
          console.log('连续3次无新推文，停止采集');
          break;
        }
      } else {
        noNewTweetsCount = 0;
      }
    }

    // 按时间排序（最新的在前）
    tweets.sort((a, b) => b.tweetTime - a.tweetTime);

    return {
      collected: tweets.length,
      tweets: tweets.slice(0, targetCount),
      config: {
        theme: theme,
        keywords: keywords.length,
        targetCount: targetCount,
        daysAgo: daysAgo,
        minViews: minViews
      }
    };
  }`
})
```

#### 5. 调用AI生成推文总结

对于每条推文，调用AI API生成主题、关键词和梗概：

```javascript
// 采集完成后，为每条推文调用AI总结
const tweetsWithSummary = [];

for (const tweet of tweets) {
  // 调用Claude API生成总结
  const summaryPrompt = \`
请为以下推文生成简短总结，以JSON格式返回：

推文内容：\${tweet.text}
作者：@\${tweet.username}

请生成：
1. 推文主题：一句话概括这条推文的核心主题（不超过20字）
2. 关键词：提取3个最相关的关键词，用逗号分隔
3. 推文梗概：用50-100字总结推文内容

返回JSON格式：
{
  "theme": "推文主题",
  "keywords": "关键词1,关键词2,关键词3",
  "summary": "推文梗概"
}
\`;

  // 调用Claude API
  const aiResponse = await callClaudeAPI(summaryPrompt);
  const aiResult = JSON.parse(aiResponse);

  tweetsWithSummary.push({
    ...tweet,
    aiTheme: aiResult.theme,
    aiKeywords: aiResult.keywords,
    aiSummary: aiResult.summary
  });

  // 调用间隔，避免API限流
  await new Promise(resolve => setTimeout(resolve, 1000));
}
```

#### 6. 上传到飞书多维表

保存JSON并调用飞书上传脚本：

```javascript
// 保存JSON
const jsonPath = '.claude/skills/x-to-feishu/temp_tweets.json';
const jsonData = JSON.stringify(
  {
    collected: tweetsWithSummary.length,
    tweets: tweetsWithSummary,
    config: {
      theme: theme,
      targetCount: targetCount,
      daysAgo: daysAgo,
      minViews: minViews
    }
  },
  null,
  2
);

await Write(jsonPath, jsonData);
```

```bash
# 调用飞书上传脚本
cd .claude/skills/x-to-feishu
python3 feishu_uploader.py temp_tweets.json
```

#### 7. 返回结果

告知用户：
- 成功采集的推文数量
- 使用的主题和关键词
- 飞书上传结果
- 安全提示

## 安全策略（防封号）

### 1️⃣ **随机延迟机制**
- 每次滚动延迟随机（2-5秒）
- 避免固定的行为模式

### 2️⃣ **保守策略**
- 默认只采集10条（不是20条）
- 最多滚动20次（不是50次）
- 连续3次无新内容立即停止

### 3️⃣ **Feed流模式优势**
- 模拟真实用户浏览首页的行为
- 看到的是关注账号的内容，质量更高
- 比搜索更不容易被检测为爬虫

### 4️⃣ **使用建议**
- 每天使用不超过2-3次
- 每次间隔至少1小时
- 建议使用测试账号
- 避免在短时间内重复采集同一主题

## 文件说明

- `skill.md` - 本说明文档（Skill定义文件）
- `README.md` - 用户友好的使用文档
- `config.json` - 配置文件（飞书配置、主题关键词等）
- `feishu_uploader.py` - 飞书上传脚本
- `cookie.txt` - Cookie配置文件

## 配置选项

### config.json 结构

```json
{
  "feishu": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret",
    "base_id": "your_base_id",
    "table_id": "your_table_id"
  },
  "collection": {
    "default_count": 10,
    "default_days_ago": 3,
    "default_min_views": 100,
    "scroll_delay_min": 2000,
    "scroll_delay_max": 5000,
    "max_scrolls": 20
  },
  "themes": {
    "AI": {
      "keywords": ["gpt", "claude", "ai", "llm", ...],
      "description": "AI人工智能相关"
    }
  }
}
```

## 使用限制

1. **需要登录** - 必须提供有效的Cookie
2. **网络稳定** - 需要稳定的网络连接
3. **AI API** - 需要配置Claude API密钥（用于生成总结）
4. **飞书配置** - 需要正确配置飞书多维表信息

## 注意事项

1. **Cookie安全** - Cookie包含敏感信息，不要泄露给他人
2. **Cookie有效期** - Cookie可能过期，需要重新获取
3. **采集频率** - 严格控制采集频率，避免被封号
4. **使用测试账号** - 强烈建议使用测试账号而非主账号
5. **AI成本** - 每条推文都会调用AI API，产生API费用

## 更新记录

- 2025-11-07：创建skill
- 2025-01-04：重大更新
  - Feed流采集模式
  - 添加AI总结功能
  - 改为飞书多维表上传（原HTML报告）
  - 加强反封号安全机制
