#!/usr/bin/env python3
"""
最终测试 - 使用飞书官方SDK示例
参考: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from lark_oapi import Client
    from lark_oapi.api.bitable.v1 import CreateAppTableRecordRequest
    print("[OK] SDK导入成功")
except Exception as e:
    print(f"[FAIL] SDK导入失败: {e}")
    sys.exit(1)

def main():
    print("最终测试 - 飞书多维表格写入")
    print("="*60)

    # 1. 创建客户端
    print("\n[1] 创建客户端...")
    client = Client.builder() \
        .app_id("cli_a9c593c3f6e15cb6") \
        .app_secret("NeDneMgPLjFLGtlvHQaQCcOo2FBso0WQ") \
        .build()

    # 2. 构建请求
    print("\n[2] 构建请求...")
    request = CreateAppTableRecordRequest.builder() \
        .app_token("OA9fbxQgeapqa9skt98czcIpnFg") \
        .table_id("tblsSjLmqFCC1Aee") \
        .request_body(
            CreateAppTableRecordRequest.builder()
            .records([
                AppTableRecord.builder()
                .fields({
                    "标题": "SDK测试文章",
                    "链接": "https://example.com/test",
                    "来源": "optO6wj2Xr",  # HackerNews的选项ID
                    "热度分数": 90.5
                })
                .build()
            ])
            .build()
        ) \
        .build()

    # 3. 打印请求详情（调试用）
    print("\n请求详情:")
    print(f"  App Token: OA9fbxQgeapqa9skt98czcIpnFg")
    print(f"  Table ID: tblsSjLmqFCC1Aee")
    print(f"  记录: 标题=SDK测试文章, 来源=optO6wj2Xr")

    # 4. 发送请求
    print("\n[3] 发送请求...")
    response = client.bitable.v1.app_table_record.create(request)

    # 5. 处理响应
    print("\n[4] 响应结果:")
    print(f"  成功: {response.success()}")
    print(f"  消息: {response.msg}")

    if hasattr(response, 'code'):
        print(f"  代码: {response.code}")

    if response.success():
        print("\n[OK] 写入成功！")
        if hasattr(response, 'data') and response.data:
            print(f"  记录ID: {response.data.records[0].record_id}")
    else:
        print("\n[FAIL] 写入失败")
        if hasattr(response, 'error'):
            print(f"  错误: {response.error}")

        # 打印完整的响应对象
        print(f"\n  完整响应: {response}")

        if hasattr(response, 'raw'):
            print(f"  原始响应: {response.raw}")

if __name__ == "__main__":
    main()
