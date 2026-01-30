# -*- coding: utf-8 -*-
"""
配音生成脚本 - Edge-TTS
Generate Chinese voiceover using Edge-TTS
"""
import sys
import asyncio
import edge_tts
import os

async def generate_audio(text: str, output_path: str, voice: str = "zh-CN-YunxiNeural"):
    """
    生成中文配音

    Args:
        text: 配音文本
        output_path: 输出MP3路径
        voice: 音色 (默认: zh-CN-YunxiNeural 男声自然)

    语音选项:
    - zh-CN-YunxiNeural: 男声, 自然
    - zh-CN-YunyangNeural: 男声, 沉稳
    - zh-CN-XiaoxiaoNeural: 女声, 清脆
    - zh-CN-XiaoyiNeural: 女声, 温柔
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    communicate = edge_tts.Communicate(text, voice)

    await communicate.save(output_path)
    print(f"[OK] Audio saved: {output_path}")
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_audio.py <text> <output_path> [voice]")
        print("Example: python generate_audio.py '你好世界' output.mp3")
        sys.exit(1)

    text = sys.argv[1]
    output_path = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-YunxiNeural"

    asyncio.run(generate_audio(text, output_path, voice))


if __name__ == "__main__":
    main()
