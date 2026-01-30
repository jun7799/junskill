# -*- coding: utf-8 -*-
"""
场景渲染脚本 - Manim
Render Manim animation scenes with synchronized key points
"""
import sys
import os
import json
import subprocess

# 图标代码库
ICON_CODES = {
    "none": "",
    "arrow_up": '''
        arrow = Arrow(ORIGIN, UP * 1.5, color=RED, stroke_width=8)
        arrow.next_to(text_obj, DOWN, buff=0.5)
        group.add(arrow)
''',
    "arrow_down": '''
        arrow = Arrow(ORIGIN, DOWN * 1.5, color=BLUE, stroke_width=8)
        arrow.next_to(text_obj, DOWN, buff=0.5)
        group.add(arrow)
''',
    "question": '''
        q = Text("?", font_size=72, weight=BOLD)
        q.set_color(YELLOW)
        q.next_to(text_obj, DOWN, buff=0.5)
        group.add(q)
''',
    "fire": '''
        fire = Triangle().scale(0.8)
        fire.set_color(ORANGE)
        fire.set_fill(ORANGE, opacity=0.6)
        fire.next_to(text_obj, DOWN, buff=0.5)
        group.add(fire)
''',
    "numbers_cross": '''
        cross = Line(UP*0.5+LEFT*0.5, DOWN*0.5+RIGHT*0.5, stroke_width=6, color=RED)
        cross2 = Line(UP*0.5+RIGHT*0.5, DOWN*0.5+LEFT*0.5, stroke_width=6, color=RED)
        cg = VGroup(cross, cross2)
        cg.next_to(text_obj, DOWN, buff=0.5)
        group.add(cg)
''',
    "scroll": '''
        scroll = Rectangle(width=4, height=1.5, color=YELLOW, fill_opacity=0.2)
        scroll.round_corners(radius=0.2)
        scroll.next_to(text_obj, DOWN, buff=0.5)
        group.add(scroll)
''',
    "balance_left": '''
        balance = Line(LEFT*2, RIGHT*2, stroke_width=4)
        tri = Triangle().scale(0.5).move_to(DOWN*1.2)
        tilt = Line(LEFT*1.5, UP*0.5+RIGHT*1.5, stroke_width=4, color=RED)
        bg = VGroup(balance, tri, tilt)
        bg.next_to(text_obj, DOWN, buff=0.5)
        group.add(bg)
''',
    "balance_right": '''
        balance = Line(LEFT*2, RIGHT*2, stroke_width=4)
        tri = Triangle().scale(0.5).move_to(DOWN*1.2)
        tilt = Line(LEFT*1.5+UP*0.5, RIGHT*1.5, stroke_width=4, color=BLUE)
        bg = VGroup(balance, tri, tilt)
        bg.next_to(text_obj, DOWN, buff=0.5)
        group.add(bg)
''',
    "wave": '''
        wave = FunctionGraph(lambda x: 0.3*np.sin(2*x), x_range=[-2,2])
        wave.set_color(BLUE)
        wave.stroke_width = 4
        wave.next_to(text_obj, DOWN, buff=0.5)
        group.add(wave)
''',
    "eye": '''
        eye_outer = Circle(radius=0.5, color=WHITE, stroke_width=3)
        eye_inner = Circle(radius=0.2, color=BLUE, fill_opacity=0.8)
        eg = VGroup(eye_outer, eye_inner)
        eg.next_to(text_obj, DOWN, buff=0.5)
        group.add(eg)
''',
    "shield": '''
        shield = Polygon(ORIGIN, UP*0.8+LEFT*0.4, UP*0.8+RIGHT*0.4)
        shield.set_color(RED)
        shield.set_fill(RED, opacity=0.3)
        shield.next_to(text_obj, DOWN, buff=0.5)
        group.add(shield)
''',
    "arrow_path": '''
        a1 = Arrow(LEFT*3+UP*0.5, LEFT*1+UP*0.5, color=BLUE, stroke_width=6)
        a2 = Arrow(LEFT*1+UP*0.5, RIGHT*1+DOWN*0.5, color=GREEN, stroke_width=6)
        ag = VGroup(a1, a2)
        ag.next_to(text_obj, DOWN, buff=0.5)
        group.add(ag)
''',
    "flow": '''
        dots = VGroup()
        for j in range(7):
            d = Dot(radius=0.15, color=BLUE, fill_opacity=0.8)
            d.shift(LEFT*2 + j*0.6)
            dots.add(d)
        dots.next_to(text_obj, DOWN, buff=0.5)
        group.add(dots)
''',
    "map_arrow": '''
        arrow = Arrow(LEFT*2, ORIGIN, color=RED, stroke_width=10, max_tip_length_to_length_ratio=0.3)
        arrow.next_to(text_obj, DOWN, buff=0.5)
        group.add(arrow)
''',
    "retreat_arrow": '''
        arrow = Arrow(ORIGIN, LEFT*2, color=BLUE, stroke_width=8)
        arrow.next_to(text_obj, DOWN, buff=0.5)
        group.add(arrow)
''',
    "chain": '''
        chain = VGroup()
        for j in range(6):
            link = Square(side_length=0.3, color=GRAY, stroke_width=2)
            link.shift(LEFT*1.5 + j*0.35)
            chain.add(link)
        chain.next_to(text_obj, DOWN, buff=0.5)
        group.add(chain)
''',
    "pause": '''
        pause = VGroup()
        pause.add(Rectangle(width=0.3, height=0.8, color=WHITE, fill_opacity=0.8))
        pause.add(Rectangle(width=0.3, height=0.8, color=WHITE, fill_opacity=0.8).shift(RIGHT*0.5))
        pause.next_to(text_obj, DOWN, buff=0.5)
        group.add(pause)
''',
    "sun": '''
        sun = Circle(radius=0.6, color=YELLOW, fill_opacity=0.6)
        rays = VGroup()
        for j in range(8):
            angle = j*PI/4
            ray = Line(ORIGIN, 0.8*np.array([np.cos(angle), np.sin(angle), 0]), color=YELLOW, stroke_width=3)
            rays.add(ray)
        sg = VGroup(sun, rays).move_to(sun.get_center())
        sg.next_to(text_obj, DOWN, buff=0.5)
        group.add(sg)
''',
    "steps": '''
        steps = VGroup()
        for j in range(4):
            step = Circle(radius=0.3, color=WHITE, fill_opacity=0.2)
            num = Text(str(j+1), font_size=24).move_to(step.get_center())
            sg = VGroup(step, num)
            sg.shift(LEFT*2 + j*1.3)
            steps.add(sg)
        steps.next_to(text_obj, DOWN, buff=0.5)
        group.add(steps)
''',
    "building": '''
        small = Rectangle(width=0.8, height=1.2, color=BLUE, fill_opacity=0.3)
        big = Rectangle(width=1.5, height=2.5, color=RED, fill_opacity=0.3)
        big.next_to(small, RIGHT, buff=0.5)
        bg = VGroup(small, big)
        bg.next_to(text_obj, DOWN, buff=0.5)
        group.add(bg)
''',
    "target": '''
        outer = Circle(radius=0.8, color=RED, stroke_width=3)
        middle = Circle(radius=0.5, color=WHITE, stroke_width=3)
        inner = Circle(radius=0.2, color=RED, fill_opacity=0.8)
        tg = VGroup(outer, middle, inner)
        tg.next_to(text_obj, DOWN, buff=0.5)
        group.add(tg)
''',
    "star": '''
        star = Text("★", font_size=72)
        star.set_color(YELLOW)
        star.next_to(text_obj, DOWN, buff=0.5)
        group.add(star)
''',
    "camp_burn": '''
        camps = VGroup()
        for j in range(5):
            camp = Square(side_length=0.4, color=GRAY, fill_opacity=0.3)
            camp.shift(LEFT*1.5 + j*0.5)
            camps.add(camp)
        camps.next_to(text_obj, DOWN, buff=0.5)
        group.add(camps)
''',
}


