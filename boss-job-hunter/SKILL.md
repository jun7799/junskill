---
name: boss-job-hunter
description: "Boss直聘职位搜索、智能匹配与本地管理。通过web-access直连Chrome搜索职位，根据简历匹配打分，批量提取JD详情页生成深度推荐报告。触发词：搜职位、找工作、Boss直聘、招聘搜索、职位匹配、投简历。"
version: 6.0.0
triggers: 搜职位、找工作、Boss直聘、招聘搜索、职位匹配、投简历、每日职位

# Boss直聘职位猎手

## 概述
一键式 Boss 直聘职位搜索 + 智能匹配 + 深度推荐报告生成。整个流程只需确认一次关键词和城市，之后全自动完成。

## 前置条件
1. **web-access skill 已安装**：通过 `ls ~/.claude/skills/web-access/SKILL.md` 确认存在
2. **CDP Proxy 运行中**：先执行前置检查确认连接正常
3. **用户 Chrome 已登录 Boss 直聘**：如果未登录，提示用户先登录

## 完整流程（一气呵成版）

> **核心原则**：整个流程只在开头确认一次参数，之后全自动跑完。中间不暂停、不反复确认。

### Phase 1: 启动（唯一的确认点）

1. 运行前置检查 + 提示自动化风险（一句话带过）：
```bash
node "${CLAUDE_SKILL_DIR}/scripts/check-deps.mjs"
```
> 温馨提示：Boss对自动化检测严格，存在封号风险。已内置防护但无法完全避免。

2. 问一次关键词和城市（用 AskUserQuestion，默认"AI产品经理"+ 广州深圳）

### Phase 2: 采集（全自动，不要暂停）

**重要：Boss 默认定位到用户所在城市（通常是惠州），必须第一时间切换到目标城市标签，不要在默认城市上浪费时间！**

```
打开搜索页 → 立刻点第一个目标城市标签(如广州) → 滚动 → 提取
→ 切换到第二个城市标签(如深圳) → 滚动 → 提取 → 关闭tab
```

具体步骤：

1. **打开搜索页**（用关键词构造URL）：
```bash
curl -s "http://localhost:3456/new?url=https://www.zhipin.com/web/geek/job?query={URL编码的关键词}&ka=header-jobs"
```

2. **立刻点击目标城市标签**（跳过默认城市！页面上有 `span.text-content` 城市标签）：
```bash
curl -s -X POST "http://localhost:3456/eval?target={TARGET_ID}" \
  -d "(() => { const spans = document.querySelectorAll('span.text-content'); for(const s of spans) { if(s.innerText.includes('{城市名}')) { s.click(); return 'clicked: ' + s.innerText; } } return 'not found'; })()"
```

3. **滚动加载**（每个城市都要滚动）：
```bash
sleep 3 && for i in 1 2 3 4 5; do curl -s "http://localhost:3456/scroll?target={TARGET_ID}&y=800&direction=down" > /dev/null; sleep 1; done
```

4. **提取职位数据**（JS 一把抓）：
```javascript
(() => {
  const cards = document.querySelectorAll('.job-card-box');
  const results = [];
  for(const card of cards) {
    const title = card.querySelector('.job-name')?.innerText?.trim() || '';
    const salary = card.querySelector('.job-salary')?.innerText?.trim() || '';
    const tags = Array.from(card.querySelectorAll('.tag-list li')).map(li => li.innerText.trim()).join('|');
    const company = card.querySelector('.company-name a, [class*=company-name] a')?.innerText?.trim()
                 || card.querySelector('.boss-name')?.innerText?.trim() || '';
    const url = card.querySelector('.job-name')?.href || '';
    let area = '';
    const areaEls = card.querySelectorAll('[class*=area], [class*=location]');
    for(const el of areaEls) { if(el.innerText.match(/[一-鿿]+/)) { area = el.innerText.trim(); break; } }
    results.push({title, salary, tags, company, url, area});
  }
  return JSON.stringify(results);
})()
```

