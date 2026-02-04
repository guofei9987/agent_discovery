from agent_discovery.storage.database import database_manager
from agent_discovery.storage.models import Configuration
from agent_discovery.storage.models import Article
from datetime import datetime

def test_database_connection():
    """测试数据库连接"""
    try:
        session = database_manager.get_session()
        # 尝试执行一个简单的查询
        count = session.query(Configuration).count()
        session.close()
        print(f"数据库连接成功，配置表中有 {count} 条记录")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def test_database_articles():
    """测试文章的查询"""

    session = database_manager.get_session()
    total_articles = session.query(Article).count()
    print(f"数据库中共有 {total_articles} 篇文章")

    today_articles = session.query(Article).filter(
        Article.fetched_at >= datetime.now().date()
    ).count()
    print(f"今天获取了 {today_articles} 篇文章")

    session.close()