def create_scene_code(segment_data: dict, bg_image: str = None) -> str:
    """
    根据片段数据生成 Manim 场景代码

    Args:
        segment_data: 片段JSON数据
        bg_image: 背景图片路径

    Returns:
        Manim Python 代码字符串
    """
    seg_id = segment_data.get("id", 1)
    title = segment_data.get("title", "")
    duration = segment_data.get("duration", 15.0)
    key_points = segment_data.get("key_points", [])

    num_points = len(key_points)
    time_per_point = duration / num_points if num_points > 0 else 3.0

    code = f'''# -*- coding: utf-8 -*-
from manim import *
import os

class Segment{seg_id}Scene(Scene):
    """片段{seg_id} - {title}"""

    def construct(self):
'''

    # 背景图
    if bg_image:
        code += f'''        # 背景
        background = ImageMobject("{bg_image}")
        background.scale_to_fit_height(config.frame_height)
        background.set_opacity(0.3)
        self.add(background)

        overlay = Rectangle(width=config.frame_width, height=config.frame_height, color=BLACK, fill_opacity=0.4)
        self.add(overlay)

'''

    # 关键点动画
    for i, point in enumerate(key_points):
        text = point.get("text", "")
        icon = point.get("icon", "none")
        icon_code = ICON_CODES.get(icon, "")

        if i == 0:
            anim_time = 0.8
        else:
            anim_time = 0.5

        wait_time = max(0.3, time_per_point - anim_time)

        code += f'''        # 关键点 {i+1}: "{text}"
        group = VGroup()
        text_obj = Text("{text}", font_size=48, weight=BOLD)
        text_obj.set_color_by_gradient(ORANGE, YELLOW)
        group.add(text_obj)
{icon_code}
        group.move_to(ORIGIN)
'''

        if i == 0:
            code += f'''        self.play(FadeIn(group), run_time={anim_time})
        self.wait({wait_time:.1f})
'''
        else:
            code += f'''        self.play(ReplacementTransform(prev_group, group), run_time={anim_time})
        self.wait({wait_time:.1f})
'''

        code += "        prev_group = group\n"

    code += '''        self.wait(1)
'''

    return code


