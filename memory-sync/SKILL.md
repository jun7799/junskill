---
name: memory-sync
description: "从Claude Code历史会话中提炼用户信息并更新记忆系统。当用户说'更新记忆'、'同步记忆'、'提炼记忆'、'刷新记忆'、'同步一下记忆'、'memory sync'时使用。支持增量更新（默认）和全量刷新（用户说'全量'时）。"
license: MIT
---

# Memory Sync Skill

从历史会话中提炼用户信息，增量合并到记忆系统。

## 工作流决策树

### 场景1：增量更新（默认）

用户说"更新记忆"、"同步记忆"、"同步一下记忆"等，但没说"全量"。

### 场景2：全量刷新

用户说"全量更新记忆"、"全量刷新记忆"等包含"全量"关键词。

### 场景3：首次运行

memory 目录为空或没有 .meta.json 文件。

## 工作流步骤

### 步骤0：定位 memory 目录

1. 确定当前项目的 memory 目录路径：
   - 查找 `~/.claude/projects/` 下与当前工作目录匹配的项目哈希目录
   - 项目哈希目录内应有 `sessions-index.json` 文件来确认匹配
   - memory 目录路径为：`~/.claude/projects/<project-hash>/memory/`
2. 如果找不到匹配的项目目录，提示用户在 Claude Code 已打开过的项目目录中运行

### 步骤1：读取同步状态

1. 读取 `memory/.meta.json`
2. 如果文件存在 → 增量模式，记录 `last_sync` 时间戳
3. 如果文件不存在 → 首次运行模式（等同全量）
4. 如果用户明确要求"全量" → 忽略 last_sync，全量模式

### 步骤2：扫描会话索引

1. 搜索 `~/.claude/projects/*/sessions-index.json`，找到所有项目的会话索引
2. 解析每个 sessions-index.json，提取所有 entries
3. **增量模式**：只保留 `fileMtime > last_sync` 的会话
4. **全量模式**：保留所有会话
5. 按 messageCount 从大到小排序

### 步骤3：读取会话内容

根据信息量分层读取：

| messageCount | 策略 |
|---|---|
| < 10 | 只用 sessions-index.json 中的 firstPrompt 和 summary，不读 .jsonl |
| 10-50 | 读 .jsonl 文件的前100行 + 后100行 |
| > 50 | 读 .jsonl 文件的前200行 + 后200行 |

注意：.jsonl 文件路径在 sessions-index.json 的 `fullPath` 字段中。

### 步骤4：提炼用户信息

从会话内容中提取信息，分类到 6 个维度。**必读**：[`dimensions.md`](references/dimensions.md) 查看完整维度定义。

关键原则：
- 只提炼**关于用户的信息**，不提炼技术内容本身
- 从用户的提问、请求、决策中推断偏好和习惯
- 关注用户明确表达的信息，也关注隐含的信息（如工具选择、工作时段）
- 不要编造，只记录会话中明确提到或能可靠推断的内容

### 步骤5：合并到记忆文件

**增量模式** — 合并到现有文件：

1. 读取现有记忆文件
2. 对每个维度的发现，执行合并：
   - **新信息**（文件中没有的）→ 追加到对应章节末尾
   - **更新的信息**（已有但更精确了）→ 替换旧描述
   - **矛盾的信息** → 保留新的，旧标注为"（已被更新于 YYYY-MM-DD）"
   - **确认的信息**（与已有信息一致）→ 不动，跳过
3. 如果发现新类别信息（6个维度无法归类）→ 创建新记忆文件
4. 更新 MEMORY.md 索引（如有新增文件）

**全量模式** — 重新生成：

1. 重新生成全部 6 个记忆文件
2. 重新生成 MEMORY.md 索引

### 步骤6：更新同步状态

写入 `memory/.meta.json`：

```json
{
  "last_sync": <当前毫秒时间戳>,
  "last_sync_date": "YYYY-MM-DD",
  "sync_count": <累加>,
  "total_sessions_processed": <累加>,
  "mode": "incremental|full",
  "files_updated": ["user_profile.md", ...]
}
```

### 步骤7：输出摘要

```
[Memory Sync 完成]
模式: 增量/全量/首次
扫描新会话: X 个
读取会话内容: Y 个
更新记忆文件: Z 个
新增记忆文件: N 个
新发现:
- (列出关键新信息，每条一行)
下次同步将从 YYYY-MM-DD 开始
```

## 注意事项

- .jsonl 文件是 JSON Lines 格式，每行一个 JSON 对象，包含 role、content 等字段
- 读取 .jsonl 时关注 role 为 "human" 或 "user" 的消息，这些是用户的真实输入
- 大文件不要全量读取，按分层策略只读头部和尾部
- 记忆文件的 frontmatter 格式必须保持一致（name, description, type 三个字段）
- MEMORY.md 是索引文件，每条记录一行，格式：`- [标题](文件名.md) — 一句话描述`
- 同步过程中不要删除任何现有记忆，只做追加和更新
