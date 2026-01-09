#!/usr/bin/env python3
"""
飞书多维表上传脚本

功能：
1. 读取推文JSON数据
2. 调用AI生成推文主题、关键词、梗概
3. 上传到飞书多维表
"""

import json
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class FeishuUploader:
    """飞书多维表上传器"""

    def __init__(self, config_path: str = None):
        """
        初始化上传器

        Args:
            config_path: 配置文件路径，默认为 config.json
        """
        # 读取配置文件
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir / "config.json"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.feishu_config = self.config['feishu']
        self.collection_config = self.config['collection']
        self.ai_config = self.config.get('ai_api', {})

        # 初始化AI客户端
        self.ai_client = None
        if self.ai_config.get('api_key') and HAS_ANTHROPIC:
            self.ai_client = anthropic.Anthropic(
                api_key=self.ai_config['api_key'],
                base_url=self.ai_config.get('base_url')
            )

        # 飞书API相关
        self.app_access_token = None
        self.tenant_access_token = None

        # 字段映射
        self.fields = self.feishu_config['field_names']

    def get_tenant_access_token(self) -> str:
        """
        获取 tenant_access_token

        Returns:
            str: tenant_access_token
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.feishu_config['app_id'],
            "app_secret": self.feishu_config['app_secret']
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if data.get('code') != 0:
            raise Exception(f"获取tenant_access_token失败: {data.get('msg')}")

        self.tenant_access_token = data.get('tenant_access_token')
        return self.tenant_access_token

    def summarize_tweet(self, tweet_text: str, author: str) -> Dict[str, str]:
        """
        使用AI总结推文（生成主题、关键词、梗概）

        Args:
            tweet_text: 推文内容
            author: 作者

        Returns:
            dict: 包含推文主题、关键词、推文梗概的字典
        """
        # 处理空内容推文（纯图片/视频/表情）
        if not tweet_text or not tweet_text.strip():
            print(f"[INFO] @{author} 的推文无文字内容，使用媒体推文模板")
            return {
                "推文主题": f"@{author} 的媒体推文",
                "关键词": "图片,视频,媒体",
                "推文梗概": "这是一条仅包含图片、视频或表情的推文，无文字内容"
            }

        if not self.ai_client:
            print("[WARN] AI客户端未配置，使用占位符数据")
            return {
                "推文主题": f"@{author} 的推文",
                "关键词": "",
                "推文梗概": tweet_text[:200]
            }

        try:
            prompt = f"""请为以下推文生成总结，以JSON格式返回：

推文内容：{tweet_text}
作者：@{author}

请生成：
1. 推文主题：一句话概括这条推文的核心主题（不超过20字）
2. 关键词：提取3个最相关的关键词，用逗号分隔
3. 推文梗概：用50-100字总结推文内容

只返回JSON格式，不要有其他内容：
{{
  "theme": "推文主题",
  "keywords": "关键词1,关键词2,关键词3",
  "summary": "推文梗概"
}}
"""

            response = self.ai_client.messages.create(
                model="glm-4.7",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result_text = response.content[0].text

            # 尝试解析JSON - 移除可能的markdown代码块标记
            try:
                # 移除 ```json 和 ``` 标记
                clean_text = result_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.startswith('```'):
                    clean_text = clean_text[3:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()

                ai_result = json.loads(clean_text)
                return {
                    "推文主题": ai_result.get("theme", ""),
                    "关键词": ai_result.get("keywords", ""),
                    "推文梗概": ai_result.get("summary", tweet_text[:200])
                }
            except json.JSONDecodeError:
                print(f"[WARN] AI返回不是有效JSON: {result_text}")
                return {
                    "推文主题": f"@{author} 的推文",
                    "关键词": "",
                    "推文梗概": tweet_text[:200]
                }

        except Exception as e:
            print(f"[WARN] AI调用失败: {e}")
            return {
                "推文主题": f"@{author} 的推文",
                "关键词": "",
                "推文梗概": tweet_text[:200]
            }

    def format_tweet_for_feishu(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        将推文数据格式化为飞书多维表记录格式

        Args:
            tweet: 推文数据字典

        Returns:
            dict: 飞书多维表记录格式
        """
        # 获取推文文本
        tweet_text = tweet.get('text', '')
        author = tweet.get('username', '')
        tweet_url = tweet.get('url', '')

        # AI总结（主题、关键词、梗概）
        summary = self.summarize_tweet(tweet_text, author)

        # 格式化时间 - 飞书需要毫秒级时间戳（数字）
        formatted_time = tweet.get('tweetTime', 0)

        # 构建记录
        record = {
            "fields": {
                self.fields['推文链接']: {"link": tweet_url},
                self.fields['发布时间']: formatted_time,
                self.fields['推文梗概']: summary['推文梗概'],
                self.fields['作者']: author,
                self.fields['点赞数']: tweet.get('likes', 0),
                self.fields['评论数']: tweet.get('replies', 0),
                self.fields['转发量']: tweet.get('retweets', 0),
                self.fields['阅读量']: tweet.get('views', 0),
            }
        }

        # 如果AI生成了主题和关键词，也添加进去
        if summary['推文主题']:
            record['fields'][self.fields['推文主题']] = summary['推文主题']
        if summary['关键词']:
            # 关键词需要是数组格式，AI返回的是逗号分隔的字符串
            keywords_list = [k.strip() for k in summary['关键词'].split(',') if k.strip()]
            record['fields'][self.fields['关键词']] = keywords_list

        return record

    def upload_tweets(self, tweets_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传推文到飞书多维表

        Args:
            tweets_data: 推文数据字典，包含 tweets 数组

        Returns:
            dict: 上传结果
        """
        # 获取token
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        # 获取推文列表
        tweets = tweets_data.get('tweets', [])
        if not tweets:
            return {
                'success': False,
                'message': '没有推文数据',
                'uploaded': 0
            }

        # 飞书API端点
        base_url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
        url = f"{base_url}/{self.feishu_config['base_id']}/tables/{self.feishu_config['table_id']}/records/batch_create"

        # 请求头
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        # 格式化推文数据
        records = []
        for tweet in tweets:
            record = self.format_tweet_for_feishu(tweet)
            records.append(record)

        # 请求体
        payload = {
            "records": records
        }

        # 发送请求
        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

            if result.get('code') == 0:
                return {
                    'success': True,
                    'message': '上传成功',
                    'uploaded': len(records),
                    'details': result
                }
            else:
                return {
                    'success': False,
                    'message': f"上传失败: {result.get('msg')}",
                    'uploaded': 0,
                    'details': result
                }

        except Exception as e:
            return {
                'success': False,
                'message': f"上传出错: {str(e)}",
                'uploaded': 0
            }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python feishu_uploader.py <tweets_data.json>")
        print("示例: python feishu_uploader.py temp_tweets.json")
        sys.exit(1)

    # 读取推文数据
    input_file = sys.argv[1]
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 '{input_file}' 不存在")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}")
        sys.exit(1)

    # 创建上传器
    uploader = FeishuUploader()

    # 上传推文
    try:
        result = uploader.upload_tweets(tweets_data)

        if result['success']:
            print(f"[OK] {result['message']}")
            print(f"[INFO] 成功上传 {result['uploaded']} 条推文到飞书多维表")
        else:
            print(f"[ERROR] {result['message']}")
            if 'details' in result:
                print(f"详情: {result['details']}")

    except Exception as e:
        print(f"[ERROR] 上传失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
