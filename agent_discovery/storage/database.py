"""
数据库初始化和管理模块
"""

import os
from datetime import datetime, timedelta
from .models import Base, init_database, Article

# 确保data目录存在
DATA_DIR = "./agent_discovery_config"
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
            new_cnt = 0
            old_cnt = 0
            for article_data in articles:
                try:
                    now = datetime.now()
                    article_payload = {
                        "title": article_data["title"],
                        "content": article_data.get("content", ""),
                        "url": article_data["url"],
                        "source": article_data["source"],
                        "source_type": article_data.get("source_type", "no source type"),
                        "published_at": article_data.get("published_at", now),
                        "fetched_at": article_data.get("fetched_at", now),
                        "lifecycle_days": article_data.get("lifecycle_days", 3600),
                        # 更新后激活文章
                        "is_archived": False,
                        "archived_date": None,
                    }

                    existing_article = session.query(Article).filter_by(url=article_payload["url"]).first()
                    if existing_article:
                        # 原地更新，保留文章 ID 和关联交互数据
                        for field, value in article_payload.items():
                            setattr(existing_article, field, value)
                        old_cnt += 1
                    else:
                        session.add(Article(**article_payload))
                        new_cnt += 1

                except Exception as e:
                    print(f"❌ 处理文章失败: {article_data.get('title', 'Unknown')}, 错误: {e}")
                    # 继续处理其他文章，不中断整个过程
                    continue

            session.commit()
            print(f"✅ 数据库新增 {new_cnt} 篇文章，更新 {old_cnt} 篇文章")
            return new_cnt+old_cnt
        except Exception as e:
            session.rollback()
            print(f"❌ 保存文章到数据库失败: {e}")
            return 0
        finally:
            session.close()

    def archive_expired_articles(self):
        """归档超过生命周期的文章"""
        session = self.get_session()
        try:
            now = datetime.now()
            archive_month = now.strftime("%Y_%m")
            archived_count = 0

            active_articles = session.query(Article).filter(
                Article.is_archived.is_(False),
            ).all()

            for article in active_articles:
                if not article.published_at:
                    continue

                expire_at = article.published_at + timedelta(days=article.lifecycle_days)
                if now >= expire_at:
                    article.is_archived = True
                    article.archived_date = archive_month
                    archived_count += 1

            session.commit()
            print(f"成功归档 {archived_count} 篇过期文章")
            return archived_count
        except Exception as e:
            session.rollback()
            print(f"❌ 归档过期文章失败: {e}")
            return 0
        finally:
            session.close()

    def archive_and_add_articles(self, articles):
        """归档过期文章并添加新文章"""
        archived_count = self.archive_expired_articles()
        saved_count = self.save_articles_to_db(articles)


database_manager = DatabaseManager(DB_URL)
