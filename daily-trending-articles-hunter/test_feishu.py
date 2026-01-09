#!/usr/bin/env python3
"""
飞书API测试脚本 - 最简化测试
"""

import json
import sys
from pathlib import Path

# 添加脚本目录到Python路径
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from feishu_client import FeishuBitableClient
    from lark_oapi.api.bitable.v1 import CreateAppTableRecordRequest
    print("[OK] 模块导入成功")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

def test_connection():
    """测试连接"""
    print("\n" + "="*60)
    print("测试1: 创建飞书客户端")
    print("="*60)

    try:
        client = FeishuBitableClient(
            app_id='cli_a9c593c3f6e15cb6',
            app_secret='NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ',
            app_token='JqCpwgydti3pH5kv8gEcS40knkf',
            table_id='tblOuJRnpMYG70bu'
        )
        print("[OK] 客户端创建成功")
        return client
    except Exception as e:
        print(f"[FAIL] 客户端创建失败: {e}")
        return None

def test_write_single_field(client):
    """测试写入单字段"""
    print("\n" + "="*60)
    print("测试2: 写入单字段记录（只写'标题'）")
    print("="*60)

    # 测试记录 - 只包含标题
    test_record = {
        'fields': {
            '标题': '测试文章标题'
        }
    }

    print("测试数据:")
    print(json.dumps(test_record, indent=2, ensure_ascii=False))

    try:
        request = CreateAppTableRecordRequest.builder() \
            .app_token('JqCpwgydti3pH5kv8gEcS40knkf') \
            .table_id('tblOuJRnpMYG70bu') \
            .request_body({'records': [test_record]}) \
            .build()

        print("\n发送请求...")
        response = client.client.bitable.v1.app_table_record.create(request)

        if response.success():
            print("[OK] 写入成功！")
            print(f"  记录ID: {response.data.records[0].record_id if hasattr(response.data, 'records') else 'unknown'}")
        else:
            print(f"[FAIL] 写入失败: {response.msg}")
            if hasattr(response, 'code'):
                print(f"  错误代码: {response.code}")
            if hasattr(response, 'data'):
                print(f"  响应数据: {response.data}")

        return response.success()

    except Exception as e:
        print(f"[FAIL] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_write_all_fields(client):
    """测试写入所有字段"""
    print("\n" + "="*60)
    print("测试3: 写入所有字段")
    print("="*60)

    test_article = {
        "title": "测试文章标题",
        "url": "https://example.com/test",
        "source": "HackerNews",
        "trending_score": 85.5
    }

    record = client.article_to_record(test_article)

    print("转换后的记录:")
    print(json.dumps(record, indent=2, ensure_ascii=False))

    try:
        request = CreateAppTableRecordRequest.builder() \
            .app_token('JqCpwgydti3pH5kv8gEcS40knkf') \
            .table_id('tblOuJRnpMYG70bu') \
            .request_body({'records': [record]}) \
            .build()

        print("\n发送请求...")
        response = client.client.bitable.v1.app_table_record.create(request)

        if response.success():
            print("[OK] 写入成功！")
        else:
            print(f"[FAIL] 写入失败: {response.msg}")
            if hasattr(response, 'code'):
                print(f"  错误代码: {response.code}")
            # 尝试获取更详细的错误信息
            if hasattr(response, 'error'):
                print(f"  详细错误: {response.error}")

        return response.success()

    except Exception as e:
        print(f"[FAIL] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试流程"""
    print("飞书API测试脚本")
    print("="*60)

    # 测试1: 连接
    client = test_connection()
    if not client:
        print("\n测试终止：无法创建客户端")
        return False

    # 测试2: 写入单字段
    success = test_write_single_field(client)
    if not success:
        print("\n单字段测试失败，停止后续测试")
        return False

    # 测试3: 写入所有字段
    success = test_write_all_fields(client)

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
