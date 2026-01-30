# -*- coding: utf-8 -*-
"""
智能BGM选择脚本
Intelligent BGM selection based on style and content keywords
"""
import json
import os
import random


def load_bgm_metadata(bgm_dir: str) -> dict:
    """加载BGM元数据"""
    meta_file = os.path.join(bgm_dir, "bgm_meta.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"music_library": [], "style_recommendations": {}}


def select_bgm_by_style(
    bgm_dir: str,
    style: str = "xiaobian",
    keywords: list = None
) -> str:
    """
    根据风格和关键词智能选择BGM

    Args:
        bgm_dir: BGM目录
        style: 视频风格 (xiaobian/dan_koe/tech/lifestyle/chinese/auto)
        keywords: 内容关键词列表

    Returns:
        选择的BGM文件名
    """
    meta = load_bgm_metadata(bgm_dir)

    if not meta["music_library"]:
        print("[WARN] No BGM metadata found, using random selection")
        return None

    # 1. 优先根据风格推荐
    style_key = {
        "xiaobian": "xiaobian",
        "小编": "xiaobian",
        "dan_koe": "dan_koe",
        "dan koe": "dan_koe",
        "tech": "tech",
        "科技": "tech",
        "technology": "tech",
        "lifestyle": "lifestyle",
        "生活": "lifestyle",
        "chinese": "chinese",
        "中国": "chinese",
        "chinese_new_year": "chinese",
    }.get(style.lower(), "xiaobian")

    recommendations = meta["style_recommendations"].get(style_key, {})
    recommended_tracks = recommendations.get("recommendations", [])
    fallback_track = recommendations.get("fallback")

    # 2. 如果有关键词，尝试关键词匹配
    if keywords:
        for track in meta["music_library"]:
            track_file = track["filename"]
            suitable_keywords = track.get("suitable_for", [])
            # 检查关键词匹配
            for kw in keywords:
                if any(kw.lower() in str(sk).lower() for sk in suitable_keywords):
                    if os.path.exists(os.path.join(bgm_dir, track_file)):
                        print(f"[INFO] Selected by keyword '{kw}': {track['title']}")
                        return track_file

    # 3. 使用风格推荐的BGM
    for track_name in recommended_tracks:
        track_path = os.path.join(bgm_dir, track_name)
        if os.path.exists(track_path):
            print(f"[INFO] Selected by style '{style}': {track_name}")
            return track_name

    # 4. 使用fallback
    if fallback_track and os.path.exists(os.path.join(bgm_dir, fallback_track)):
        print(f"[INFO] Using fallback: {fallback_track}")
        return fallback_track

    # 5. 随机选择一个存在的
    existing = [t["filename"] for t in meta["music_library"]
                if os.path.exists(os.path.join(bgm_dir, t["filename"]))]
    if existing:
        selected = random.choice(existing)
        print(f"[INFO] Random selection: {selected}")
        return selected

    return None


def list_available_bgm(bgm_dir: str) -> list:
    """列出所有可用的BGM"""
    meta = load_bgm_metadata(bgm_dir)
    available = []

    for track in meta["music_library"]:
        track_path = os.path.join(bgm_dir, track["filename"])
        if os.path.exists(track_path):
            available.append(track)

    return available


def print_bgm_catalog(bgm_dir: str):
    """打印BGM目录"""
    available = list_available_bgm(bgm_dir)

    print("\n=== 可用BGM目录 ===\n")

    for track in available:
        print(f"【{track['title']}】")
        print(f"  文件: {track['filename']}")
        print(f"  风格: {track.get('style', 'N/A')}")
        print(f"  情绪: {track.get('mood', 'N/A')}")
        print(f"  适用: {', '.join(track.get('suitable_for', ['N/A']))}")
        print(f"  能量: {track.get('energy', 'N/A')}")
        print()


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python select_bgm.py <bgm_dir> [style] [keywords...]")
        print("")
        print("Examples:")
        print('  python select_bgm.py "D:\\资源\\bgm" xiaobian')
        print('  python select_bgm.py "D:\\资源\\bgm" dan_koe "科技" "成长"')
        print('  python select_bgm.py "D:\\资源\\bgm" list')
        sys.exit(1)

    bgm_dir = sys.argv[1]

    if sys.argv[2] == "list":
        print_bgm_catalog(bgm_dir)
    else:
        style = sys.argv[2] if len(sys.argv) > 2 else "xiaobian"
        keywords = sys.argv[3:] if len(sys.argv) > 3 else None

        result = select_bgm_by_style(bgm_dir, style, keywords)

        if result:
            print(f"\n[SELECTED] {result}")
            print(f"[FULL_PATH] {os.path.join(bgm_dir, result)}")
        else:
            print("[ERROR] No suitable BGM found")


if __name__ == "__main__":
    main()
