from agent_discovery.storage.database import database_manager
from agent_discovery.storage.models import Configuration

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
