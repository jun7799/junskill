#!/usr/bin/env python3
"""
测试不同的API版本和端点
"""

import requests
import json

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

def test_apis():
    token = get_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 测试1：使用 v1 版本
    print("\n=== 测试1: v1版本 ===")
    url1 = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    data1 = {"records": [{"fields": {"标题": "测试1"}}]}
    response = requests.post(url1, json=data1, headers=headers)
    print(f"URL: {url1}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

    # 测试2：不带 /bitable/
    print("\n=== 测试2: 不使用bitable路径 ===")
    url2 = f"https://open.feishu.cn/open-apis/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    response = requests.post(url2, json=data1, headers=headers)
    print(f"URL: {url2}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")

    # 测试3：使用旧的sheets API（如果这是电子表格）
    print("\n=== 测试3: sheets API ===")
    url3 = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{APP_TOKEN}/values_append"
    data3 = {"valueRange": {"range": "A1:B1", "values": [["测试", "数据"]]}}
    response = requests.post(url3, json=data3, headers=headers)
    print(f"URL: {url3}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")

if __name__ == "__main__":
    test_apis()
