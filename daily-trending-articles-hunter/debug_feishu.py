#!/usr/bin/env python3
"""
调试飞书API - 查看详细错误信息
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from lark_oapi import Client
    from lark_oapi.api.auth.v3 import CreateTenantAccessTokenRequest
    from lark_oapi.api.bitable.v1 import CreateAppTableRecordRequest
    print("[OK] SDK导入成功")
except Exception as e:
    print(f"[FAIL] SDK导入失败: {e}")
    sys.exit(1)

def main():
    print("飞书API调试工具")
    print("="*60)

    # 1. 测试认证
    print("\n[步骤1] 测试认证...")
    try:
        client = Client.builder() \
            .app_id("cli_a9c593c3f6e15cb6") \
            .app_secret("NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ") \
            .build()

        # 获取token
        request = CreateTenantAccessTokenRequest.builder() \
            .app_id("cli_a9c593c3f6e15cb6") \
            .app_secret("NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ") \
            .build()

        response = client.auth.v3.tenant_access_token.create(request)

        if response.success():
            token = response.data.tenant_access_token
            print(f"[OK] 认证成功")
            print(f"  Token: {token[:20]}...")
        else:
            print(f"[FAIL] 认证失败: {response.msg}")
            print(f"  错误详情: {response}")
            return False

    except Exception as e:
        print(f"[ERROR] 认证异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. 测试写入
    print("\n[步骤2] 测试写入...")
    try:
        test_record = {
            'fields': {
                '标题': '调试测试'
            }
        }

        print(f"测试数据: {test_record}")

        request = CreateAppTableRecordRequest.builder() \
            .app_token('JqCpwgydti3pH5kv8gEcS40knkf') \
            .table_id('tblOuJRnpMYG70bu') \
            .request_body({'records': [test_record]}) \
            .build()

        print("发送请求...")
        response = client.bitable.v1.app_table_record.create(request)

        print(f"\n响应状态: {'成功' if response.success() else '失败'}")
        print(f"响应消息: {response.msg}")
        print(f"响应代码: {getattr(response, 'code', 'N/A')}")
        print(f"响应对象: {response}")

        if hasattr(response, 'error'):
            print(f"\n错误详情: {response.error}")

        if hasattr(response, 'data'):
            print(f"\n响应数据: {response.data}")

        # 检查响应的所有属性
        print("\n[调试信息] 响应对象所有属性:")
        for attr in dir(response):
            if not attr.startswith('_'):
                try:
                    value = getattr(response, attr)
                    print(f"  {attr}: {value}")
                except:
                    print(f"  {attr}: <无法访问>")

        return response.success()

    except Exception as e:
        print(f"[ERROR] 写入异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 检查权限
    print("\n[步骤3] 检查应用权限...")
    print("请确认应用已开通以下权限：")
    print("  - bitable:app")
    print("  - bitable:app:readonly")
    print("\n如果权限不足，请在飞书开放平台添加")

    return False

if __name__ == "__main__":
    main()
