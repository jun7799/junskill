#!/usr/bin/env python3
"""
检查飞书应用权限
"""

import requests

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"

def check_permissions():
    """检查应用权限"""
    # 获取token
    token_response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )

    if token_response.status_code != 200:
        print("无法获取token")
        return

    token_data = token_response.json()
    if token_data.get("code") != 0:
        print(f"Token错误: {token_data}")
        return

    token = token_data["tenant_access_token"]
    print(f"Token: {token[:20]}...")

    # 检查应用权限
    headers = {"Authorization": f"Bearer {token}"}

    # 查看应用权限列表（如果API支持）
    print("\n=== 应用开通的权限 ===")

    # 尝试访问一个受保护的资源看是否成功
    test_urls = [
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/OA9fbxQgeapqa9skt98czcIpnFg/tables",
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/OA9fbxQgeapqa9skt98czcIpnFg/tables/tblsSjLmqFCC1Aee",
    ]

    for url in test_urls:
        print(f"\n测试访问: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('msg', 'unknown')}")
        elif response.status_code == 400:
            data = response.json()
            print(f"失败: {json.dumps(data, ensure_ascii=False, indent=2)}")
        elif response.status_code == 403:
            print(f"权限不足: {response.text}")

if __name__ == "__main__":
    import json
    check_permissions()
