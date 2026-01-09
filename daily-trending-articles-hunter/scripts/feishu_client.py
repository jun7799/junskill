#!/usr/bin/env python3
"""
每日热门文章猎手 - 飞书多维表格API客户端

功能：
1. 认证管理（tenant_access_token）
2. 创建/获取多维表格
3. 批量写入记录（支持去重）
4. 字段映射和数据类型转换

依赖：pip install lark-oapi
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from lark_oapi import Client
    from lark_oapi.api.auth.v3 import CreateTenantAccessTokenRequest
    from lark_oapi.api.bitable.v1 import (
        BatchCreateAppTableRecordRequest,
        SearchAppTableRecordRequest,
        UpdateAppTableRecordRequest,
        ListAppTableFieldRequest
    )
except ImportError:
    print("警告: 未安装 lark-oapi，请运行: pip install lark-oapi")
    exit(1)

SCRIPT_DIR = Path(__file__).parent


class FeishuBitableClient:
    """飞书多维表格客户端"""

    def __init__(self, app_id: str, app_secret: str, app_token: str, table_id: str):
        """
        初始化飞书客户端

        Args:
            app_id: 飞书应用的 App ID
            app_secret: 飞书应用的 App Secret
            app_token: 多维表格的 App Token
            table_id: 数据表格的 Table ID
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id

        # 创建客户端
        self.client = Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .build()

        self._tenant_access_token = None
        # 初始化时获取表格字段信息
        self._table_fields_cache = None

    def get_table_fields(self) -> Optional[Dict]:
        """获取表格字段信息，用于调试"""
        print("\n  正在获取表格字段信息...")
        try:
            # 注意：飞书SDK的字段列表API可能需要不同路径
            # 这里尝试使用简化方式获取
            request = ListAppTableFieldRequest.builder() \
                .app_token(self.app_token) \
                .table_id(self.table_id) \
                .build()

            response = self.client.bitable.v1.app_table_field.list(request)

            if response.success() and hasattr(response.data, 'items'):
                print("\n  表格字段列表:")
                for field in response.data.items:
                    print(f"    - {field.field_name} ({field.field_type_name})")
                return response.data.items

        except Exception as e:
            print(f"\n  获取字段信息失败: {e}")
            print("\n  请手动检查飞书表格的字段名称是否与以下配置一致:")
            print("    - 标题 (text)")
            print("    - 链接 (url)")
            print("    - 来源 (single_select)")
            print("    - 热度分数 (number)")

        return None

    def get_tenant_access_token(self) -> str:
        """获取 tenant_access_token 用于API调用"""
        if self._tenant_access_token:
            return self._tenant_access_token

        request = CreateTenantAccessTokenRequest.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .build()

        response = self.client.auth.v3.tenant_access_token.create(request)

        if not response.success():
            raise Exception(f"获取 tenant_access_token 失败: {response.msg}")

        self._tenant_access_token = response.data.tenant_access_token
        return self._tenant_access_token

    def article_to_record(self, article: Dict) -> Dict:
        """
        将文章数据转换为飞书记录格式

        字段映射：
        - 标题 -> text
        - 链接 -> url (需要使用对象格式: {"link": "https://..."})
        - 来源 -> single_select (需要传递选项ID)
        - 热度分数 -> number
        """
        # 来源字段的选项映射
        source_options = {
            "公众号": "optp8Kzrvf",
            "HackerNews": "optO6wj2Xr",
            "dev.to": "optOdV3HeY",
            "掘金": "optFOZBC6e"
        }

        source = article.get("source", "")
        source_option_id = source_options.get(source, "optO6wj2Xr")  # 默认HackerNews

        record = {
            "fields": {
                "标题": article.get("title", "")[:200],  # 限制长度避免溢出
                "链接": {"link": article.get("url", "")},  # URL字段需要对象格式
                "来源": source_option_id,  # 单选字段需要选项ID
                "热度分数": float(article.get("trending_score", 0)),  # 确保是数字类型
            }
        }

        return record

    def check_duplicate(self, url: str) -> Optional[Dict]:
        """
        检查文章是否已存在（基于URL去重）

        返回已存在的记录，如果不存在则返回None

        注意：当前版本简化实现，暂时跳过去重检查
        TODO: 实现基于URL的去重功能
        """
        # 暂时跳过去重，让数据先写入
        # 如果需要去重，可以使用 AppTableRecord.list() 获取所有记录后本地去重
        return None

    def create_records(self, articles: List[Dict], skip_duplicate: bool = True) -> Dict:
        """
        批量创建记录

        Args:
            articles: 文章列表
            skip_duplicate: 是否跳过重复记录

        Returns:
            创建结果统计
        """
        # 先获取字段信息（调试用）
        self.get_table_fields()

        results = {
            "success": 0,
            "duplicate": 0,
            "failed": 0,
            "errors": []
        }

        # 飞书API限制每次最多500条记录
        batch_size = 500

        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            records_to_create = []

            for article in batch:
                # 检查重复
                if skip_duplicate:
                    duplicate = self.check_duplicate(article.get("url", ""))
                    if duplicate:
                        results["duplicate"] += 1
                        continue

                # 转换为记录格式
                record = self.article_to_record(article)
                records_to_create.append(record)

            # 批量创建
            if records_to_create:
                # 调试：打印第一个记录的字段
                if i == 0 and records_to_create:
                    print("\n  调试-第一个记录结构:")
                    print(json.dumps(records_to_create[0], indent=2, ensure_ascii=False)[:500])

                request = BatchCreateAppTableRecordRequest.builder() \
                    .app_token(self.app_token) \
                    .table_id(self.table_id) \
                    .request_body({"records": records_to_create}) \
                    .build()

                response = self.client.bitable.v1.app_table_record.batch_create(request)

                if response.success():
                    results["success"] += len(records_to_create)
                    print(f"  -> 成功写入 {len(records_to_create)} 条记录")
                else:
                    # 调试：打印详细的错误信息
                    error_details = str(response.msg)
                    if hasattr(response, 'code'):
                        error_details += f" (code: {response.code})"

                    results["failed"] += len(records_to_create)
                    results["errors"].append({
                        "batch": i // batch_size + 1,
                        "error": error_details
                    })
                    print(f"  -> 写入失败: {error_details}")

        return results

    def update_existing_records(self, articles: List[Dict]) -> Dict:
        """
        更新已存在的记录（如果有更新的数据）

        用于定时任务中更新热度分数等动态数据
        """
        results = {
            "updated": 0,
            "not_found": 0,
            "failed": 0
        }

        for article in articles:
            url = article.get("url", "")
            duplicate = self.check_duplicate(url)

            if duplicate:
                # 更新热度分数
                record_id = duplicate["record_id"]
                new_score = article.get("trending_score", 0)

                request = UpdateAppTableRecordRequest.builder() \
                    .app_token(self.app_token) \
                    .table_id(self.table_id) \
                    .record_id(record_id) \
                    .fields({"热度分数": new_score}) \
                    .build()

                response = self.client.bitable.v1.app_table_record.update(request)

                if response.success():
                    results["updated"] += 1
                else:
                    results["failed"] += 1
            else:
                results["not_found"] += 1

        return results

    def print_summary(self, results: Dict):
        """打印操作摘要"""
        print("\n飞书表格操作摘要:")
        print(f"  成功: {results.get('success', 0)}")
        print(f"  跳过重复: {results.get('duplicate', 0)}")
        print(f"  失败: {results.get('failed', 0)}")

        if results.get("errors"):
            print(f"\n错误详情:")
            for error in results["errors"]:
                print(f"  批次 {error['batch']}: {error['error']}")


