#!/usr/bin/env python3
"""
直接使用HTTP请求，打印完整请求和响应
"""

import requests
import json
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"
APP_TOKEN = "OA9fbxQgeapqa9skt98czcIpnFg"
TABLE_ID = "tblsSjLmqFCC1Aee"

def get_token():
    """获取token"""
    print("\n[1] 获取Access Token...")
    response = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    print(f"Token请求状态码: {response.status_code}")
    print(f"Token响应: {response.text}")

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            token = data["tenant_access_token"]
            print(f"\n[OK] Token获取成功: {token[:20]}...")
            return token
    return None

def write_record():
    """写入记录"""
    token = get_token()
    if not token:
        print("[FAIL] 无法获取Token")
        return False

    print("\n[2] 写入测试记录...")

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 请求体
    data = {
        "records": [
            {
                "fields": {
                    "标题": "直接API测试",
                    "链接": "https://example.com",
                    "来源": "optO6wj2Xr",
                    "热度分数": 88.8
                }
            }
        ]
    }

    print(f"请求URL: {url}")
    print(f"请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
    print(f"请求体: {json.dumps(data, ensure_ascii=False, indent=2)}")

    # 为了能够捕获详细的请求信息，我们手动构建请求
    print("\n发送请求中...")

    # 使用requests的Session来捕获更详细的调试信息
    session = requests.Session()

    # 准备请求
    req = requests.Request('POST', url, json=data, headers=headers)
    prepared = req.prepare()

    print("\n[调试] 准备的请求:")
    print(f"  方法: {prepared.method}")
    print(f"  URL: {prepared.url}")
    print(f"  头: {dict(prepared.headers)}")
    if prepared.body:
        print(f"  体: {prepared.body[:500]}")

    # 发送请求
    response = session.send(prepared)

    print("\n[3] 响应结果:")
    print(f"  状态码: {response.status_code}")
    print(f"  响应头: {dict(response.headers)}")
    print(f"  响应体: {response.text}")

    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            print("\n[OK] 写入成功！")
            return True
        else:
            print(f"\n[FAIL] 写入失败: {result}")
            return False
    else:
        print(f"\n[FAIL] HTTP错误: {response.status_code}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("直接API测试 - 显示完整请求/响应")
    print("="*60)

    success = write_record()

    print("\n" + "="*60)
    if success:
        print("[结果] 测试通过")
    else:
        print("[结果] 测试失败")
    print("="*60)
