# 背景音乐库 / Background Music Library

将无版权/免版税的背景音乐放在对应分类目录下。

## 目录结构 / Directory Structure

```
bgm/
├── inspirational/    # 励志、成长、Dan Koe风格
├── calm/            # 平静、科普、小编风格
├── upbeat/          # 轻快、活泼
└── tech/            # 科技感、电子
```

## 音乐推荐来源 / Recommended Sources

### 免费无版权音乐
1. **YouTube Audio Library** - 免费使用
2. **Pixabay Music** - 免费下载
3. **Bensound** - 免费音乐（需署名）
4. **Kevin MacLeod** - 免费音乐
5. **Epidemic Sound** - 付费订阅

### 中文BGM推荐
1. **耳聆网** - 免费音效/音乐
2. **爱给网** - 免费素材
3. **淘声网** - 声音搜索引擎

## 使用说明 / Usage

添加音乐文件时：
1. 文件名建议：`风格_描述.mp3`
2. 推荐格式：MP3, 320kbps
3. 推荐时长：2-5分钟（会自动循环）
4. 音量：保持原始音量，脚本会自动降低

示例：
- `inspirational/uplifting_piano.mp3`
- `calm/gentle_ambient.mp3`
- `tech/electronic_beat.mp3`

## 音量调整 / Volume Settings

脚本会自动将BGM音量降低到原始的15-25%，确保不影响解说。

可调参数：
- 低音量：15%（安静解说）
- 中音量：20%（平衡）
- 高音量：25%（动态内容）