def render_scene(json_path: str, output_path: str = None):
    """
    渲染 Manim 场景

    Args:
        json_path: 片段数据JSON路径
        output_path: 输出视频路径 (可选)
    """
    with open(json_path, "r", encoding="utf-8") as f:
        segment_data = json.load(f)

    seg_id = segment_data.get("id", 1)

    # 查找背景图
    json_dir = os.path.dirname(json_path)
    bg_image = os.path.join(json_dir, f"seg{seg_id}_bg.png")
    if not os.path.exists(bg_image):
        bg_image = None

    # 生成场景代码
    scene_code = create_scene_code(segment_data, bg_image)

    # 写入临时文件
    temp_file = f"temp_scene_{seg_id}.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(scene_code)

    # 渲染
    cmd = [
        "manim", "render", temp_file, f"Segment{seg_id}Scene",
        "-qm", "--format=mp4"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)

        # 查找输出文件
        output_video = f"media/videos/temp_scene_{seg_id}/720p30/Segment{seg_id}Scene.mp4"

        if os.path.exists(output_video):
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                import shutil
                shutil.move(output_video, output_path)
                print(f"[OK] Video saved: {output_path}")
            else:
                print(f"[OK] Video saved: {output_video}")
            return output_video if output_path else output_video
        else:
            print(f"[ERROR] Video file not found")
            return None

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Render failed: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_scene.py <segment_json> [output_path]")
        print("Example: python render_scene.py segment1.json output/segment1.mp4")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    render_scene(json_path, output_path)


if __name__ == "__main__":
    main()
