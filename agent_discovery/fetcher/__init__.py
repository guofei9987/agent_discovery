from .news_fetcher import NewsFetcher
from .rss_fetcher import RSSFetcher


def fetch_all_msg(cfg):
    all_msg = list()
    if cfg.get('news_source', {}).get('enabled', False):
        fetcher1 = NewsFetcher()
        news_msg = fetcher1.fetch_all(cfg)
        all_msg.extend(news_msg)

    if cfg.get('rss', {}).get('enabled', False):
        fetcher2 = RSSFetcher()
        rss_msg = fetcher2.fetch_all_rss(cfg)
        all_msg.extend(rss_msg)

    return all_msg
