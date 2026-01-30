# -*- coding: utf-8 -*-
"""
字幕烧录脚本 - 将SRT字幕硬编码到视频
Burn subtitles into video using FFmpeg drawtext
"""
import subprocess
import os
import sys


def srt_to_ass(srt_path: str, ass_path: str = None) -> str:
    """
    将SRT转换为ASS格式（更好的中文支持）

    Args:
        srt_path: SRT文件路径
        ass_path: 输出ASS文件路径（可选）

    Returns:
        ASS文件内容
    """
    with open(srt_path, "r", encoding="utf-8") as f:
        srt_content = f.read()

    # 简单的SRT到ASS转换
    lines = srt_content.split("\n")

    ass_header = """[Script Info]
Title: Karaoke
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_lines = [ass_header]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():
            # 字幕序号
            if i + 1 < len(lines):
                time_line = lines[i + 1].strip()
                if "-->" in time_line:
                    # 解析时间
                    times = time_line.split("-->")
                    start = times[0].strip().replace(",", ".")
                    end = times[1].strip().replace(",", ".")

                    # SRT时间转ASS时间 (0:00:00.000 -> 0:00:00.00)
                    def srt_to_ass(t):
                        parts = t.split(":")
                        h = int(parts[0])
                        m = int(parts[1])
                        s_parts = parts[2].split(".")
                        s = int(s_parts[0])
                        ms = int(s_parts[1]) if len(s_parts) > 1 else 0
                        total_ms = h * 3600000 + m * 60000 + s * 1000 + ms
                        return f"{total_ms // 3600000}:{(total_ms % 3600000) // 60000:02d}:{(total_ms % 60000) // 1000:02d}.{total_ms % 1000:02d}"

                    # 获取字幕文本
                    text_lines = []
                    i += 2
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1

                    text = "\\N".join(text_lines)  # ASS换行符
                    # 转义特殊字符
                    text = text.replace("&", "&amp;")

                    ass_lines.append(f"Dialogue: 0,{srt_to_ass(start)},{srt_to_ass(end)},Default,,0,0,0,,{text}")
        i += 1

    ass_content = "\n".join(ass_lines)

    if ass_path:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

    return ass_content


def burn_subtitle(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_size: int = 48,
    font_color: str = "white",
    ffmpeg_path: str = "ffmpeg"
) -> bool:
    """
    将字幕烧录到视频中（使用ASS格式）

    Args:
        video_path: 输入视频路径
        srt_path: SRT字幕文件路径
        output_path: 输出视频路径
        font_size: 字体大小
        font_color: 字体颜色
        ffmpeg_path: ffmpeg路径

    Returns:
        是否成功
    """
    # 转换SRT到ASS
    ass_path = srt_path.replace(".srt", ".ass")
    srt_to_ass(srt_path, ass_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 使用ASS字幕滤镜
    cmd = [
        ffmpeg_path, "-y",
        "-i", video_path,
        "-vf", f"ass='{ass_path}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Failed to burn subtitle: {result.stderr[:300]}")
        return False

    print(f"[OK] Subtitle burned: {output_path}")
    return True


def burn_subtitle_drawtext(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_size: int = 48,
    font_name: str = "Arial",
    ffmpeg_path: str = "ffmpeg"
) -> bool:
    """
    将字幕烧录到视频中（使用drawtext，备用方案）

    Args:
        video_path: 输入视频路径
        srt_path: SRT字幕文件路径
        output_path: 输出视频路径
        font_size: 字体大小
        font_name: 字体名称
        ffmpeg_path: ffmpeg路径

    Returns:
        是否成功
    """
    # 读取SRT字幕
    with open(srt_path, "r", encoding="utf-8") as f:
        srt_content = f.read()

    # 解析SRT字幕
    def parse_srt_time(time_str):
        parts = time_str.strip().replace(",", ".").split(":")
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        return h * 3600 + m * 60 + s

    subtitles = []
    lines = srt_content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():
            if i + 1 < len(lines) and "-->" in lines[i + 1]:
                time_line = lines[i + 1].strip()
                times = time_line.split("-->")
                start_time = parse_srt_time(times[0])
                end_time = parse_srt_time(times[1])

                # 获取文本
                text_lines = []
                i += 2
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1

                text = " ".join(text_lines)
                subtitles.append({
                    "start": start_time,
                    "end": end_time,
                    "text": text
                })
        i += 1

    # 构建drawtext滤镜链
    filter_parts = []
    for sub in subtitles:
        # 转义文本中的特殊字符
        text = sub["text"].replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        filter_parts.append(
            f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_name}:"
            f"x=(w-tw)/2:y=h-120:enable='between(t,{sub['start']},{sub['end']})'"
        )

    # FFmpeg对filter链长度有限制，如果字幕太多可能需要分段处理
    # 这里简单处理：只取前50条字幕（大约1分钟内容）
    if len(filter_parts) > 50:
        print(f"[WARN] Too many subtitles ({len(filter_parts)}), using first 50")
        filter_parts = filter_parts[:50]

    filter_complex = ",".join(filter_parts)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        ffmpeg_path, "-y",
        "-i", video_path,
        "-vf", filter_complex,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Failed to burn subtitle: {result.stderr[:300]}")
        return False

    print(f"[OK] Subtitle burned: {output_path}")
    return True


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("Usage: python burn_subtitle.py <video.mp4> <subtitle.srt> <output.mp4>")
        print("")
        print("Arguments:")
        print("  video.mp4    - Input video file")
        print("  subtitle.srt - SRT subtitle file")
        print("  output.mp4   - Output video file")
        print("")
        print("Example:")
        print('  python burn_subtitle.py video.mp4 subtitles.srt video_with_sub.mp4')
        sys.exit(1)

    video_path = sys.argv[1]
    srt_path = sys.argv[2]
    output_path = sys.argv[3]

    # 优先使用ASS格式（更好的中文支持）
    success = burn_subtitle(video_path, srt_path, output_path)

    # 如果失败，尝试drawtext方案
    if not success:
        print("[WARN] ASS method failed, trying drawtext method...")
        burn_subtitle_drawtext(video_path, srt_path, output_path)


if __name__ == "__main__":
    main()
