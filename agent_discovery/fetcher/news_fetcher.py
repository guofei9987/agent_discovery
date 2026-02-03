'''
从网络获取信息
'''

import json
import random
import time
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import requests


class NewsFetcher(object):
    DEFAULT_API_URL = "https://newsnow.busiyi.world/api/s"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

    def __init__(self):
        self.url = NewsFetcher.DEFAULT_API_URL

    def fetch_one(self, platform_id, platform_name
                  , max_retries: int = 3
                  , min_retry_wait: int = 3
                  , max_retry_wait: int = 5
                  ) -> dict:
        url = f"{self.url}?id={platform_id}"

        retries = 0
        while retries < max_retries:
            retries += 1
            try:
                response = requests.get(url, headers=NewsFetcher.DEFAULT_HEADERS, timeout=10)

                data_text = response.text
                data_dict = json.loads(data_text)
                if data_dict['status'] not in {'success', 'cache'}:
                    raise ValueError(f"请求出错 platform_id = {platform_id}, platform_name = {platform_name}")
                data_dict = data_dict['items']
                print(f"✅ 【新闻】 {platform_name} 获取 {len(data_dict)} 条（{url}）")
                return data_dict

            except Exception as e:
                print(f"❌ 【新闻】获取失败 {platform_name}（{url}）")
                wait_time = random.randint(min_retry_wait, max_retry_wait)
                time.sleep(wait_time)

        return dict()

    def fetch_all(self, cfg):
        print("获取新闻...")
        platforms = cfg.get('news_source', {}).get('sources', list())
        news_all = list()
        for platform in platforms:
            platform_id, platform_name = platform['id'], platform['name']
            news_one_platform = self.fetch_one(platform_id, platform_name)

            for news_one in news_one_platform:
                news_all.append({
                    "platform_id": platform_id
                    , "platform_name": platform_name
                    , "news_id": news_one['id']
                    , "news_title": news_one['title']
                    , "url": news_one['url']
                    # ❗️很多源没有时间，用当前时间
                    , "published_at": datetime.now()
                })

        print(f"从 {len(platforms)} 个平台，获取了 {len(news_all)} 条新闻")

        return news_all