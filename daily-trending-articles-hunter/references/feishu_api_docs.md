# 飞书多维表格API文档参考

## 快速开始

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`

### 2. 配置权限

在应用权限管理中开通以下权限：

- `bitable:app`：查看、评论和创建多维表格
- `bitable:app:readonly`：只读权限

### 3. 获取多维表格信息

#### 获取 App Token

1. 打开目标多维表格
2. 从URL中获取：`https://example.feishu.cn/base/{APP_TOKEN}/...`

#### 获取 Table ID

1. 在多维表格中点击目标数据表
2. 从URL中获取表ID，或通过API获取所有数据表列表

## API 端点

### 认证

```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
```

### 创建记录

```
POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
```

### 搜索记录

```
POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search
```

### 更新记录

```
PUT https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
```

## SDK 使用

### 安装

```bash
pip install lark-oapi
```

### 基础用法

```python
from lark_oapi.api.bitable.v1 import *

# 创建客户端
client = Client.builder() \
    .app_id("app_id") \
    .app_secret("app_secret") \
    .build()

# 创建记录
request = CreateAppTableRecordRequest.builder() \
    .app_token("app_token") \
    .table_id("table_id") \
    .records([{
        "fields": {
            "标题": "文章标题",
            "链接": "https://example.com"
        }
    }]) \
    .build()

response = client.bitable.v1.app_table_record.create(request)
```

## 字段类型映射

| Python类型 | 飞书字段类型 | 示例 |
|-----------|-------------|------|
| str | text | `"文本内容"` |
| str | url | `"https://example.com"` |
| str | single_select | `"选项名称"` |
| list | multi_select | `[{"name": "选项1"}, {"name": "选项2"}]` |
| str | date | `"2024-01-01"` |
| int/float | number | `123` |

## 常见问题

### Q: 如何获取表格的 app_token 和 table_id？

A:
- `app_token`: 从多维表格URL中获取，格式为 `base/{app_token}/...`
- `table_id`: 可以通过API获取，或在开发者工具中查看

### Q: 为什么写入数据失败？

A: 检查以下几点：
1. 应用是否已开通相关权限
2. app_token 和 table_id 是否正确
3. 字段名称是否与表格中完全一致
4. 字段类型是否匹配

### Q: 如何处理批量写入的限流？

A: 飞书API限制每次最多500条记录，建议：
- 分批写入，每批不超过500条
- 添加请求间隔，避免触发限流
- 使用异步处理提高效率

## 相关链接

- [飞书开放平台文档](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/introduction)
- [Python SDK](https://github.com/larksuite/lark-oapi-python)
- [API 限流说明](https://open.feishu.cn/document/server-docs/docs/api-call-limit/rate-limit)
