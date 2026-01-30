---
name: content-video-generator
description: 自动从任何内容生成解读视频。当用户要求"把XXX做成视频"、"生成XXX的科普视频"、"解读XXX内容"时使用。支持书籍、文章、论文、概念等任何内容，自动归纳精华并生成视频（配音+插图+动画+字幕+BGM）。
---

# 内容解读视频生成器

自动从任何内容（书籍、文章、论文、概念等）生成解读视频。该技能归纳内容精华，用科普风格让观众快速理解内容核心。

## 何时使用此技能

当用户出现以下请求时触发：
- "把XXX做成视频"、"生成XXX的科普视频"
- "解读XXX"、"解释XXX概念"
- "XXX视频制作"、"XXX内容讲解"

## 工作流程

```
用户输入（任何内容）
    ↓
1. 内容分析 → 提取核心精华
2. 脚本生成 → 选择风格 + 分段
3. 素材生成 → 配音 + 插图 + 动画
4. 视频合成 → FFmpeg 合并（优化版）
5. 字幕生成 → Whisper语音识别
6. 字幕修正 → 人工检查专业术语（重要！）
7. 字幕烧录 → 烧录修正后的字幕
8. BGM添加 → 自动选择并添加
9. 预览验证 → 自动生成预览帧
    ↓
完整解读视频（含正确字幕+BGM）
```

## 风格选择

生成视频前，必须确认或询问用户选择**脚本风格**：

### 风格 A：小编风格（默认）
- 口语化、网感强
- "小编"、"哈哈"、"滴啦"
- 技术江湖人说江湖话
- 短句节奏、自嘲幽默
- 适合：轻松科普、技术解读
- **推荐BGM分类**：`calm`（平静）、`upbeat`（轻快）

### 风格 B：Dan Koe 风格
- 对话式挑衅、挑战观念
- 深度思考 + 实践步骤
- 诊断问题→揭示原因→解决方案
- 口语化与学术性混合
- 适合：深度观点、思维模型、成长话题
- **推荐BGM分类**：`inspirational`（励志）

**询问方式**：
```
"选择脚本风格：
A. 小编风格（口语化、轻松）
B. Dan Koe风格（深度、挑衅）"
```

## 捆绑脚本

### `scripts/fetch_content.py` ⭐新增
网页内容抓取（支持MCP + Playwright双模式）

```bash
python scripts/fetch_content.py <url> [output.json]
```

**特性**：
- 优先使用MCP webReader
- MCP不可用时自动切换Playwright
- 支持微信公众号、网页文章等

### `scripts/generate_audio.py`
生成中文配音

```bash
python scripts/generate_audio.py "配音文本" output/segment1.mp3
```

音色：zh-CN-YunyangNeural（男声沉稳）

### `scripts/generate_image.py`
生成背景插图

```bash
python scripts/generate_image.py "prompt" output/seg1_bg.png
```

### `scripts/render_scene.py`
渲染动画场景

```bash
python scripts/render_scene.py segment_data.json output/seg1.mp4
```

### `scripts/generate_subtitle.py`
基于脚本生成字幕（SRT格式）- Fallback方案

```bash
python scripts/generate_subtitle.py <script.json> <audio_dir> <output.srt>
```

**特性**：
- 根据脚本和音频时长自动生成时间轴
- 支持中文分词和换行
- 输出标准SRT格式

### `scripts/generate_subtitle_whisper.py` ⭐推荐
Whisper语音识别生成字幕（更准确）

```bash
python scripts/generate_subtitle_whisper.py <video.mp4> <output.srt> [model_size]
```

**特性**：
- 使用OpenAI Whisper语音识别
- 基于实际音频生成时间轴（更准确）
- 支持多种模型大小（tiny/base/small/medium/large）
- **注意**：技术术语需要人工修正

### `scripts/burn_subtitle.py` ⭐新增
烧录字幕到视频（硬字幕）

```bash
python scripts/burn_subtitle.py <video.mp4> <subtitle.srt> <output.mp4>
```

**特性**：
- 支持中文显示
- 自动转换为ASS格式
- 可自定义字体大小和颜色

### `scripts/add_bgm.py` ⭐新增
添加背景音乐

```bash
python scripts/add_bgm.py <video.mp4> <bgm_dir> <output.mp4> [category] [volume]
```

**特性**：
- 自动从BGM库选择音乐
- 根据风格分类选择
- 自动降低音量（默认20%）
- 淡入淡出效果

**BGM分类**：
- `inspirational`：励志、成长、Dan Koe风格
- `calm`：平静、科普、小编风格
- `upbeat`：轻快、活泼
- `tech`：科技感、电子

### `scripts/compose_video.py` ⭐优化版（集成字幕+BGM）
智能视频合成（一键完成所有流程）

```bash
python scripts/compose_video.py <script.json> <bg_dir> <scene_dir> <audio_dir> <output_dir> [options]
```

**特性**：
- ✅ 自动去除Manim视频的黑色背景（colorkey）
- ✅ 背景图保持比例，自动裁剪填充（无变形）
- ✅ 可选背景虚化效果（gblur）
- ✅ 自动生成并烧录字幕
- ✅ 自动添加背景音乐
- ✅ Windows路径兼容性处理

