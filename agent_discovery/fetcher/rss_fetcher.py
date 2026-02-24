"""
RSS新闻获取器
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class RSSFetcher:
    """RSS新闻获取器类"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_feed(self, rss_url: str) -> Optional[Dict]:
        """
        获取RSS feed数据

        Args:
            rss_url: RSS feed URL

        Returns:
            feed数据字典或None
        """
        try:
            response = self.session.get(rss_url, timeout=self.timeout)
            response.raise_for_status()

            # 解析RSS feed
            feed = feedparser.parse(response.content)
            print(f"✅ 【RSS】获取成功: {rss_url}, 条目数: {len(feed.entries)}")
            return feed
        except Exception as e:
            print(f"❌ 【RSS】获取失败 {rss_url}: {e}")
            return None

    def is_article_fresh(self, entry: Dict, lifecycle_days: int) -> bool:
        """
        检查文章是否足够新鲜

        Args:
            entry: RSS条目
            lifecycle_days: 最大文章年龄（天）

        Returns:
            是否足够新鲜
        """
        if lifecycle_days <= 0:
            return True  # 禁用过滤

        # 提取发布时间
        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_at = datetime(*entry.updated_parsed[:6])

        if not published_at:
            return True  # 没有发布时间，不过滤

        # 检查文章年龄
        max_age = timedelta(days=lifecycle_days)
        article_age = datetime.now() - published_at
        return article_age <= max_age

    def parse_article(self, entry: Dict, source_url: str, source_name: str) -> Optional[Dict]:
        """
        解析RSS条目为统一格式

        Args:
            entry: RSS条目
            source_url: RSS源URL
            source_name: 来源名称

        Returns:
            统一格式的文章字典或None
        """
        try:
            # 提取基本信息
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()

            # 提取发布时间
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            else:
                published_at = datetime.now()

            # 创建统一格式的文章字典
            article = {
                "platform_id": f"rss_{source_name.lower().replace(' ', '_')}",
                "platform_name": source_name,
                "news_id": link,  # 使用链接作为ID
                "news_title": title,
                "url": link,
                "published_at": published_at
                , "source_type": "rss"
            }

            return article
        except Exception as e:
            print(f"解析文章失败: {e}")
            return None

    def fetch_articles_from_rss(self, rss_url: str, source_name: str = "Unknown"
                                , lifecycle_days: int = 3) -> List[Dict]:
        """
        从RSS源获取文章列表

        Args:
            rss_url: RSS源URL
            source_name: 来源名称
            lifecycle_days: 最大文章年龄（天）

        Returns:
            统一格式的文章字典列表
        """
        articles = []

        # 获取RSS feed
        feed = self.fetch_feed(rss_url)
        if not feed:
            return articles

        # 解析每个条目
        for entry in feed.entries:
            # 检查文章新鲜度
            if not self.is_article_fresh(entry, lifecycle_days):
                continue

            article = self.parse_article(entry, rss_url, source_name)
            if article and article['news_title'] and article['url']:
                articles.append(article)

        return articles

    def fetch_all_rss(self, cfg) -> List[Dict]:
        """
        获取所有配置的RSS源并保存到数据库

        Returns:
            统一格式的文章字典列表
        """
        print("获取RSS...")

        all_articles = []

        # 获取RSS源列表
        feeds = cfg.get('rss', {}).get('feeds', [])

        # 获取每个RSS源的文章
        for feed_config in feeds:
            rss_url = feed_config['url']
            source_name = feed_config['name']

            # 获取该源的新鲜度设置（覆盖全局设置）
            lifecycle_days = feed_config.get('lifecycle_days', -1)

            articles = self.fetch_articles_from_rss(rss_url, source_name, lifecycle_days)
            all_articles.extend(articles)

        print(f"从 {len(feeds)} 个平台，获取了 {len(all_articles)} 条RSS")
        return all_articles
