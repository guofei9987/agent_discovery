from concurrent.futures import ThreadPoolExecutor
from .news_fetcher import NewsFetcher
from .rss_fetcher import RSSFetcher
from .arxiv_fetcher import ArxivFetcher


def fetch_all_msg(cfg):
    """并行获取所有数据源的消息"""
    executors = []

    if 'news_source' in cfg:
        executors.append(lambda: NewsFetcher().fetch_all(cfg))
    if 'rss' in cfg:
        executors.append(lambda: RSSFetcher().fetch_all_rss(cfg))
    if 'arXiv' in cfg:
        executors.append(lambda: ArxivFetcher().fetch_all(cfg))

    with ThreadPoolExecutor() as pool:
        results = list(pool.map(lambda f: f(), executors))

    return [item for r in results for item in r]