**参数说明**：
- `--blur N`：虚化强度（默认12，0=不虚化）
- `--bgm DIR`：BGM目录
- `--bgm-cat CAT`：BGM分类（inspirational/calm/upbeat/tech）
- `--bgm-vol N`：BGM音量0.0-1.0（默认0.20）
- `--no-subtitle`：不烧录字幕

### `scripts/generate_preview.py` ⭐新增
自动生成预览帧

```bash
python scripts/generate_preview.py <video_path> <output_dir> [count]
```

**特性**：
- 自动提取视频关键帧
- 用于快速验证视频质量
- 检查背景、文字、比例是否正确

### `scripts/merge_video.py`
基础音视频合并（已保留）

```bash
python scripts/merge_video.py video.mp4 audio.mp3 output.mp4
```

## 背景音乐库

### 目录结构
```
bgm/
├── inspirational/    # 励志、成长、Dan Koe风格
├── calm/            # 平静、科普、小编风格
├── upbeat/          # 轻快、活泼
└── tech/            # 科技感、电子
```

### 添加音乐
将无版权/免版税的背景音乐放入对应分类目录。

**推荐来源**：
- YouTube Audio Library（免费）
- Pixabay Music（免费）
- Bensound（免费，需署名）
- Kevin MacLeod（免费）

**命名建议**：
- `风格_描述.mp3`
- 例如：`inspirational/uplifting_piano.mp3`

## 图标库

24个内置图标：`none`, `arrow_up`, `arrow_down`, `question`, `fire`, `camp_burn`, `numbers_cross`, `scroll`, `balance_left`, `balance_right`, `wave`, `eye`, `shield`, `arrow_path`, `flow`, `map_arrow`, `retreat_arrow`, `chain`, `pause`, `sun`, `steps`, `building`, `target`, `star`

添加自定义图标见 `references/icons.md`

## 脚本格式

```json
{
  "id": 1,
  "title": "片段标题",
  "audio_text": "配音文本",
  "key_points": [
    {"text": "要点1", "icon": "arrow_up"}
  ],
  "image_prompt": "背景图提示词",
  "duration": 15.0
}
```

## 风格化脚本生成指南

### 小编风格示例

```json
{
  "audio_text": "这玩意儿绝了！AI能自动生成视频，你敢信？小编今天就带你见识见识，说干就干滴啦！",
  "key_points": [
    {"text": "AI生成视频", "icon": "star"},
    {"text": "说干就干", "icon": "arrow_path"}
  ]
}
```

### Dan Koe 风格示例

```json
{
  "audio_text": "你可能听过AI生成视频，但真正理解它的人不到1%。这不是技术问题，而是思维问题。让我告诉你为什么。",
  "key_points": [
    {"text": "<1% 真正理解", "icon": "question"},
    {"text": "不是技术问题", "icon": "numbers_cross"},
    {"text": "是思维问题", "icon": "target"}
  ]
}
```

## 完整生成流程（推荐使用优化版）

```bash
# 1. 抓取内容（可选，MCP不可用时使用）
python scripts/fetch_content.py "https://mp.weixin.qq.com/s/xxx" article.json

# 2. 生成配音
python scripts/generate_audio.py "文本" output/seg1.mp3

# 3. 生成插图
python scripts/generate_image.py "prompt" output/seg1_bg.png

# 4. 渲染场景
python scripts/render_scene.py seg1.json output/seg1.mp4

# 5. 一键合成（含字幕+BGM）
python scripts/compose_video.py video_script.json output/images output/scenes output/audio output/final --blur 12 --bgm ../bgm --bgm-cat inspirational

# 6. 生成预览验证
python scripts/generate_preview.py output/final/final_video_complete.mp4 output/previews 5
```

## 优化功能详解

### 1. 网页抓取备用方案
当MCP工具因余额或其他原因不可用时，自动切换到Playwright本地抓取：
```python
result = await fetch_content(url, output_path)
```

### 2. 视频合成优化
**问题**：Manim渲染的视频是不透明黑色背景，直接overlay会完全遮挡背景图

**解决**：使用colorkey滤镜去除黑色背景
```bash
[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(iw-ow)/2:(ih-oh)/2,gblur=sigma=12[bg];
[1:v]colorkey=black:0.1:0.5[fg];
[bg][fg]overlay=(W-w)/2:(H-h)/2[video]
```

### 3. 背景图比例处理
**问题**：竖版图片强制缩放到横版会变形

**解决**：保持比例+居中裁剪
```
scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(iw-ow)/2:(ih-oh)/2
```

### 4. 背景虚化可选
用户可选择虚化强度，让文字更突出：
- `blur_sigma=0`：不虚化
- `blur_sigma=8-15`：推荐范围
- `blur_sigma=20+`：强虚化

### 5. 自动字幕生成
根据脚本文本和音频时长自动生成SRT字幕，并烧录到视频中。

### 6. 自动BGM添加
- 根据视频风格自动选择BGM分类
- 自动降低音量到20%（不影响解说）
- 添加淡入淡出效果

