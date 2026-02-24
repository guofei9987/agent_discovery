"""
数据库模型定义
根据AGENT.md中的存储方案设计：
1. SQLite数据库存储最近30天的新闻数据
2. 用户点赞/不喜欢的数据存储在SQLite中
3. 历史数据每月归档到Markdown文件
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    JSON,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Article(Base):
    """新闻文章表"""
    __tablename__ = "articles"

    # 自增 id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本信息
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)

    # 来源信息
    source = Column(String(100), nullable=False)  # 来源网站名称
    source_type = Column(String(20), nullable=False)  # 来源类型（大类），如newsnow、arXiv等

    # 时间信息
    published_at = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.now(), nullable=False)
    lifecycle_days = Column(Integer, nullable=False, default=-1)  # 生命周期（天），-1 表示不限制

    # AI分析结果
    ai_summary = Column(Text, nullable=True)  # AI生成的摘要
    ai_keywords = Column(JSON, nullable=True)  # AI提取的关键词
    ai_sentiment = Column(Float, nullable=True)  # 情感分析得分(-1到1)
    ai_importance = Column(Float, nullable=True)  # 重要性评分(0-1)

    # 状态和标记，预留字段
    is_archived = Column(Boolean, default=False, index=True)  # 是否已归档
    archived_date = Column(String(10), nullable=True)  # 归档日期 YYYY_MM
    is_filtered = Column(Boolean, default=False)  # 是否被过滤掉

    # 用户交互统计（计算字段，非直接存储）
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)

    # 关系
    user_interactions = relationship("UserInteraction", back_populates="article", cascade="all, delete-orphan")


class UserInteraction(Base):
    """用户交互记录表"""
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户标识（可以是匿名session ID或用户ID）
    user_id = Column(String(100), nullable=False, index=True)

    # 关联的文章
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)

    # 交互类型
    interaction_type = Column(String(20), nullable=False)  # like, dislike, view, hide, save

    # 交互数据
    interaction_data = Column(JSON, nullable=True)  # 额外的交互数据

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    article = relationship("Article", back_populates="user_interactions")


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户标识
    user_id = Column(String(100), nullable=False, unique=True, index=True)

    # 偏好设置
    preferred_categories = Column(JSON, nullable=True)  # 偏好的新闻分类
    preferred_sources = Column(JSON, nullable=True)  # 偏好的新闻来源
    blocked_keywords = Column(JSON, nullable=True)  # 屏蔽的关键词
    blocked_sources = Column(JSON, nullable=True)  # 屏蔽的新闻来源

    # AI个性化设置
    ai_interpretation_enabled = Column(Boolean, default=True)
    ai_summary_length = Column(String(20), default="medium")  # short, medium, long

    # 显示设置
    items_per_page = Column(Integer, default=20)
    default_sort = Column(String(20), default="published_at")  # published_at, importance, relevance
    theme = Column(String(20), default="light")  # light, dark

    # 更新信息
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class TaskSchedule(Base):
    """定时任务记录表"""
    __tablename__ = "task_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 任务信息
    task_name = Column(String(100), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # fetch_news, archive_news, clean_up等

    # 执行信息
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    run_interval = Column(Integer, nullable=True)  # 运行间隔（秒）

    # 状态
    is_active = Column(Boolean, default=True)
    last_status = Column(String(20), nullable=True)  # success, failed, running
    last_error = Column(Text, nullable=True)

    # 统计
    total_runs = Column(Integer, default=0)
    success_runs = Column(Integer, default=0)

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Configuration(Base):
    """应用配置表"""
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 配置键值
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    config_type = Column(String(20), default="string")  # string, json, int, float, bool

    # 描述和分类
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)

    # 是否可修改
    is_editable = Column(Boolean, default=True)

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def init_database(db_path: str = "sqlite:///./data/news.db"):
    """
    初始化数据库连接和表结构
    """
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session


if __name__ == "__main__":
    # 测试数据库初始化
    print("初始化数据库...")
    Session = init_database()
    print("数据库初始化完成！")

    # 创建测试配置
    session = Session()

    # 添加默认配置
    default_configs = [
        Configuration(
            config_key="news_sources.rss.urls",
            config_value='["https://rss.example.com/feed"]',
            config_type="json",
            description="RSS新闻源URL列表",
            category="news_sources"
        ),
        Configuration(
            config_key="fetch_interval_minutes",
            config_value="30",
            config_type="int",
            description="新闻抓取间隔（分钟）",
            category="scheduler"
        ),
        Configuration(
            config_key="max_articles_per_fetch",
            config_value="50",
            config_type="int",
            description="每次抓取的最大文章数",
            category="news_fetcher"
        ),
    ]

    for config in default_configs:
        session.merge(config)  # 使用merge避免重复插入

    session.commit()
    session.close()
    print("默认配置已添加！")
