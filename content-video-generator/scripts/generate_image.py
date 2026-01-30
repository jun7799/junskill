# -*- coding: utf-8 -*-
"""
插图生成脚本 - ModelScope API (异步模式)
Generate background illustrations using ModelScope API
"""
import sys
import os
import requests
import time
import json
from datetime import datetime

# ModelScope API 配置
BASE_URL = 'https://api-inference.modelscope.cn/'
# API Key 需通过环境变量或命令行参数提供
DEFAULT_API_KEY = os.getenv("MODELSCOPE_API_KEY", "")

COMMON_HEADERS = {
    "Content-Type": "application/json",
}


def generate_image(prompt: str, output_path: str, api_key: str = None, model: str = "Tongyi-MAI/Z-Image-Turbo"):
    """
    生成背景插图（异步模式）

    Args:
        prompt: 图片提示词
        output_path: 输出PNG路径
        api_key: ModelScope API Key (可选，默认使用内置key)
        model: 使用的模型 (默认: Tongyi-MAI/Z-Image-Turbo)
    """
    # API Key 优先级：命令行参数 > 环境变量 > 默认值
    api_key = api_key or os.getenv("MODELSCOPE_API_KEY", DEFAULT_API_KEY)

    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    headers = {
        **COMMON_HEADERS,
        "Authorization": f"Bearer {api_key}",
        "X-ModelScope-Async-Mode": "true",
    }

    payload = {
        "model": model,
        "prompt": prompt
    }

    try:
        # 提交任务
        print(f"[INFO] Submitting image generation task...")
        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
        )
        response.raise_for_status()

        task_id = response.json()["task_id"]
        print(f"[INFO] Task ID: {task_id}")

        # 轮询任务状态
        while True:
            result = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers={
                    **COMMON_HEADERS,
                    "Authorization": f"Bearer {api_key}",
                    "X-ModelScope-Task-Type": "image_generation",
                },
            )
            result.raise_for_status()
            data = result.json()

            task_status = data.get("task_status", "")

            if task_status == "SUCCEED":
                # 下载图片
                image_url = data["output_images"][0]
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(img_response.content)

                print(f"[OK] Image saved: {output_path}")
                return output_path

            elif task_status == "FAILED":
                print(f"[ERROR] Image generation failed: {data}")
                return None

            elif task_status == "RUNNING":
                print(f"[INFO] Task running... waiting 5s")
                time.sleep(5)

            else:
                print(f"[INFO] Task status: {task_status}, waiting 5s")
                time.sleep(5)

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP Error: {e}")
        print(f"[ERROR] Response: {e.response.text if e.response else 'No response'}")
        return None
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_image.py <prompt> <output_path> [api_key] [model]")
        print("")
        print("Examples:")
        print('  python generate_image.py "Ancient Chinese battlefield" output.png')
        print('  python generate_image.py "A golden cat" cat.png "" "Tongyi-MAI/Z-Image-Turbo"')
        print("")
        print("Models:")
        print("  - Tongyi-MAI/Z-Image-Turbo (default, fast)")
        print("  - flux-schnell")
        print("  - stabilityai/stable-diffusion-3-medium")
        print("")
        print("API Key: Uses built-in key by default, or set MODELSCOPE_API_KEY env var")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2]
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    model = sys.argv[4] if len(sys.argv) > 4 else "Tongyi-MAI/Z-Image-Turbo"

    generate_image(prompt, output_path, api_key, model)


if __name__ == "__main__":
    main()
