# -*- coding: utf-8 -*-
"""
字幕生成脚本（Whisper语音识别版）
Generate subtitles using Whisper speech recognition
"""
import subprocess
import os
import sys


def generate_subtitle_whisper(
    video_path: str,
    output_srt: str,
    model_size: str = "small",
    language: str = "zh"
) -> bool:
    """
    使用Whisper语音识别生成字幕

    Args:
        video_path: 视频文件路径
        output_srt: 输出SRT文件路径
        model_size: Whisper模型大小 (tiny/base/small/medium/large)
        language: 语言代码

    Returns:
        是否成功
    """
    # 检查whisper是否安装
    try:
        import whisper
    except ImportError:
        print("[ERROR] whisper not installed. Run: pip install openai-whisper")
        return False

    print(f"[INFO] Generating subtitles with Whisper ({model_size} model)...")

    # 使用whisper命令行（更快）
    output_dir = os.path.dirname(output_srt)
    if not output_dir:
        output_dir = "."

    cmd = [
        "whisper",
        video_path,
        "--model", model_size,
        "--language", language,
        "--task", "transcribe",
        "--output_dir", output_dir,
        "--output_format", "srt",
        "--verbose", "False"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Whisper failed: {result.stderr}")
        return False

    # Whisper会生成 video_name.srt
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    whisper_srt = os.path.join(output_dir, f"{video_name}.srt")

    if os.path.exists(whisper_srt):
        # 重命名到目标路径
        if whisper_srt != output_srt:
            import shutil
            shutil.move(whisper_srt, output_srt)

        print(f"[OK] Subtitle saved: {output_srt}")
        return True

    return False


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("Usage: python generate_subtitle_whisper.py <video.mp4> <output.srt> [model_size]")
        print("")
        print("Arguments:")
        print("  video.mp4   - Input video file with speech")
        print("  output.srt  - Output SRT subtitle file")
        print("  model_size  - Whisper model: tiny/base/small/medium/large (default: small)")
        print("")
        print("Example:")
        print('  python generate_subtitle_whisper.py video.mp4 subtitles.srt small')
        sys.exit(1)

    video_path = sys.argv[1]
    output_path = sys.argv[2]
    model_size = sys.argv[3] if len(sys.argv) > 2 else "small"

    generate_subtitle_whisper(video_path, output_path, model_size)


if __name__ == "__main__":
    main()
