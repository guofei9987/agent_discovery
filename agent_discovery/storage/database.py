"""
数据库初始化和管理模块
"""

import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .models import Base, init_database, Article

# 确保data目录存在
DATA_DIR = "./data"
DB_PATH = os.path.join(DATA_DIR, "news.db")
DB_URL = f"sqlite:///{DB_PATH}"


def initialize_database():
    """初始化数据库"""
    # 创建data目录（如果不存在）
    os.makedirs(DATA_DIR, exist_ok=True)

    # 初始化数据库表结构
    Session = init_database(DB_URL)

    # 创建默认配置
    create_default_configurations(Session)

    return Session


def create_default_configurations(Session):
    """创建默认配置"""
    session = Session()

    try:
        # 检查是否已有配置
        from .models import Configuration

        # 默认配置项
        default_configs = [
            {
                "config_key": "news_sources.rss.urls",
                "config_value": '["https://feeds.bbci.co.uk/news/rss.xml", "https://rss.cnn.com/rss/edition.rss"]',
                "config_type": "json",
                "description": "RSS新闻源URL列表",
                "category": "news_sources"
            },
            {
                "config_key": "news_sources.api.newsapi.enabled",
                "config_value": "false",
                "config_type": "bool",
                "description": "是否启用NewsAPI",
                "category": "news_sources"
            },
            {
                "config_key": "fetch_interval_minutes",
                "config_value": "30",
                "config_type": "int",
                "description": "新闻抓取间隔（分钟）",
                "category": "scheduler"
            },
            {
                "config_key": "max_articles_per_fetch",
                "config_value": "50",
                "config_type": "int",
                "description": "每次抓取的最大文章数",
                "category": "news_fetcher"
            },
            {
                "config_key": "llm.provider",
                "config_value": "openai",
                "config_type": "string",
                "description": "LLM提供商（openai/claude/ollama）",
                "category": "llm"
            },
            {
                "config_key": "llm.model",
                "config_value": "gpt-3.5-turbo",
                "config_type": "string",
                "description": "LLM模型名称",
                "category": "llm"
            },
            {
                "config_key": "archive.days_threshold",
                "config_value": "30",
                "config_type": "int",
                "description": "归档阈值（天数）",
                "category": "storage"
            }
        ]

        # 插入或更新默认配置
        for config_data in default_configs:
            config = session.query(Configuration).filter_by(config_key=config_data["config_key"]).first()
            if config:
                # 更新现有配置的描述等信息
                config.config_value = config_data["config_value"]
                config.config_type = config_data["config_type"]
                config.description = config_data["description"]
                config.category = config_data["category"]
            else:
                # 创建新配置
                config = Configuration(**config_data)
                session.add(config)

        session.commit()
        print("默认配置已创建/更新")

    except Exception as e:
        session.rollback()
        print(f"创建默认配置时出错: {e}")
    finally:
        session.close()


def get_database_session():
    """获取数据库会话"""
    Session = initialize_database()
    return Session()


def test_database_connection():
    """测试数据库连接"""
    try:
        Session = initialize_database()
        session = Session()
        # 尝试执行一个简单的查询
        from .models import Configuration
        count = session.query(Configuration).count()
        session.close()
        print(f"数据库连接成功，配置表中有 {count} 条记录")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def save_articles_to_db(articles):
    """保存文章到数据库"""
    session = get_database_session()
    try:
        saved_count = 0
        for article_data in articles:
            try:
                # 检查文章是否已存在
                existing_article = session.query(Article).filter(
                    Article.url == article_data["url"]
                ).first()

                if not existing_article:
                    # 创建新文章
                    article = Article(
                        title=article_data["news_title"],
                        content=article_data.get("content", ""),
                        url=article_data["url"],
                        source=article_data["platform_name"],
                        source_type=article_data.get("source_type", "rss"),
                        published_at=article_data.get("published_at", datetime.now().isoformat()),
                    )
                    session.add(article)
                    saved_count += 1
            except Exception as e:
                print(f"处理文章失败: {article_data.get('news_title', 'Unknown')}, 错误: {e}")
                # 继续处理其他文章，不中断整个过程
                continue

        session.commit()
        print(f"成功保存 {saved_count} 篇文章到数据库")
        return saved_count
    except Exception as e:
        session.rollback()
        print(f"保存文章到数据库失败: {e}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    # 测试数据库初始化
    print("初始化数据库...")
    if test_database_connection():
        print("数据库初始化完成！")
    else:
        print("数据库初始化失败！")