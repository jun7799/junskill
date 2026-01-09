#!/usr/bin/env python3
"""
使用raw string测试飞书API
"""

import requests

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"
APP_TOKEN = "OA9fbxQgeapqa9skt98czcIpnFg"
TABLE_ID = "tblsSjLmqFCC1Aee"

def get_token():
    response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    return response.json().get("tenant_access_token")

def test_raw():
    token = get_token()
    if not token:
        return

    print(f"Token: {token[:20]}...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 使用原始的JSON字符串
    raw_data = '{"records":[{"fields":{"标题":"测试文章","链接":"https://example.com","来源":"optO6wj2Xr","热度分数":85.5}}]}'

    print(f"\n发送原始JSON: {raw_data}")

    response = requests.post(url, data=raw_data.encode('utf-8'), headers=headers)

    print(f"\n状态码: {response.status_code}")
    print(f"响应: {response.text}")

if __name__ == "__main__":
    test_raw()
