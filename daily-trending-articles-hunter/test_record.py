#!/usr/bin/env python3
"""
直接测试写入飞书记录，包含完整错误信息
"""

import requests
import json

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"
APP_TOKEN = "OA9fbxQgeapqa9skt98czcIpnFg"
TABLE_ID = "tblsSjLmqFCC1Aee"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    response = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["tenant_access_token"]
    return None

def test_write():
    token = get_token()
    if not token:
        print("无法获取token")
        return

    print(f"Token: {token[:20]}...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 测试1：只写标题
    print("\n=== 测试1：只写标题 ===")
    payload1 = {
        "records": [
            {
                "fields": {
                    "标题": "测试标题"
                }
            }
        ]
    }

    print(f"请求: {json.dumps(payload1, ensure_ascii=False, indent=2)}")
    response = requests.post(url, json=payload1, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"完整响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 测试2：写所有字段（单选用选项ID）
    print("\n=== 测试2：所有字段（单选ID）===")
    payload2 = {
        "records": [
            {
                "fields": {
                    "标题": "测试标题2",
                    "链接": "https://example.com",
                    "来源": "optO6wj2Xr",
                    "热度分数": 85.5
                }
            }
        ]
    }

    print(f"请求: {json.dumps(payload2, ensure_ascii=False, indent=2)}")
    response = requests.post(url, json=payload2, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"完整响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    # 测试3：写所有字段（单选用文本）
    print("\n=== 测试3：所有字段（单选文本）===")
    payload3 = {
        "records": [
            {
                "fields": {
                    "标题": "测试标题3",
                    "链接": "https://example.com",
                    "来源": "HackerNews",
                    "热度分数": 90.0
                }
            }
        ]
    }

    print(f"请求: {json.dumps(payload3, ensure_ascii=False, indent=2)}")
    response = requests.post(url, json=payload3, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"完整响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    test_write()
