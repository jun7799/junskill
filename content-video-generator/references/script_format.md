# 脚本格式说明

本文档说明 `book-video-generator` skill 使用的脚本数据格式。

## 片段 (Segment) 数据结构

每个视频片段包含以下字段：

```json
{
  "id": 1,
  "title": "开篇悬念",
  "audio_text": "配音文本内容",
  "key_points": [
    {"text": "关键点文字", "icon": "arrow_up"}
  ],
  "image_prompt": "背景图片提示词",
  "duration": 18.5
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | int | 是 | 片段序号（从1开始） |
| `title` | string | 是 | 片段标题（用于管理） |
| `audio_text` | string | 是 | 配音文本（Edge-TTS朗读） |
| `key_points` | array | 是 | 关键点数组（动画用） |
| `image_prompt` | string | 是 | 背景图提示词（ModelScope生成） |
| `duration` | float | 否 | 片段时长（秒，可省略自动计算） |

## 关键点 (KeyPoint) 数据结构

```json
{
  "text": "刘备 75000",
  "icon": "arrow_up"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 显示的文字 |
| `icon` | string | 是 | 图标名称（见图标库） |

## 完整脚本示例

```json
[
  {
    "id": 1,
    "title": "开篇悬念",
    "audio_text": "公元222年，三国版'以少胜多'神剧本来了！刘备带着七万五千大军，气势汹汹要灭东吴。",
    "key_points": [
      {"text": "公元222年", "icon": "none"},
      {"text": "刘备 75000", "icon": "arrow_up"},
      {"text": "灭东吴?", "icon": "question"}
    ],
    "image_prompt": "Ancient Chinese battlefield, Three Kingdoms period, ink wash painting style, dark atmosphere",
    "duration": 15.0
  },
  {
    "id": 2,
    "title": "结果揭示",
    "audio_text": "结局啥样？陆逊一把火，把刘备的四十多座营寨烧了个精光！",
    "key_points": [
      {"text": "一把火", "icon": "fire"},
      {"text": "40+ 营寨 烧光", "icon": "camp_burn"},
      {"text": "75000 -> 团灭", "icon": "numbers_cross"}
    ],
    "image_prompt": "Ancient Chinese military camp aftermath, burned camps, dark smoke",
    "duration": 12.0
  }
]
```

## 脚本编写指南

### 1. 片段时长控制

建议每个片段 15-25 秒：
- 太短：信息不足，画面切换频繁
- 太长：观众疲劳，容易走神

### 2. 关键点数量

建议每个片段 3-6 个关键点：
- 1-2个：画面太单调
- 7+个：每个点展示时间太短

### 3. 配音文本风格

- **口语化**: "是个大坑" 比 "存在重大风险" 更自然
- **有节奏**: 短句为主，配合停顿
- **带情绪**: "!" "?" 表示强调/悬念

### 4. 图标选择

- **动词**选动态图标：`arrow_path`, `flow`, `fire`
- **对比**选天平：`balance_left`, `balance_right`
- **强调**选醒目：`star`, `target`, `exclamation`
- **无动作**选简单：`none`, `scroll`

### 5. 图片提示词

- 风格统一：`ink wash painting style`, `illustration style`
- 尺寸固定：`1280x720`
- 避免具体人物：用场景代替

## Python 数据类

如果使用 Python 代码生成脚本：

```python
from dataclasses import dataclass
from typing import List

@dataclass
class KeyPoint:
    text: str
    icon: str = "none"

@dataclass
class Segment:
    id: int
    title: str
    audio_text: str
    key_points: List[KeyPoint]
    image_prompt: str
    duration: float = 15.0

# 使用示例
segment = Segment(
    id=1,
    title="开篇",
    audio_text="公元222年，三国版神剧本来了！",
    key_points=[
        KeyPoint(text="刘备 75000", icon="arrow_up"),
        KeyPoint(text="火攻", icon="fire"),
    ],
    image_prompt="Ancient battlefield, ink style"
)
```
