"""
新闻聚合器主入口点
"""

import argparse
import uvicorn
from loguru import logger
import os
import sys

# 添加news_agent目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent_discovery'))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新闻聚合器")
    parser.add_argument(
        "action",
        choices=["api", "fetch", "test"],
        help="要执行的操作: api(启动API服务器), fetch(获取新闻), test(运行测试)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API服务器主机地址"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API服务器端口"
    )

    args = parser.parse_args()

    if args.action == "api":
        # 启动API服务器
        logger.info(f"启动新闻聚合器API服务器 at {args.host}:{args.port}")
        uvicorn.run(
            "agent_discovery.api.main:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )
    elif args.action == "fetch":
        # 获取新闻
        logger.info("开始获取新闻...")
        try:
            from agent_discovery.fetcher.rss_fetcher import RSSFetcher
            rss_fetcher = RSSFetcher()
            articles = rss_fetcher.fetch_all_rss()
            # 这里应该保存文章到数据库，但为了简化，我们只返回文章数量
            saved_count = len(articles)
            logger.info(f"新闻获取完成，获取了 {saved_count} 篇文章")
        except Exception as e:
            logger.error(f"新闻获取失败: {e}")
    elif args.action == "test":
        # 运行测试
        logger.info("运行测试...")
        print("测试功能尚未完全实现")


if __name__ == "__main__":
    main()