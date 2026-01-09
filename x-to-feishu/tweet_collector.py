#!/usr/bin/env python3
"""
X/Twitter 推文采集脚本 - 使用 Playwright

功能：
1. 使用 Cookie 登录 X
2. 从 Feed 流滚动采集推文
3. 根据关键词过滤
4. 保存为 JSON 格式
"""

import json
import sys
import asyncio
import random
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urljoin

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def parse_cookie_file(cookie_path: str) -> str:
    """读取 cookie.txt 文件并返回 cookie 字符串"""
    with open(cookie_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 过滤掉空行和注释行
    cookie_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

    if not cookie_lines:
        raise ValueError('Cookie文件为空')

    # 如果有多行，用分号连接
    return '; '.join(cookie_lines)


def parse_time_ago(time_str: str) -> datetime:
    """解析相对时间字符串（如"2小时前"）返回 datetime"""
    now = datetime.now()
    time_str = time_str.lower().strip()

    # 处理各种时间格式
    if '小时前' in time_str or 'h' in time_str or 'hour' in time_str:
        hours = int(''.join(filter(str.isdigit, time_str)) or 0)
        return now - timedelta(hours=hours)
    elif '分钟前' in time_str or 'm' in time_str or 'min' in time_str:
        mins = int(''.join(filter(str.isdigit, time_str)) or 0)
        return now - timedelta(minutes=mins)
    elif '秒前' in time_str or 's' in time_str or 'sec' in time_str:
        secs = int(''.join(filter(str.isdigit, time_str)) or 0)
        return now - timedelta(seconds=secs)
    elif '天前' in time_str or 'd' in time_str or 'day' in time_str:
        days = int(''.join(filter(str.isdigit, time_str)) or 0)
        return now - timedelta(days=days)

    return now


def parse_views(view_str: str) -> int:
    """解析观看数字符串（如"1.2K"、"3.5万"）返回数字"""
    if not view_str:
        return 0

    view_str = view_str.replace(',', '').replace(' ', '').lower()

    if '万' in view_str:
        return int(float(view_str.replace('万', '')) * 10000)
    elif 'k' in view_str:
        return int(float(view_str.replace('k', '')) * 1000)
    elif 'm' in view_str:
        return int(float(view_str.replace('m', '')) * 1000000)

    return int(view_str) if view_str.isdigit() else 0


async def collect_tweets(
    cookie_string: str,
    keywords: list,
    target_count: int = 10,
    days_ago: int = 1,
    min_views: int = 100
) -> dict:
    """
    采集推文主函数

    Args:
        cookie_string: Cookie 字符串
        keywords: 关键词列表
        target_count: 目标采集数量
        days_ago: 采集几天内的推文
        min_views: 最小观看数

    Returns:
        dict: 包含推文列表和统计信息
    """

    if not HAS_PLAYWRIGHT:
        raise ImportError('需要安装 playwright: pip install playwright && playwright install chromium')

    tweets = []
    seen_tweet_ids = set()
    time_threshold = datetime.now() - timedelta(days=days_ago)

    print(f'[INFO] 开始采集推文...')
    print(f'[INFO] 关键词数量: {len(keywords)}')
    print(f'[INFO] 目标数量: {target_count}')
    print(f'[INFO] 时间范围: {days_ago}天内')
    print(f'[INFO] 最小观看数: {min_views}')

    async with async_playwright() as p:
        # 启动浏览器（使用系统安装的 Chrome）
        browser = await p.chromium.launch(
            channel="chrome",  # 使用系统 Chrome
            headless=False
        )
        context = await browser.new_context()

        # 设置 cookie
        cookies = []
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.x.com',
                    'path': '/'
                })

        await context.add_cookies(cookies)

        # 打开页面
        page = await context.new_page()
        await page.goto('https://x.com', wait_until='domcontentloaded', timeout=60000)

        # 刷新页面使 Cookie 生效
        await page.reload(wait_until='domcontentloaded', timeout=60000)

        # 等待页面完全加载
        await asyncio.sleep(5)

        print('[OK] 已登录 X')

        # 截图检查登录状态（调试用）
        try:
            await page.screenshot(path='debug_login.png', full_page=True)
            print('[INFO] 已保存登录状态截图 debug_login.png')
        except:
            pass

        # 调试：检查页面是否真的有推文
        await asyncio.sleep(3)
        articles = await page.query_selector_all('article[data-testid="tweet"]')
        print(f'[DEBUG] 页面上找到 {len(articles)} 个推文元素')

        if len(articles) == 0:
            print('[WARN] 没有找到推文元素，可能 Cookie 已过期或未登录')
            print('[INFO] 请检查 debug_login.png 截图确认登录状态')
            await browser.close()
            return {
                'collected': 0,
                'tweets': [],
                'error': 'No tweets found on page'
            }

        # 临时调试：获取第一条推文的内容
        try:
            first_text = await articles[0].query_selector('[data-testid="tweetText"]')
            if first_text:
                first_tweet_text = await first_text.inner_text()
                print(f'[DEBUG] 第一条推文内容: {first_tweet_text[:100]}...')
        except:
            pass

        # 收集推文
        scroll_attempts = 0
        max_scrolls = 30
        no_new_tweets_count = 0

        # 打印关键词列表用于调试
        print(f'[DEBUG] 关键词列表: {keywords[:5]}...')  # 只显示前5个

        while len(tweets) < target_count and scroll_attempts < max_scrolls:
            # 查找所有推文
            articles = await page.query_selector_all('article[data-testid="tweet"]')
            print(f'[DEBUG] 滚动 {scroll_attempts + 1}: 找到 {len(articles)} 个推文元素')

            new_count = 0
            parse_errors = 0
            skipped_keyword = 0
            skipped_time = 0

            for article in articles:
                try:
                    # 获取推文 ID
                    time_elem = await article.query_selector('time')
                    if not time_elem:
                        continue

                    time_parent = await time_elem.evaluate('el => el.parentElement.href')
                    if not time_parent:
                        continue

                    tweet_id = time_parent.split('/status/')[1].split('?')[0]

                    if tweet_id in seen_tweet_ids:
                        continue

                    # 获取推文文本
                    text_elem = await article.query_selector('[data-testid="tweetText"]')
                    if not text_elem:
                        continue

                    tweet_text = await text_elem.inner_text()

                    # 检查关键词
                    text_lower = tweet_text.lower()
                    matched_keyword = None
                    for kw in keywords:
                        if kw.lower() in text_lower:
                            matched_keyword = kw
                            break

                    # 临时注释掉关键词过滤，直接采集所有推文
                    # if not matched_keyword:
                    #     skipped_keyword += 1
                    #     continue

                    if matched_keyword:
                        print(f'[DEBUG] 匹配到关键词 "{matched_keyword}": {tweet_text[:50]}...')

                    # 获取时间
                    time_text = await (await time_elem.query_selector('..')).inner_text()
                    tweet_time = parse_time_ago(time_text)

                    # 临时注释掉时间过滤
                    # if tweet_time < time_threshold:
                    #     continue

                    # 获取观看数
                    views_elem = await article.query_selector('[href*="/analytics"]')
                    views_text = await views_elem.inner_text() if views_elem else '0'
                    views = parse_views(views_text)

                    # 临时注释掉观看数过滤
                    # if views < min_views:
                    #     continue

                    # 获取用户信息
                    user_elem = await article.query_selector('[data-testid="User-Name"] a')
                    username = await user_elem.get_attribute('href') if user_elem else ''
                    username = username.split('/')[-1] if username else ''
                    display_name = await user_elem.inner_text() if user_elem else username

                    # 获取互动数据
                    reply_elem = await article.query_selector('[data-testid="reply"]')
                    reply_label = await reply_elem.get_attribute('aria-label') if reply_elem else '0'
                    replies = int(''.join(filter(str.isdigit, reply_label)) or '0')

                    retweet_elem = await article.query_selector('[data-testid="retweet"]')
                    retweet_label = await retweet_elem.get_attribute('aria-label') if retweet_elem else '0'
                    retweets = int(''.join(filter(str.isdigit, retweet_label)) or '0')

                    like_elem = await article.query_selector('[data-testid="like"]')
                    like_label = await like_elem.get_attribute('aria-label') if like_elem else '0'
                    likes = int(''.join(filter(str.isdigit, like_label)) or '0')

                    seen_tweet_ids.add(tweet_id)
                    tweets.append({
                        'id': tweet_id,
                        'url': time_parent,
                        'text': tweet_text,
                        'username': username,
                        'displayName': display_name,
                        'timeStr': time_text,
                        'tweetTime': int(tweet_time.timestamp() * 1000),
                        'views': views,
                        'replies': replies,
                        'retweets': retweets,
                        'likes': likes
                    })
                    new_count += 1

                except Exception as e:
                    # 打印错误信息用于调试
                    print(f'[ERROR] 解析推文失败: {e}')
                    continue

            print(f'[INFO] 滚动 {scroll_attempts + 1}/{max_scrolls}, 本轮新增 {new_count} 条, 总计 {len(tweets)} 条')

            # 如果没有新推文了
            if new_count == 0:
                no_new_tweets_count += 1
                if no_new_tweets_count >= 3:
                    print('[INFO] 连续3次无新推文，停止采集')
                    break
            else:
                no_new_tweets_count = 0

            # 滚动到底部
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

            # 随机延迟
            delay = random.uniform(2, 5)
            await asyncio.sleep(delay)

            scroll_attempts += 1

        await browser.close()

    # 按时间排序
    tweets.sort(key=lambda x: x['tweetTime'], reverse=True)

    return {
        'collected': len(tweets),
        'tweets': tweets[:target_count],
        'config': {
            'keywords_count': len(keywords),
            'target_count': target_count,
            'days_ago': days_ago,
            'min_views': min_views
        }
    }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print('用法: python tweet_collector.py <output.json>')
        print('示例: python tweet_collector.py temp_tweets.json')
        sys.exit(1)

    # 读取配置
    script_dir = Path(__file__).parent
    config_path = script_dir / 'config.json'
    cookie_path = script_dir / 'cookie.txt'

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 获取 AI 主题的关键词
    keywords = config['themes']['AI']['keywords']

    # 读取 cookie
    cookie_string = parse_cookie_file(str(cookie_path))

    # 运行采集
    result = asyncio.run(collect_tweets(
        cookie_string=cookie_string,
        keywords=keywords,
        target_count=10,
        days_ago=7,  # 采集最近7天内的推文
        min_views=0  # 关闭观看数过滤
    ))

    # 保存结果
    output_file = sys.argv[1]
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f'[OK] 成功采集 {result["collected"]} 条推文')
    print(f'[OK] 已保存到 {output_file}')


if __name__ == '__main__':
    main()
