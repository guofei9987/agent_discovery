"""
新闻聚合器Web API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uvicorn
from loguru import logger
import yaml
from importlib import resources

from agent_discovery.storage.models import Article
from agent_discovery.storage.database import database_manager
from agent_discovery.fetcher import fetch_all_msg
from agent_discovery.config_loader import load_or_create_config

# 创建FastAPI应用
app = FastAPI(
    title="新闻聚合器API",
    description="一个智能新闻聚合和分析API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic模型定义
class ArticleResponse(BaseModel):
    id: int

    title: str
    content: Optional[str]
    summary: Optional[str]
    url: str

    source: str
    source_type: str

    published_at: datetime
    fetched_at: datetime

    ai_summary: Optional[str]
    ai_keywords: Optional[List[str]]
    ai_sentiment: Optional[float]
    ai_importance: Optional[float]

    is_filtered: Optional[bool]

    class Config:
        from_attributes = True


class FetchResult(BaseModel):
    success: bool
    message: str
    articles_fetched: int


# API路由
@app.get("/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用新闻聚合器API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now()}


@app.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
        limit: int = Query(50, ge=1, le=500, description="返回文章数量限制"),
        offset: int = Query(0, ge=0, description="偏移量"),
        source: Optional[str] = Query(None, description="新闻源过滤"),
        importance_threshold: Optional[float] = Query(None, ge=0, le=1, description="重要性阈值"),
        sentiment_filter: Optional[str] = Query(None, description="情感过滤 (positive/negative/neutral)"),
        keyword: Optional[str] = Query(None, description="关键词搜索"),
        start_date: Optional[datetime] = Query(None, description="开始日期"),
        end_date: Optional[datetime] = Query(None, description="结束日期"),
        sort_by: Optional[str] = Query("id", description="排序字段 (id/published_at)")
):
    """
    获取文章列表
    """
    session = database_manager.get_session()
    try:
        query = session.query(Article)

        # 应用过滤条件
        if source is not None and source != "":
            query = query.filter(Article.source == source)

        if importance_threshold is not None:
            query = query.filter(Article.ai_importance >= importance_threshold)

        if sentiment_filter:
            if sentiment_filter == "positive":
                query = query.filter(Article.ai_sentiment > 0)
            elif sentiment_filter == "negative":
                query = query.filter(Article.ai_sentiment < 0)
            elif sentiment_filter == "neutral":
                query = query.filter(Article.ai_sentiment == 0)

        if keyword:
            query = query.filter(
                Article.title.contains(keyword) |
                Article.summary.contains(keyword) |
                Article.content.contains(keyword)
            )

        if start_date:
            query = query.filter(Article.published_at >= start_date)

        if end_date:
            query = query.filter(Article.published_at <= end_date)

        # 应用分页和排序
        if sort_by == "published_at":
            articles = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
        else:
            articles = query.order_by(Article.id.desc()).offset(offset).limit(limit).all()

        return articles
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取文章列表失败")
    finally:
        session.close()


@app.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int):
    """
    获取单篇文章详情
    """
    session = database_manager.get_session()
    try:
        article = session.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章未找到")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取文章详情失败")
    finally:
        session.close()


@app.post("/fetch", response_model=FetchResult)
async def fetch_news():
    """
    手动触发新闻获取
    """
    try:
        cfg = load_or_create_config()

        all_articles = fetch_all_msg(cfg)
        database_manager.archive_and_add_articles(all_articles)

        return FetchResult(
            success=True,
            message=f"成功获取并保存了 {len(all_articles)} 篇文章 ",
            articles_fetched=len(all_articles)
        )
    except Exception as e:
        logger.error(f"新闻获取失败: {e}")
        return FetchResult(
            success=False,
            message=f"新闻获取失败: {str(e)}",
            articles_fetched=0
        )


@app.get("/sources")
async def get_sources():
    """
    获取所有新闻源列表
    """
    session = database_manager.get_session()
    try:
        sources = session.query(Article.source).distinct().all()
        return [source[0] for source in sources]
    except Exception as e:
        logger.error(f"获取新闻源列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取新闻源列表失败")
    finally:
        session.close()


@app.get("/stats")
async def get_stats():
    """
    获取统计信息
    """
    session = database_manager.get_session()
    try:
        total_articles = session.query(Article).count()
        today_articles = session.query(Article).filter(
            Article.published_at >= datetime.now().date()
        ).count()

        # 获取最近7天的文章统计
        week_ago = datetime.now() - timedelta(days=7)
        week_articles = session.query(Article).filter(
            Article.published_at >= week_ago
        ).count()

        # 按源统计
        source_stats = {}
        sources = session.query(Article.source).distinct().all()
        for source in sources:
            count = session.query(Article).filter(Article.source == source[0]).count()
            source_stats[source[0]] = count

        return {
            "total_articles": total_articles,
            "today_articles": today_articles,
            "week_articles": week_articles,
            "sources": source_stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")
    finally:
        session.close()


if __name__ == "__main__":
    # 启动开发服务器
    logger.info("启动新闻聚合器API服务器...")
    uvicorn.run(
        "agent_discovery.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
