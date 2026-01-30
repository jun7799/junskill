# -*- coding: utf-8 -*-
"""
背景音乐添加脚本
Add background music to video with automatic volume adjustment
"""
import subprocess
import os
import sys
import random
import json


BGM_CATEGORIES = {
    "inspirational": "励志、成长、Dan Koe风格",
    "calm": "平静、科普、小编风格",
    "upbeat": "轻快、活泼",
    "tech": "科技感、电子"
}


def get_video_duration(video_path: str, ffprobe_path: str = "ffprobe") -> float:
    """获取视频时长"""
    cmd = [
        ffprobe_path,
        "-i", video_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "json"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(json.loads(result.stdout)["format"]["duration"])
    except:
        return 120.0


def get_audio_duration(audio_path: str, ffprobe_path: str = "ffprobe") -> float:
    """获取音频时长"""
    cmd = [
        ffprobe_path,
        "-i", audio_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "json"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(json.loads(result.stdout)["format"]["duration"])
    except:
        return 180.0


def select_bgm(
    bgm_dir: str,
    category: str = None,
    ffprobe_path: str = "ffprobe",
    style: str = "xiaobian",
    keywords: list = None
) -> str:
    """
    选择背景音乐（智能选择 + 目录结构备选）

    Args:
        bgm_dir: BGM根目录
        category: 音乐分类（inspirational/calm/upbeat/tech）
        ffprobe_path: ffprobe路径
        style: 视频风格（用于智能选择）
        keywords: 内容关键词（用于智能匹配）

    Returns:
        选中的BGM文件路径，如果没找到则返回None
    """
    # 1. 优先使用智能选择（基于元数据）
    try:
        # 导入智能选择模块
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        select_module_path = os.path.join(skill_dir, "scripts", "select_bgm.py")

        if os.path.exists(select_module_path):
            # 动态导入选择函数
            import importlib.util
            spec = importlib.util.spec_from_file_location("select_bgm", select_module_path)
            select_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(select_module)

            selected_filename = select_module.select_bgm_by_style(bgm_dir, style, keywords)

            if selected_filename:
                bgm_path = os.path.join(bgm_dir, selected_filename)
                if os.path.exists(bgm_path):
                    return bgm_path
    except Exception as e:
        print(f"[DEBUG] Smart selection failed: {e}, using directory structure")

    # 2. Fallback: 使用目录结构选择
    # 如果指定了分类，从该分类选择
    if category and category in BGM_CATEGORIES:
        category_dir = os.path.join(bgm_dir, category)
        if os.path.exists(category_dir):
            bgm_files = [f for f in os.listdir(category_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
            if bgm_files:
                selected = random.choice(bgm_files)
                print(f"[INFO] Selected BGM (directory): {category}/{selected}")
                return os.path.join(category_dir, selected)

    # 从所有分类中选择
    all_bgm = []
    for cat in BGM_CATEGORIES.keys():
        category_dir = os.path.join(bgm_dir, cat)
        if os.path.exists(category_dir):
            bgm_files = [os.path.join(category_dir, f) for f in os.listdir(category_dir)
                        if f.endswith(('.mp3', '.wav', '.m4a'))]
            all_bgm.extend(bgm_files)

    # 如果目录结构也没有，尝试直接在bgm_dir找mp3文件
    if not all_bgm and os.path.exists(bgm_dir):
        bgm_files = [os.path.join(bgm_dir, f) for f in os.listdir(bgm_dir)
                    if f.endswith(('.mp3', '.wav', '.m4a'))]
        all_bgm = bgm_files

    if all_bgm:
        selected = random.choice(all_bgm)
        rel_path = os.path.relpath(selected, bgm_dir)
        print(f"[INFO] Selected BGM (random): {rel_path}")
        return selected

    print("[WARN] No BGM files found")
    return None


def add_bgm(
    video_path: str,
    bgm_path: str,
    output_path: str,
    bgm_volume: float = 0.20,
    fade_duration: float = 2.0,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe"
) -> bool:
    """
    添加背景音乐到视频

    Args:
        video_path: 输入视频路径
        bgm_path: 背景音乐路径
        output_path: 输出视频路径
        bgm_volume: BGM音量（0.0-1.0，推荐0.15-0.25）
        fade_duration: 淡入淡出时长（秒）
        ffmpeg_path: ffmpeg路径
        ffprobe_path: ffprobe路径

    Returns:
        是否成功
    """
    video_duration = get_video_duration(video_path, ffprobe_path)
    bgm_duration = get_audio_duration(bgm_path, ffprobe_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 如果BGM比视频短，需要循环
    # 构建amix滤镜
    # 音频滤镜链：1) 原视频音频 2) BGM降低音量+淡入淡出
    audio_filter = f"[1:a]volume={bgm_volume},afade=t=in:st=0:d={fade_duration},afade=t=out:st={video_duration-fade_duration}:d={fade_duration}[bgm]"

    # 使用amix混合音频
    cmd = [
        ffmpeg_path, "-y",
        "-i", video_path,
        "-stream_loop", "-1", "-i", bgm_path,  # 循环BGM
        "-filter_complex",
        f"{audio_filter};[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Failed to add BGM: {result.stderr[:300]}")
        return False

    print(f"[OK] BGM added: {output_path}")
    return True


def add_bgm_auto(
    video_path: str,
    bgm_dir: str,
    output_path: str,
    category: str = None,
    bgm_volume: float = 0.20,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe",
    style: str = "xiaobian",
    keywords: list = None
) -> bool:
    """
    自动选择并添加背景音乐

    Args:
        video_path: 输入视频路径
        bgm_dir: BGM目录
        output_path: 输出视频路径
        category: 音乐分类（可选，已弃用，建议使用style）
        bgm_volume: BGM音量
        ffmpeg_path: ffmpeg路径
        ffprobe_path: ffprobe路径
        style: 视频风格（xiaobian/dan_koe/tech/lifestyle/chinese）
        keywords: 内容关键词列表

    Returns:
        是否成功
    """
    bgm_path = select_bgm(bgm_dir, category, ffprobe_path, style, keywords)

    if not bgm_path:
        print("[WARN] No BGM available, copying original video")
        import shutil
        shutil.copy(video_path, output_path)
        return True

    return add_bgm(video_path, bgm_path, output_path, bgm_volume, 2.0, ffmpeg_path, ffprobe_path)


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("Usage: python add_bgm.py <video.mp4> <bgm_dir> <output.mp4> [category] [volume]")
        print("")
        print("Arguments:")
        print("  video.mp4  - Input video file")
        print("  bgm_dir    - Background music directory")
        print("  output.mp4 - Output video file")
        print("  category   - BGM category: inspirational/calm/upbeat/tech (optional)")
        print("  volume     - BGM volume 0.0-1.0, default 0.20 (optional)")
        print("")
        print("BGM Categories:")
        for cat, desc in BGM_CATEGORIES.items():
            print(f"  {cat}: {desc}")
        print("")
        print("Example:")
        print('  python add_bgm.py video.mp4 ../bgm output/final.mp4 inspirational 0.20')
        sys.exit(1)

    video_path = sys.argv[1]
    bgm_dir = sys.argv[2]
    output_path = sys.argv[3]
    category = sys.argv[4] if len(sys.argv) > 4 else None
    bgm_volume = float(sys.argv[5]) if len(sys.argv) > 5 else 0.20

    # 解析相对路径中的 ..
    bgm_dir = os.path.abspath(bgm_dir)

    add_bgm_auto(video_path, bgm_dir, output_path, category, bgm_volume)


if __name__ == "__main__":
    main()
