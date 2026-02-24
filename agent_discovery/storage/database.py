"""
数据库初始化和管理模块
"""

import os
from datetime import datetime
from .models import Base, init_database, Article

# 确保data目录存在
DATA_DIR = "./data"
DB_PATH = os.path.join(DATA_DIR, "news.db")
DB_URL = f"sqlite:///{DB_PATH}"
COLD_DB_PATH = os.path.join(DATA_DIR, "cold_storage.db")
COLD_DB_URL = f"sqlite:///{COLD_DB_PATH}"


class DatabaseManager:
    """数据库管理类"""

    def __init__(self, db_url: str):
        """初始化数据库"""
        # 创建data目录（如果不存在）
        os.makedirs(DATA_DIR, exist_ok=True)

        # 初始化数据库表结构
        Session = init_database(db_url)
        self.Session = Session
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    

    def save_articles_to_db(self, articles):
        """保存文章到数据库"""
        session = self.get_session()
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
                            source_type=article_data.get("source_type", "no source type"),
                            published_at=article_data.get("published_at", datetime.now()),
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


database_manager = DatabaseManager(DB_URL)