def load_config(config_path: str = None) -> Dict:
    """加载配置文件"""
    if config_path is None:
        config_path = SCRIPT_DIR.parent / "assets" / "config.json"

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def load_articles(input_path: str = None) -> List[Dict]:
    """加载计算热度的文章数据"""
    if input_path is None:
        input_path = SCRIPT_DIR.parent / "data" / "articles_scored.json"

    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


if __name__ == "__main__":
    # 加载配置和数据
    config = load_config()
    articles = load_articles()

    if not articles:
        print("没有找到文章数据，请先运行 calculate_trending.py")
        exit(1)

    # 从配置或环境变量获取飞书凭证
    feishu_config = config.get("feishu", {})
    app_id = os.getenv("FEISHU_APP_ID", feishu_config.get("app_id", "").replace("${FEISHU_APP_ID}", ""))
    app_secret = os.getenv("FEISHU_APP_SECRET", feishu_config.get("app_secret", "").replace("${FEISHU_APP_SECRET}", ""))
    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN", feishu_config.get("bitable_app_token", "").replace("${FEISHU_BITABLE_APP_TOKEN}", ""))
    table_id = os.getenv("FEISHU_TABLE_ID", feishu_config.get("table_id", "").replace("${FEISHU_TABLE_ID}", ""))

    if not all([app_id, app_secret, app_token, table_id]):
        print("\n错误: 飞书配置不完整")
        print("请在 config.json 中配置飞书凭证，或设置以下环境变量:")
        print("  FEISHU_APP_ID")
        print("  FEISHU_APP_SECRET")
        print("  FEISHU_BITABLE_APP_TOKEN")
        print("  FEISHU_TABLE_ID")
        print("\n飞书应用创建指南: https://open.feishu.cn/document/server-docs/authorization-management/access-token/create-app")
        exit(1)

    try:
        # 创建客户端并写入数据
        print("正在连接飞书多维表格...")
        client = FeishuBitableClient(app_id, app_secret, app_token, table_id)

        print(f"准备写入 {len(articles)} 篇文章...")
        results = client.create_records(articles, skip_duplicate=True)
        client.print_summary(results)

        print("\n数据写入完成!")

    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请检查:")
        print("1. 飞书应用配置是否正确")
        print("2. 多维表格是否存在且字段名称正确")
        print("3. 网络连接是否正常")
        exit(1)