5. **重复步骤 2-4** 对每个目标城市（切换标签 → 滚动 → 提取）

6. **关闭 tab**，将所有城市数据合并保存到 `D:/求职/raw-jobs.json`

### Phase 3: 一键流水线（全自动）

运行编排脚本，一条命令完成「去重打分 → 筛选高分 → 批量提取JD → 输出结果」：

```bash
node "${CLAUDE_SKILL_DIR}/scripts/run-full.mjs" "D:/求职/raw-jobs.json"
```

脚本自动执行：
1. **process-and-save**：去重 + 智能打分 + 本地存储 + 增量报告
2. **筛选4-5分职位**：自动从 jobs.md 中提取高分职位URL
3. **batch-extract-jd**：逐个打开详情页提取完整JD（实际薪资、岗位职责、任职要求）
4. **输出**：`D:/求职/jd-details.json` + 终端打印 TOP 5

删除临时文件：`rm "D:/求职/raw-jobs.json"`

### Phase 4: 生成推荐报告（Claude 执行）

读取 `D:/求职/jd-details.json`（JD详情）+ `D:/求职/简历版本/` 目录下的简历，按以下模板生成报告。

**报告保存到**：`D:/求职/Boss直聘推荐报告_{关键词}_{日期}.md`

**报告模板结构：**

```markdown
# Boss直聘职位推荐报告 vX
> 搜索关键词：「{关键词}」| 城市范围：{城市列表}
> 基于简历「{简历文件名}」+ {N}个职位详情页深度分析
> 生成时间：{日期}

## 你的核心匹配优势
（表格：你的优势 vs JD高频要求）

## TIER 1: 必须投（3-5个）
- 地点 + 薪资（以详情页实际薪资为准！搜索页薪资常虚高）
- 职位链接
- **为什么必须投**（逐条对标JD原文 vs 用户经验）
- **打招呼文案**（150字内，三点式结构）

## TIER 2: 强烈推荐（5-8个）
同TIER 1格式，含打招呼文案。

## TIER 3: 推荐投（5-8个）
简化：地点 + 薪资 + 链接 + 2-3句匹配分析。

## TIER 4: 可以试试
表格：职位 + 薪资 + 偏差原因。

## 投递建议（按波次）
## 本轮关键发现
```

**匹配维度参考：**

| 维度 | 用户优势 | JD高频关键词 |
|------|---------|-------------|
| 经验 | 10年B端 | "3-8年产品经验" |
| HR | HR SaaS考勤0-1 + 完整HR管理系统 | "HR系统/人事/薪酬/考勤" |
| AI | 独立开发6+个AI产品 | "AI产品落地/Agent/RAG/Prompt" |
| 技术 | 计算机科班 + Claude Code精通 | "技术背景优先" |
| 工具 | OpenClaw/Claude Code深度用户 | "Cursor/Claude Code/IDE工具" |
| 商业 | 5000万+营收 | "商业化/变现" |

**分级标准：**

| 等级 | 标准 |
|------|------|
| TIER 1 | 3个+核心维度匹配 + 薪资合理 + 方向高度对口 |
| TIER 2 | 2个核心维度匹配 + 方向相关 |
| TIER 3 | 1-2个维度匹配或有明显短板 |
| TIER 4 | 方向偏差或薪资偏低 |

**用户画像（写在skill里，不用每次翻memory）：**
- 10年B端产品经验（HR SaaS + 政务系统 + 运营商）
- AI原生能力：独立开发6+个AI产品（Agent直聘平台、拼好模、访谈式简历生成器等）
- Claude Code精通：分析过60万行源码，开发20+自定义Skills
- 商业化：5000万+销售额，DDoS防护年销3000万
- 计算机科班：广东金融学院，VibeCoding能力

### Phase 5: 输出结果

告知用户报告路径 + TIER 1 清单 + 关键发现。清理 `D:/求职/jd-details.json`。

---

## 快速指令（不搜新职位时用）