### 7. Windows路径兼容
自动处理中文路径编码问题，在目标目录内创建list文件

### 8. 自动预览生成
合成后自动提取关键帧，快速验证效果

### 9. 简版视频生成流程 ⭐推荐（静态图+音频+字幕）
适用于科普短视频、解说视频等，无需复杂动画：

**工作流程**：
```bash
# 1. 生成所有音频段（串行，并行不稳定）
edge-tts --voice zh-CN-YunyangNeural --text "文本1" --write-media seg1.mp3
edge-tts --voice zh-CN-YunyangNeural --text "文本2" --write-media seg2.mp3
...

# 2. 生成所有背景图（串行，API队列限制）
python scripts/generate_image.py "prompt1" seg1_bg.png
python scripts/generate_image.py "prompt2" seg2_bg.png
...

# 3. 合并音频
echo "file 'seg1.mp3'" > audio_list.txt
echo "file 'seg2.mp3'" >> audio_list.txt
ffmpeg -f concat -safe 0 -i audio_list.txt -c copy audio.mp3

# 4. 获取每段音频时长
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 seg1.mp3

# 5. 创建视频段（图片+音频）
ffmpeg -loop 1 -i seg1_bg.png -i seg1.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -t [时长] seg1_video.mp4

# 6. 合并所有视频
echo "file 'seg1_video.mp4'" > video_list.txt
echo "file 'seg2_video.mp4'" >> video_list.txt
ffmpeg -f concat -safe 0 -i video_list.txt -c copy video.mp4

# 7. Whisper生成字幕（small模型更快）
whisper audio.mp3 --model small --language zh --output_format srt --task transcribe

# 8. 手动修正字幕错误（重要！）

# 9. 烧录字幕
ffmpeg -i video.mp4 -vf "subtitles=subtitle.srt:force_style='FontName=Microsoft YaHei,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=30'" final.mp4
```

**输出规格**：
- 分辨率：760x1280（竖版）或 1920x1080（横版）
- 音频：AAC 192k
- 字体：Microsoft YaHei，大小18
- 字幕：底部居中，白色文字+黑色描边

### 10. 字幕修正流程 ⭐重要
Whisper语音识别对技术术语的准确性有限，必须人工检查修正：

**常见识别错误**：
| 正确术语 | Whisper识别 | 说明 |
|---------|------------|------|
| Skills | Scales | 首字母s大写 |
| Github | Gathup | 发音近似 |
| ChatGPT | Chat GPT | 拼写错误 |
| yt-dlp | YTDLP | 大小写错误 |
| Pake | PAKE | 全大写 |
| ArchiveBox | ARCOVOX | 完全错误 |
| Ciphey | SIFE | 完全错误 |
| 小编 | 小边/小編 | 常见错字 |
| 简史 | 简矢 | 同音错误 |
| 拜拜滴啦 | 白白滴啦 | 语气词 |
| 连贯性 | 连惯性 | 同音错误 |

**修正步骤**：
1. 生成字幕后，打开SRT文件
2. 对照原文检查所有专有名词
3. 修正拼写和大小写
4. 使用修正后的SRT重新烧录

**修正命令**：
```bash
# 1. Whisper生成初始字幕
python scripts/generate_subtitle_whisper.py video.mp4 subtitles.srt

# 2. 手动修正 subtitles.srt 中的专业术语

# 3. 重新烧录修正后的字幕
python scripts/burn_subtitle.py video.mp4 subtitles_corrected.srt output.mp4
```

**建议**：对于技术类视频，建议先列出所有专业术语对照表，批量查找替换。

## 配置要求

```bash
export MODELSCOPE_API_KEY="你的密钥"
export FFMPEG_PATH="ffmpeg路径"
export FFPROBE_PATH="ffprobe路径"
```

### 依赖安装

```bash
# 必需
pip install edge-tts

# 可选（网页抓取备用方案）
pip install playwright
playwright install chromium

# 可选（场景渲染）
pip install manim
```

## 常见问题

### Q: 为什么背景图看不到？
A: 使用 `scripts/compose_video.py` 而不是 `scripts/merge_video.py`，前者会自动去除黑色背景

### Q: 为什么背景图变形了？
A: 优化版脚本会自动保持比例，如仍有问题请检查原始图片

### Q: 如何调整背景虚化程度？
A: 使用 `--blur` 参数（0-20）

### Q: 如何不生成字幕？
A: 添加 `--no-subtitle` 参数

### Q: 如何更改BGM音量？
A: 使用 `--bgm-vol` 参数（0.0-1.0，推荐0.15-0.25）

### Q: MCP工具不可用怎么办？
A: 使用 `scripts/fetch_content.py` 会自动切换到Playwright

### Q: BGM从哪里来？
A: 需要手动下载免版税音乐放入 `bgm/` 对应分类目录

### Q: 如何添加自定义BGM？
A: 将MP3文件放入 `bgm/` 下的分类目录即可

### Q: Whisper识别的字幕不准确怎么办？
A: Whisper对专业术语识别有限，需要人工修正SRT文件后再重新烧录。参见"字幕修正流程"章节
