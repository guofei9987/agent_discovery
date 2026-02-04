from .news_fetcher import NewsFetcher
from .rss_fetcher import RSSFetcher
from .arxiv_fetcher import ArxivFetcher


def fetch_all_msg(cfg):
    all_msg = list()
    if 'news_source' in cfg:
        fetcher1 = NewsFetcher()
        news_msg = fetcher1.fetch_all(cfg)
        all_msg.extend(news_msg)

    if 'rss' in cfg:
        fetcher2 = RSSFetcher()
        rss_msg = fetcher2.fetch_all_rss(cfg)
        all_msg.extend(rss_msg)

    if 'arXiv' in cfg:
        arxiv = ArxivFetcher()
        arxiv_msg = arxiv.fetch_all(cfg)
        all_msg.extend(arxiv_msg)

    return all_msg