| 场景 | 命令 |
|------|------|
| 查看总职位摘要 | `node "${CLAUDE_SKILL_DIR}/scripts/process-and-save.mjs --summary"` |
| 更新职位状态 | `node "${CLAUDE_SKILL_DIR}/scripts/process-and-save.mjs --set-status "公司名" "已打招呼"` |
| 完整报告 | `node "${CLAUDE_SKILL_DIR}/scripts/process-and-save.mjs --full-report"` |
| 清理过期职位 | `node "${CLAUDE_SKILL_DIR}/scripts/process-and-save.mjs --clean"` |
| 批量提取JD | `node "${CLAUDE_SKILL_DIR}/scripts/batch-extract-jd.mjs urls.json output.json` |

---

## 本地数据结构

**数据目录：** `D:/求职/boss-jobs/`

| 文件 | 说明 |
|------|------|
| `jobs.md` | 总职位表（Markdown格式，唯一数据源） |
| `reports/YYYY-MM-DD.md` | 每次运行的增量报告 |

## 状态管理

| 状态 | 说明 |
|------|------|
| 新发现 | 默认状态，刚抓取到的职位 |
| 已打招呼 | 用户已在 Boss 上发送打招呼消息 |
| 已投递 | 用户已正式投递简历 |
| 面试中 | 正在面试流程中 |
| 已拒绝 | 用户主动放弃该职位 |
| 不合适 | 被公司拒绝或不匹配 |

## Boss 直聘页面选择器参考

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 职位卡片 | `.job-card-box` | 每个职位一个卡片 |
| 职位名称 | `.job-name` | 包含链接，href 为职位详情 URL |
| 薪资 | `.job-salary` | 如 "30-50K" |
| 标签列表 | `.tag-list li` | 经验\|学历\|其他标签 |
| 公司名称 | `.company-name a` 或 `.boss-name` | 优先用 company-name |
| 地区 | `[class*=area]` 或 `[class*=location]` | 提取时用正则匹配中文 |
| 城市标签 | `span.text-content` | 顶部城市切换标签 |
| JD详情 | `.job-sec-text` | 职位详情页的完整JD文本 |
| JD薪资 | `.job-banner .salary` | 详情页实际薪资（可能比搜索页低） |

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| CDP未连接 | 运行 `check-deps.mjs`，检查 Chrome 远程调试 |
| Boss未登录 | 提示用户登录 zhipin.com，刷新即可 |
| 没有目标城市标签 | 回退方案：用搜索框输入关键词+城市 |
| 职位数量不够 | 增加滚动次数或切换下一页 |
| 薪资虚高 | **始终以详情页薪资为准**，搜索页仅参考 |

---

## 每日自动采集（已配置）

**Windows 计划任务 `BossJobHunter-Daily`**，每天 07:57 自动运行。

**前提条件**（必须满足，否则脚本会静默退出）：
1. 电脑处于开机状态（不休眠）
2. Chrome 已打开且登录了 Boss 直聘
3. CDP Proxy 正在运行（Chrome 远程调试端口已开启）

**自动完成**：
- 打开搜索页 → 切换广州/深圳 → 滚动提取 → 去重打分 → 筛选高分 → 批量提取JD
- 日志文件：`D:/求职/boss-jobs/auto-daily.log`
- JD详情输出：`D:/求职/jd-details.json`

**你需要做的**：
早上打开 Claude Code，说「生成今天的推荐报告」即可。数据已经采集好了。

**手动触发**：
```bash
node "${CLAUDE_SKILL_DIR}/scripts/auto-daily.mjs" [关键词]
```

**修改计划任务**：
```bash
# 查看状态
schtasks /query /tn BossJobHunter-Daily

# 删除任务
schtasks /delete /tn BossJobHunter-Daily /f

# 重新创建（改时间）
schtasks /create /tn BossJobHunter-Daily /tr C:\Users\44162\.claude\skills\boss-job-hunter\scripts\auto-daily.bat /sc daily /st 08:00 /f
```

---
_Last updated: 2026-05-11 (v6.0 一气呵成版)_
