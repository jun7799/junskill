# -*- coding: utf-8 -*-
"""
视频合并脚本 - FFmpeg
Merge audio and video with precise duration matching
"""
import sys
import os
import subprocess
import json

# 默认 FFmpeg 路径 (Windows)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")


def get_audio_duration(audio_path: str) -> float:
    """
    获取音频精确时长

    Args:
        audio_path: 音频文件路径

    Returns:
        时长（秒）
    """
    cmd = [
        FFPROBE_PATH,
        "-i", audio_path,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        print(f"[WARN] Could not get audio duration: {e}")
        return 15.0


def merge_av(video_path: str, audio_path: str, output_path: str):
    """
    合并音视频，以音频时长为准

    Args:
        video_path: 视频文件路径
        audio_path: 音频文件路径
        output_path: 输出文件路径
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 获取音频时长
    audio_duration = get_audio_duration(audio_path)
    print(f"[INFO] Audio duration: {audio_duration:.2f}s")

    # FFmpeg 合并命令 - 使用音频时长
    cmd = [
        FFMPEG_PATH,
        "-y",  # 覆盖输出
        "-t", str(audio_duration),  # 以音频时长为准
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",  # 视频流直接复制
        "-c:a", "aac",  # 音频编码为AAC
        "-shortest",  # 以最短的流为准
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[OK] Merged: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Merge failed: {e}")
        print(f"[ERROR] stderr: {e.stderr}")
        return None


def main():
    if len(sys.argv) < 4:
        print("Usage: python merge_video.py <video> <audio> <output>")
        print("Example: python merge_video.py video.mp4 audio.mp3 merged.mp4")
        print("Environment: FFMPEG_PATH, FFPROBE_PATH")
        sys.exit(1)

    video_path = sys.argv[1]
    audio_path = sys.argv[2]
    output_path = sys.argv[3]

    merge_av(video_path, audio_path, output_path)


if __name__ == "__main__":
    main()
