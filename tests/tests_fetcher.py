import yaml
from importlib import resources

import agent_discovery.config as config

with resources.open_text(config, "config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

from agent_discovery.fetcher import NewsFetcher, RSSFetcher, ArxivFetcher, fetch_all_msg


def test_arxiv_fetcher():
    print(f"开始测试Arxiv获取器...")
    arxiv_fetcher = ArxivFetcher()
    papers = arxiv_fetcher.fetch_one("machine learning", max_results=5)
    assert len(papers) > 0
    print("Arxiv获取器测试完成")


def test_arxiv_fetcher_all():
    print(f"开始测试Arxiv批量获取器...")
    arxiv_fetcher = ArxivFetcher()
    papers_all = arxiv_fetcher.fetch_all(cfg)
    assert len(papers_all) > 0
    print("Arxiv批量获取器测试完成")


def test_news_fetcher_one():
    print(f"开始测试从单条新闻源获取新闻...")
    news_fetcher = NewsFetcher()
    sources = cfg['news_source']['sources'][0]
    news_one_platform = news_fetcher.fetch_one(sources['id'], sources['name'])
    assert len(news_one_platform) > 0
    print("单条获取新闻测试完成")


def test_news_fetcher_all():
    print(f"开始测试从批量获取新闻...")
    news_fetcher = NewsFetcher()
    news_all = news_fetcher.fetch_all(cfg)

    assert len(news_all) > 0
    print("批量获取新闻测试完成")


def test_rss_fetcher():
    """测试RSS获取器"""
    print("开始测试RSS获取器...")

    # 创建RSS获取器实例
    fetcher = RSSFetcher()

    # 测试获取所有RSS新闻
    rss_articles = fetcher.fetch_all_rss(cfg)
    print(f"获取到 {len(rss_articles)} 篇RSS文章")
    print(rss_articles)

    # 验证结果
    assert len(rss_articles) > 0
    print("RSS获取器测试完成")


def test_fetch_all_news():
    """测试获取所有新闻"""
    print("开始测试获取所有新闻...")

    # 获取所有新闻
    all_news = fetch_all_msg(cfg)
    print(f"获取到 {len(all_news)} 条新闻")
    print(all_news)

    # 验证结果
    assert len(all_news) > 0

    print("获取所有新闻测试完成")


def main():
    """主测试函数"""
    print("=" * 50)
    print("新闻获取器综合测试")
    print("=" * 50)

    try:
        test_news_fetcher_one()
        print()

        test_rss_fetcher()
        print()

        test_fetch_all_news()
        print()

        print("所有测试通过！")

    except Exception as e:
        print(f"测试失败: {e}")
        raise


if __name__ == "__main__":
    main()

# %%
