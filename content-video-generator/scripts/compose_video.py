# -*- coding: utf-8 -*-
"""
优化版视频合成脚本（集成字幕和BGM）
Optimized video composition with:
- Black background removal (colorkey)
- Proper background scaling
- Optional blur effect
- Auto subtitle generation
- Auto BGM addition
- Windows path compatibility
"""
import subprocess
import os
import sys
import json

# 获取skill目录
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, skill_dir)

BGM_CATEGORIES = {
    "inspirational": "励志、成长、Dan Koe风格",
    "calm": "平静、科普、小编风格",
    "upbeat": "轻快、活泼",
    "tech": "科技感、电子"
}


def get_duration(file_path: str, ffprobe_path: str = "ffprobe") -> float:
    """获取媒体文件时长"""
    cmd = [
        ffprobe_path,
        "-i", file_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "json"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(json.loads(result.stdout)["format"]["duration"])
    except:
        return 15.0


def compose_segment(
    bg_image: str,
    scene_video: str,
    audio_path: str,
    output_path: str,
    blur_sigma: float = 0,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe"
) -> bool:
    """
    合成视频片段（优化版）

    Args:
        bg_image: 背景图片路径
        scene_video: 场景视频路径（Manim渲染的）
        audio_path: 音频路径
        output_path: 输出视频路径
        blur_sigma: 背景虚化强度（0=不虚化，推荐值：8-15）
        ffmpeg_path: ffmpeg可执行文件路径
        ffprobe_path: ffprobe可执行文件路径

    Returns:
        是否成功
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    audio_duration = get_duration(audio_path, ffprobe_path)

    # 构建滤镜链
    # 1. 背景图：缩放+裁剪（保持比例）+ 可选虚化
    # 2. 场景视频：去黑底（colorkey）
    # 3. 叠加
    filters = "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(iw-ow)/2:(ih-oh)/2"

    # 添加虚化效果
    if blur_sigma > 0:
        filters += f",gblur=sigma={blur_sigma}"

    filters += "[bg];"
    filters += "[1:v]colorkey=black:0.1:0.5[fg];"
    filters += "[bg][fg]overlay=(W-w)/2:(H-h)/2[video]"

    cmd = [
        ffmpeg_path, "-y",
        "-loop", "1", "-i", bg_image,
        "-i", scene_video,
        "-i", audio_path,
        "-filter_complex", filters,
        "-map", "[video]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac",
        "-shortest",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Composition failed: {result.stderr[:300]}")
        return False

    print(f"[OK] Composed: {output_path}")
    return True


def compose_all_segments(
    script_json: str,
    bg_dir: str,
    scene_dir: str,
    audio_dir: str,
    output_dir: str,
    blur_sigma: float = 12,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe"
) -> str:
    """
    批量合成所有片段并拼接最终视频

    Args:
        script_json: 脚本JSON文件路径
        bg_dir: 背景图片目录
        scene_dir: 场景视频目录
        audio_dir: 音频目录
        output_dir: 输出目录
        blur_sigma: 背景虚化强度
        ffmpeg_path: ffmpeg可执行文件路径
        ffprobe_path: ffprobe可执行文件路径

    Returns:
        最终视频路径
    """
    with open(script_json, "r", encoding="utf-8") as f:
        script = json.load(f)

    segments_dir = os.path.join(output_dir, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    print(f"[INFO] Composing {len(script['segments'])} segments...")

    # 合成每个片段
    for i, segment in enumerate(script["segments"], 1):
        seg_id = segment.get("id", i)
        bg_image = os.path.join(bg_dir, f"seg{seg_id:02d}_bg.png")
        scene_video = os.path.join(scene_dir, f"seg{seg_id:02d}.mp4")
        audio_path = os.path.join(audio_dir, f"seg{seg_id:02d}.mp3")
        output_path = os.path.join(segments_dir, f"seg{seg_id:02d}.mp4")

        print(f"[INFO] Segment {seg_id}/{len(script['segments'])}...")

        if not os.path.exists(bg_image) or not os.path.exists(scene_video) or not os.path.exists(audio_path):
            print(f"[WARN] Missing files for segment {seg_id}, skipping")
            continue

        compose_segment(bg_image, scene_video, audio_path, output_path, blur_sigma, ffmpeg_path, ffprobe_path)

    # 拼接最终视频（处理Windows路径问题）
    print("[INFO] Concatenating final video...")

    # 在segments目录内创建list文件，避免路径编码问题
    original_dir = os.getcwd()
    os.chdir(segments_dir)

    with open("list.txt", "w", encoding="utf-8") as f:
        for i, segment in enumerate(script["segments"], 1):
            seg_id = segment.get("id", i)
            f.write(f"file 'seg{seg_id:02d}.mp4'\n")

    final_output = "final_video.mp4"
    concat_cmd = [
        ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0",
        "-i", "list.txt",
        "-c", "copy",
        final_output
    ]

    result = subprocess.run(concat_cmd, capture_output=True, text=True)

    os.chdir(original_dir)

    if result.returncode != 0 or not os.path.exists(os.path.join(segments_dir, final_output)):
        print(f"[ERROR] Concatenation failed")
        return None

    # 移动到输出目录
    final_path = os.path.join(output_dir, "final_video.mp4")
    os.rename(os.path.join(segments_dir, final_output), final_path)

    size_mb = os.path.getsize(final_path) / (1024 * 1024)
    print(f"[OK] Final video: {final_path} ({size_mb:.2f} MB)")

    return final_path


def add_subtitle_and_bgm(
    video_path: str,
    script_json: str,
    audio_dir: str,
    bgm_dir: str,
    output_path: str,
    bgm_category: str = None,
    bgm_volume: float = 0.20,
    burn_subtitle: bool = True,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe",
    style: str = "xiaobian",
    keywords: list = None
) -> str:
    """
    添加字幕和背景音乐

    Args:
        video_path: 输入视频路径
        script_json: 脚本JSON文件路径
        audio_dir: 音频目录
        bgm_dir: BGM目录
        output_path: 输出视频路径
        bgm_category: BGM分类（已弃用，建议使用style）
        bgm_volume: BGM音量
        burn_subtitle: 是否烧录字幕
        ffmpeg_path: ffmpeg路径
        ffprobe_path: ffprobe路径
        style: 视频风格（xiaobian/dan_koe/tech/lifestyle/chinese）
        keywords: 内容关键词列表

    Returns:
        最终视频路径
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. 生成字幕（优先使用Whisper语音识别）
    print("[INFO] Generating subtitles with Whisper...")
    srt_path = os.path.join(os.path.dirname(output_path), "subtitles.srt")

    try:
        # 优先使用Whisper语音识别（更准确）
        from scripts.generate_subtitle_whisper import generate_subtitle_whisper
        whisper_success = generate_subtitle_whisper(video_path, srt_path, "small", "zh")

        if not whisper_success:
            # Whisper失败，使用fallback方案
            print("[WARN] Whisper failed, using script-based subtitles")
            from scripts.generate_subtitle import generate_full_subtitle
            generate_full_subtitle(script_json, audio_dir, srt_path, ffprobe_path)

        # 烧录字幕
        if burn_subtitle:
            print("[INFO] Burning subtitles into video...")
            temp_video = os.path.join(os.path.dirname(output_path), "temp_with_sub.mp4")

            try:
                from scripts.burn_subtitle import burn_subtitle
                burn_subtitle(video_path, srt_path, temp_video, ffmpeg_path=ffmpeg_path)
                video_path = temp_video
            except Exception as e:
                print(f"[WARN] Failed to burn subtitle: {e}")
    except Exception as e:
        print(f"[WARN] Failed to generate subtitle: {e}")

    # 2. 添加BGM（使用智能选择）
    if bgm_dir and os.path.exists(bgm_dir):
        print(f"[INFO] Adding background music (style: {style}, keywords: {keywords})...")

        try:
            from scripts.add_bgm import add_bgm_auto
            add_bgm_auto(
                video_path, bgm_dir, output_path,
                bgm_category, bgm_volume,
                ffmpeg_path, ffprobe_path,
                style, keywords
            )
            print(f"[OK] Final video with subtitle and BGM: {output_path}")
            return output_path
        except Exception as e:
            print(f"[WARN] Failed to add BGM: {e}")

    # BGM添加失败，直接返回原视频
    import shutil
    shutil.copy(video_path, output_path)
    print(f"[OK] Final video: {output_path}")
    return output_path


def compose_full_video(
    script_json: str,
    bg_dir: str,
    scene_dir: str,
    audio_dir: str,
    output_dir: str,
    blur_sigma: float = 12,
    bgm_dir: str = None,
    bgm_category: str = None,
    bgm_volume: float = 0.20,
    burn_subtitle: bool = True,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe",
    style: str = "xiaobian",
    keywords: list = None
) -> str:
    """
    完整视频合成流程（包含字幕和BGM）

    Args:
        script_json: 脚本JSON文件路径
        bg_dir: 背景图片目录
        scene_dir: 场景视频目录
        audio_dir: 音频目录
        output_dir: 输出目录
        blur_sigma: 背景虚化强度
        bgm_dir: BGM目录
        bgm_category: BGM分类（已弃用，建议使用style）
        bgm_volume: BGM音量
        burn_subtitle: 是否烧录字幕
        ffmpeg_path: ffmpeg路径
        ffprobe_path: ffprobe路径
        style: 视频风格（xiaobian/dan_koe/tech/lifestyle/chinese）
        keywords: 内容关键词列表

    Returns:
        最终视频路径
    """
    # 1. 合成视频片段并拼接
    base_video = compose_all_segments(
        script_json, bg_dir, scene_dir, audio_dir,
        output_dir, blur_sigma, ffmpeg_path, ffprobe_path
    )

    if not base_video:
        print("[ERROR] Failed to compose base video")
        return None

    # 2. 添加字幕和BGM（使用智能选择）
    final_video = os.path.join(output_dir, "final_video_complete.mp4")

    add_subtitle_and_bgm(
        base_video, script_json, audio_dir, bgm_dir, final_video,
        bgm_category, bgm_volume, burn_subtitle, ffmpeg_path, ffprobe_path,
        style, keywords
    )

    return final_video


def main():
    """命令行入口"""
    if len(sys.argv) < 6:
        print("Usage: python compose_video.py <script.json> <bg_dir> <scene_dir> <audio_dir> <output_dir> [options]")
        print("")
        print("Arguments:")
        print("  script.json   - Video script JSON file")
        print("  bg_dir        - Background images directory")
        print("  scene_dir     - Scene videos directory")
        print("  audio_dir     - Audio files directory")
        print("  output_dir    - Output directory")
        print("")
        print("Options:")
        print("  --blur N          - Background blur strength (default: 12)")
        print("  --bgm DIR         - Background music directory")
        print("  --style STYLE     - Video style: xiaobian/dan_koe/tech/lifestyle/chinese (default: xiaobian)")
        print("  --keywords KW1,KW2 - Content keywords for BGM matching (comma-separated)")
        print("  --bgm-cat CAT     - BGM category: inspirational/calm/upbeat/tech (deprecated, use --style)")
        print("  --bgm-vol N       - BGM volume 0.0-1.0 (default: 0.20)")
        print("  --no-subtitle     - Don't burn subtitles")
        print("")
        print("Examples:")
        print('  python compose_video.py video_script.json output/images output/scenes output/audio output/final --blur 12 --bgm "D:\\资源\\bgm" --style dan_koe')
        print('  python compose_video.py video_script.json output/images output/scenes output/audio output/final --bgm "D:\\资源\\bgm" --style tech --keywords "科技","AI"')
        sys.exit(1)

    script_json = sys.argv[1]
    bg_dir = sys.argv[2]
    scene_dir = sys.argv[3]
    audio_dir = sys.argv[4]
    output_dir = sys.argv[5]

    # 解析可选参数
    blur_sigma = 12
    bgm_dir = None
    bgm_category = None
    bgm_volume = 0.20
    burn_subtitle = True
    style = "xiaobian"
    keywords = None

    i = 6
    while i < len(sys.argv):
        if sys.argv[i] == "--blur" and i + 1 < len(sys.argv):
            blur_sigma = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--bgm" and i + 1 < len(sys.argv):
            bgm_dir = os.path.abspath(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--style" and i + 1 < len(sys.argv):
            style = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--keywords" and i + 1 < len(sys.argv):
            keywords_str = sys.argv[i + 1]
            keywords = [k.strip() for k in keywords_str.split(",")]
            i += 2
        elif sys.argv[i] == "--bgm-cat" and i + 1 < len(sys.argv):
            bgm_category = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--bgm-vol" and i + 1 < len(sys.argv):
            bgm_volume = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--no-subtitle":
            burn_subtitle = False
            i += 1
        else:
            i += 1

    result = compose_full_video(
        script_json, bg_dir, scene_dir, audio_dir, output_dir,
        blur_sigma, bgm_dir, bgm_category, bgm_volume, burn_subtitle,
        "ffmpeg", "ffprobe", style, keywords
    )

    if result:
        print(f"[DONE] Video saved to: {result}")
    else:
        print("[ERROR] Video composition failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
