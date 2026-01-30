# -*- coding: utf-8 -*-
"""
字幕生成脚本
Generate subtitles (SRT) from script and audio timing
"""
import os
import sys
import json
import subprocess


def format_srt_time(seconds: float) -> str:
    """将秒数转换为SRT时间格式 (00:00:00,000)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


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
        return 15.0


def generate_segment_subtitle(
    audio_text: str,
    audio_path: str,
    output_path: str,
    words_per_line: int = 15,
    ffprobe_path: str = "ffprobe"
) -> str:
    """
    为单个片段生成字幕文件

    Args:
        audio_text: 配音文本
        audio_path: 音频文件路径
        output_path: 输出SRT文件路径
        words_per_line: 每行字幕字数
        ffprobe_path: ffprobe路径

    Returns:
        SRT文件内容
    """
    duration = get_audio_duration(audio_path, ffprobe_path)

    # 简单分词（中文按字符，英文按单词）
    def split_text(text):
        # 简单处理：中文字符直接算，英文按空格分
        words = []
        current = ""
        for char in text:
            if ord(char) > 127:  # 中文/非ASCII
                if current:
                    words.append(current)
                    current = ""
                words.append(char)
            else:
                if char == " ":
                    if current:
                        words.append(current)
                        current = ""
                else:
                    current += char
        if current:
            words.append(current)
        return words

    words = split_text(audio_text)
    total_words = len(words)

    # 计算每个字/词的时长
    time_per_word = duration / total_words if total_words > 0 else 0.5

    # 生成字幕条目
    srt_lines = []
    current_time = 0.0
    line_count = 1

    # 按行分组
    current_line = []
    current_line_chars = 0

    for word in words:
        char_count = len(word) if ord(word[0]) < 128 else 1  # 中文算1字，英文单词算字符数

        if current_line_chars + char_count > words_per_line and current_line:
            # 当前行满了，生成字幕
            line_text = "".join(current_line)
            line_duration = len(current_line) * time_per_word

            start_time = current_time
            end_time = current_time + line_duration

            srt_lines.append(f"{line_count}")
            srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
            srt_lines.append(line_text)
            srt_lines.append("")

            current_time = end_time
            line_count += 1
            current_line = [word]
            current_line_chars = char_count
        else:
            current_line.append(word)
            current_line_chars += char_count

    # 处理最后一行
    if current_line:
        line_text = "".join(current_line)
        line_duration = len(current_line) * time_per_word
        start_time = current_time
        end_time = min(current_time + line_duration, duration)

        srt_lines.append(f"{line_count}")
        srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
        srt_lines.append(line_text)
        srt_lines.append("")

    srt_content = "\n".join(srt_lines)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return srt_content


def generate_full_subtitle(
    script_json: str,
    audio_dir: str,
    output_path: str,
    ffprobe_path: str = "ffprobe"
) -> str:
    """
    为整个视频生成字幕文件（所有片段拼接）

    Args:
        script_json: 脚本JSON文件路径
        audio_dir: 音频文件目录
        output_path: 输出SRT文件路径
        ffprobe_path: ffprobe路径

    Returns:
        SRT文件内容
    """
    with open(script_json, "r", encoding="utf-8") as f:
        script = json.load(f)

    srt_lines = []
    current_time = 0.0
    subtitle_index = 1

    for segment in script.get("segments", []):
        seg_id = segment.get("id", 1)
        audio_text = segment.get("audio_text", "")
        audio_path = os.path.join(audio_dir, f"seg{seg_id:02d}.mp3")

        if not os.path.exists(audio_path):
            continue

        duration = get_audio_duration(audio_path, ffprobe_path)

        # 简单分词
        def split_text(text):
            words = []
            current = ""
            for char in text:
                if ord(char) > 127:
                    if current:
                        words.append(current)
                        current = ""
                    words.append(char)
                else:
                    if char == " ":
                        if current:
                            words.append(current)
                            current = ""
                    else:
                        current += char
            if current:
                words.append(current)
            return words

        words = split_text(audio_text)
        total_words = len(words)
        time_per_word = duration / total_words if total_words > 0 else 0.5

        # 按行生成字幕
        current_line = []
        current_line_chars = 0
        words_per_line = 15

        for word in words:
            char_count = len(word) if ord(word[0]) < 128 else 1

            if current_line_chars + char_count > words_per_line and current_line:
                line_text = "".join(current_line)
                line_duration = len(current_line) * time_per_word

                start_time = current_time
                end_time = current_time + line_duration

                srt_lines.append(f"{subtitle_index}")
                srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
                srt_lines.append(line_text)
                srt_lines.append("")

                current_time = end_time
                subtitle_index += 1
                current_line = [word]
                current_line_chars = char_count
            else:
                current_line.append(word)
                current_line_chars += char_count

        # 最后一行
        if current_line:
            line_text = "".join(current_line)
            line_duration = len(current_line) * time_per_word
            start_time = current_time
            end_time = min(current_time + line_duration, current_time + duration)

            srt_lines.append(f"{subtitle_index}")
            srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
            srt_lines.append(line_text)
            srt_lines.append("")

            current_time = end_time
            subtitle_index += 1

    srt_content = "\n".join(srt_lines)

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"[OK] Subtitle saved: {output_path}")
    return srt_content


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("Usage: python generate_subtitle.py <script.json> <audio_dir> <output.srt>")
        print("")
        print("Arguments:")
        print("  script.json  - Video script JSON file")
        print("  audio_dir    - Directory containing audio files")
        print("  output.srt   - Output SRT file path")
        print("")
        print("Example:")
        print('  python generate_subtitle.py video_script.json output/audio output/subtitles.srt')
        sys.exit(1)

    script_json = sys.argv[1]
    audio_dir = sys.argv[2]
    output_path = sys.argv[3]

    generate_full_subtitle(script_json, audio_dir, output_path)


if __name__ == "__main__":
    main()
