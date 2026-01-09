#!/usr/bin/env python3
"""
Save article to Feishu Bitable

Usage:
    python save_to_feishu.py --title "标题" --url "链接" --keywords "关键词1,关键词2" --summary "摘要" --platform "平台" --author "作者"

Requirements:
    - requests: pip install requests
"""

import argparse
import json
import sys
import io
from typing import Optional

# FIX: Force UTF-8 encoding for output to avoid Windows GBK encoding errors
# Windows console defaults to GBK, which cannot handle emoji/special characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Feishu Configuration
FEISHU_CONFIG = {
    "app_id": "cli_a9c593c3f6e15cb6",
    "app_secret": "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ",
    "base_id": "XGqVbRXijaegF0ssTFCcTQ68nRd",
    "table_id": "tblYY3JCuszQJ0Pb",
}


def get_tenant_access_token(app_id: str, app_secret: str) -> Optional[str]:
    """Get Feishu tenant access token."""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": app_id, "app_secret": app_secret}

    try:
        import requests
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 0:
            return result.get("tenant_access_token")
        else:
            print(f"Error getting token: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None


def save_to_feishu(
    title: str,
    url: str,
    keywords: list,
    summary: str,
    platform: str,
    author: str = "",
    publish_time: str = ""
) -> bool:
    """
    Save article to Feishu Bitable.

    Args:
        title: Article title
        url: Article URL
        keywords: List of keywords
        summary: Article summary in markdown format
        platform: Source platform
        author: Article author (optional)
        publish_time: Article publish time (optional)

    Returns:
        True if successful, False otherwise
    """
    # Get tenant access token
    token = get_tenant_access_token(
        FEISHU_CONFIG["app_id"],
        FEISHU_CONFIG["app_secret"]
    )

    if not token:
        print("Failed to get access token")
        return False

    # Prepare record data
    # Note: Feishu Link type fields require object format: {"link": "url"}
    fields = {
        "文章标题": title,
        "文章链接": {"link": url},
        "文章主题关键词": keywords,
        "文章梗概": summary,  # 支持markdown格式
        "来源平台": platform,
    }

    if author:
        fields["作者"] = author

    if publish_time:
        # Convert to integer (Feishu Date field requires milliseconds timestamp)
        try:
            timestamp = int(publish_time)
            # If timestamp is in seconds (less than 10000000000), convert to milliseconds
            if timestamp < 10000000000:
                timestamp = timestamp * 1000
            fields["发布时间"] = timestamp
        except ValueError:
            # If not a number, try to parse as date string
            import datetime
            # Try common date formats
            for fmt in ["%Y年%m月%d日", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    dt = datetime.datetime.strptime(publish_time.split()[0], fmt)
                    # Convert to milliseconds
                    fields["发布时间"] = int(dt.timestamp() * 1000)
                    break
                except:
                    continue

    # Create record
    api_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_CONFIG['base_id']}/tables/{FEISHU_CONFIG['table_id']}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"fields": fields}

    try:
        import requests
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 0:
            print(f"Successfully saved to Feishu!")
            print(f"  Record ID: {result.get('data', {}).get('record', {}).get('record_id')}")
            return True
        else:
            print(f"Error saving record: {result.get('msg')}")
            print(f"Full response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False

    except Exception as e:
        print(f"Error saving to Feishu: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Save article to Feishu Bitable")
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--url", required=True, help="Article URL")
    parser.add_argument("--keywords", required=True, help="Comma-separated keywords")
    parser.add_argument("--summary", required=True, help="Article summary in markdown format")
    parser.add_argument("--platform", required=True, help="Source platform")
    parser.add_argument("--author", default="", help="Article author (optional)")
    parser.add_argument("--publish-time", default="", help="Article publish time (optional)")

    args = parser.parse_args()

    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    # Validate
    if not keywords:
        print("Error: At least one keyword is required")
        sys.exit(1)

    # Save to Feishu
    success = save_to_feishu(
        title=args.title,
        url=args.url,
        keywords=keywords,
        summary=args.summary,
        platform=args.platform,
        author=args.author,
        publish_time=args.publish_time
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
