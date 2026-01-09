#!/usr/bin/env python3
"""
检查飞书表格字段详细信息
"""

import requests
import json

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"
APP_TOKEN = "OA9fbxQgeapqa9skt98czcIpnFg"
TABLE_ID = "tblsSjLmqFCC1Aee"

def get_access_token():
    """获取access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data.get("tenant_access_token")
    return None

def check_fields():
    """检查表格字段"""
    token = get_access_token()
    if not token:
        print("无法获取token")
        return

    print(f"Token: {token[:20]}...")

    # 先检查表格
    table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(table_url, headers=headers)
    print(f"\n获取表格列表状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")

        # 获取字段
        fields_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
        response = requests.get(fields_url, headers=headers)
        print(f"\n获取字段状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"字段响应: {json.dumps(data, ensure_ascii=False, indent=2)}")

            if data.get("code") == 0:
                fields = data.get("data", {}).get("items", [])
                print("\n字段列表:")
                for field in fields:
                    print(f"  - {field.get('field_name', 'N/A')} (ID: {field.get('field_id', 'N/A')}, Type: {field.get('type', 'N/A')})")

if __name__ == "__main__":
    check_fields()
