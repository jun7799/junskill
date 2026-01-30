# -*- coding: utf-8 -*-
"""
视频预览帧生成脚本
Generate preview frames from video for quick verification
"""
import subprocess
import os
import sys


def generate_previews(
    video_path: str,
    output_dir: str,
    count: int = 3,
    ffmpeg_path: str = "ffmpeg"
) -> list:
    """
    从视频中提取预览帧

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        count: 提取帧数（默认3帧，均匀分布）
        ffmpeg_path: ffmpeg可执行文件路径

    Returns:
        生成的预览图路径列表
    """
    os.makedirs(output_dir, exist_ok=True)

    # 获取视频时长
    probe_cmd = [
        ffmpeg_path.replace("ffmpeg", "ffprobe"),
        "-i", video_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "json"
    ]

    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        import json
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except:
        duration = 30.0

    preview_paths = []

    # 均匀提取帧
    for i in range(count):
        timestamp = duration * (i + 1) / (count + 1)
        output_path = os.path.join(output_dir, f"preview_{i+1}.jpg")

        cmd = [
            ffmpeg_path, "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(output_path):
            preview_paths.append(output_path)
            print(f"[OK] Preview {i+1}: {output_path} (at {timestamp:.1f}s)")
        else:
            print(f"[WARN] Failed to extract preview {i+1}")

    return preview_paths


def generate_segment_previews(
    segments_dir: str,
    output_dir: str,
    count_per_segment: int = 1,
    ffmpeg_path: str = "ffmpeg"
) -> dict:
    """
    批量生成所有片段的预览帧

    Args:
        segments_dir: 片段视频目录
        output_dir: 输出目录
        count_per_segment: 每个片段提取帧数
        ffmpeg_path: ffmpeg可执行文件路径

    Returns:
        {segment_name: [preview_paths]} 的字典
    """
    import glob
    segment_files = sorted(glob.glob(os.path.join(segments_dir, "seg*.mp4")))

    if not segment_files:
        print(f"[WARN] No segment files found in {segments_dir}")
        return {}

    os.makedirs(output_dir, exist_ok=True)

    previews = {}

    for segment_file in segment_files:
        segment_name = os.path.basename(segment_file)
        seg_output_dir = os.path.join(output_dir, segment_name.replace(".mp4", ""))
        preview_paths = generate_previews(segment_file, seg_output_dir, count_per_segment, ffmpeg_path)
        previews[segment_name] = preview_paths

    return previews


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("Usage: python generate_preview.py <video_path> <output_dir> [count]")
        print("")
        print("Arguments:")
        print("  video_path  - Video file path")
        print("  output_dir  - Output directory for preview frames")
        print("  count       - Number of frames to extract (default: 3)")
        print("")
        print("Example:")
        print("  python generate_preview.py output/final_video.mp4 output/previews 5")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    print(f"[INFO] Generating {count} preview frames from {video_path}...")

    previews = generate_previews(video_path, output_dir, count)

    if previews:
        print(f"[DONE] Generated {len(previews)} preview frames in {output_dir}")
        print("[INFO] Use these to verify video quality before publishing")
    else:
        print("[ERROR] No previews generated")


if __name__ == "__main__":
    main()
