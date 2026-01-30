# Manim 图标库文档

本文档说明如何为 `book-video-generator` skill 添加自定义图标。

## 现有图标列表

| 图标名 | 英文 | 说明 |
|--------|------|------|
| 无图标 | none | 纯文字，无图形 |
| 向上箭头 | arrow_up | 兵力增加、数据上升 |
| 向下箭头 | arrow_down | 兵力减少、下降 |
| 问号 | question | 悬念、疑问 |
| 火焰 | fire | 火攻、战争 |
| 营寨燃烧 | camp_burn | 火烧连营 |
| 数字叉号 | numbers_cross | 失败、团灭 |
| 卷轴 | scroll | 历史、经典 |
| 天平左倾 | balance_left | 优势、实 |
| 天平右倾 | balance_right | 劣势、虚 |
| 波浪线 | wave | 节奏、流动 |
| 眼睛 | eye | 观察、信息 |
| 盾牌 | shield | 防御、隐藏 |
| 路径箭头 | arrow_path | 策略、变化 |
| 流动点 | flow | 灵活性 |
| 地图箭头 | map_arrow | 进军方向 |
| 撤退箭头 | retreat_arrow | 撤退、后退 |
| 链条 | chain | 连营、连接 |
| 暂停 | pause | 等待、时机 |
| 太阳 | sun | 夏天、时间 |
| 步骤 | steps | 分步流程 |
| 建筑 | building | 城市、商业 |
| 靶心 | target | 目标、弱点 |
| 星星 | star | 重点、亮点 |

## 添加新图标

### Step 1: 在 `scripts/render_scene.py` 中添加图标代码

找到 `ICON_CODES` 字典，添加新条目：

```python
ICON_CODES = {
    # ... 现有图标 ...

    "my_new_icon": '''
        # 这里写 Manim 绘图代码
        shape = Circle(radius=0.5, color=RED, fill_opacity=0.5)
        shape.next_to(text_obj, DOWN, buff=0.5)
        group.add(shape)
    ''',
}
```

### Step 2: 在 SKILL.md 中更新图标列表

编辑 `SKILL.md` 的图标表格，添加新图标。

### Manim 绘图参考

```python
# 基础形状
Circle(radius=0.5)
Square(side_length=1)
Triangle().scale(0.5)
Polygon(LEFT*1, UP*0.5, RIGHT*1, DOWN*0.5)

# 线条
Line(LEFT*2, RIGHT*2)
Arrow(ORIGIN, UP*1.5, color=RED, stroke_width=8)

# 文字/符号
Text("文字", font_size=48)
Tex("∑", font_size=72)
MathTex("x^2")

# 组合
VGroup(对象1, 对象2, 对象3)

# 颜色
RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, WHITE, GRAY, BROWN

# 位置
.next_to(对象, DOWN, buff=0.5)
.move_to(ORIGIN)
.shift(LEFT*2 + UP*1)

# 样式
.set_color(RED)
.set_fill(RED, opacity=0.5)
.stroke_width(4)
```

## 图标代码模板

```python
"<图标名>": '''
    # 描述：这是干什么的

    # 创建图形对象
    shape = ...  # Manim 图形

    # 添加到组
    shape.next_to(text_obj, DOWN, buff=0.5)
    group.add(shape)
''',
```

## 示例：添加"爱心"图标

```python
"heart": '''
    # 用文字符号当图标（最简单）
    heart = Text("", font_size=72)
    heart.set_color(RED)
    heart.next_to(text_obj, DOWN, buff=0.5)
    group.add(heart)
''',
```

或者用 Manim 画：

```python
"heart": '''
    # 用多边形画心形
    heart = VMobject()
    heart.set_points([
        UP*0.5,
        LEFT*0.5 + UP*0.2,
        ORIGIN,
        RIGHT*0.5 + UP*0.2,
        UP*0.5
    ])
    heart.set_color(RED)
    heart.set_fill(RED, opacity=0.5)
    heart.next_to(text_obj, DOWN, buff=0.5)
    group.add(heart)
''',
```
