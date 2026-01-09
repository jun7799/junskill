#!/usr/bin/env python3
"""
使用requests直接测试飞书API
绕过SDK，直接调用REST API
"""

import requests
import json

APP_ID = "cli_a9c593c3f6e15cb6"
APP_SECRET = "NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ"
APP_TOKEN = "JqCpwgydti3pH5kv8gEcS40knkf"
TABLE_ID = "tblOuJRnpMYG70bu"

def get_access_token():
    """获取access token"""
    print("\n[步骤1] 获取Access Token...")

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                token = data.get("tenant_access_token")
                print(f"\n[OK] 获取Token成功: {token[:20]}...")
                return token
            else:
                print(f"\n[FAIL] 获取Token失败: {data}")
                return None
        else:
            print(f"\n[FAIL] HTTP请求失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"\n[ERROR] 请求异常: {e}")
        return None

def write_record(token):
    """写入测试记录"""
    print("\n[步骤2] 写入测试记录...")

    # 使用App ID作为API路径
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 测试1：尝试英文字段名
    print("\n[测试1] 尝试英文字段名...")
    payload1 = {
        "records": [
            {
                "fields": {
                    "title": "API Test Article"
                }
            }
        ]
    }

    try:
        # 使用json参数发送，requests会自动设置Content-Type
        response = requests.post(url, json=payload1, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("[OK] 英文字段名成功！")
                return True
    except Exception as e:
        print(f"[ERROR] 英文字段测试异常: {e}")

    # 测试2：尝试中文字段名
    print("\n[测试2] 尝试中文字段名...")
    payload2 = {
        "records": [
            {
                "fields": {
                    "标题": "API测试文章"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload2, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("[OK] 写入成功！")
                return True
            else:
                print(f"[FAIL] 写入失败: {data}")
                if "msg" in data:
                    print(f"错误消息: {data['msg']}")
                return False
        else:
            print(f"[FAIL] HTTP请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
        return False

def check_table_fields(token):
    """检查表格字段信息"""
    print("\n[步骤3] 检查表格字段信息...")

    # 先检查表格是否存在
    table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # 检查表格
        response = requests.get(table_url, headers=headers)
        print(f"检查表格状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                table_info = data.get("data", {})
                print(f"\n[OK] 表格存在: {table_info.get('name', '未知')}")
            else:
                print(f"\n[FAIL] 表格不存在或无法访问: {data}")
                return None
        else:
            print(f"\n[FAIL] 表格检查HTTP失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return None

        # 然后获取字段
        fields_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"

        response = requests.get(fields_url, headers=headers)
        print(f"获取字段状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                fields = data.get("data", {}).get("items", [])
                print("\n[OK] 获取字段信息成功:")
                for field in fields:
                    field_name = field.get('field_name', 'N/A')
                    field_type = field.get('type', 'N/A')
                    print(f"  - {field_name} ({field_type})")
                return fields
            else:
                print(f"\n[FAIL] 获取字段失败: {data}")
                return None
        else:
            error_text = response.text[:500]
            print(f"\n[FAIL] 获取字段HTTP失败: {response.status_code}")
            print(f"响应: {error_text}")

            # 可能是权限问题
            if "91402" in error_text:
                print("\n[提示] 错误代码91402: 表格或字段可能不存在")
                print("请检查:")
                print("  1. App Token是否正确")
                print("  2. Table ID是否正确")
                print("  3. 应用是否有权限访问此表格")

            return None

    except Exception as e:
        print(f"\n[ERROR] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*60)
    print("飞书API测试 (使用requests)")
    print("="*60)

    # 1. 获取token
    token = get_access_token()
    if not token:
        print("\n[终止] 无法获取Token")
        return False

    # 2. 检查表格字段
    fields = check_table_fields(token)
    if fields:
        # 验证字段是否存在
        field_names = [f['field_name'] for f in fields]
        required_fields = ["标题", "链接", "来源", "热度分数"]
        print("\n[字段验证]:")
        for rf in required_fields:
            if rf in field_names:
                field_type = next(f['type'] for f in fields if f['field_name'] == rf)
                print(f"  [OK] {rf} (类型: {field_type})")
            else:
                print(f"  [FAIL] 缺少字段: {rf}")

    # 3. 写入测试记录
    success = write_record(token)

    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
