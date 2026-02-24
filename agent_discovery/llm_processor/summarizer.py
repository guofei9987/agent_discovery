"""
LLM 摘要生成模块
使用 OpenAI 兼容接口调用 DeepSeek 或其他 LLM 服务
支持流式输出
"""

import os
from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from loguru import logger

from agent_discovery.storage.database import database_manager
from agent_discovery.storage.models import Article
from agent_discovery.config_loader import load_or_create_config, load_or_create_prompt


class LLMSummarizer:
    """LLM 摘要生成器"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化摘要生成器

        Args:
            config: LLM 配置，如果为 None 则从配置文件加载
        """
        if config is None:
            cfg = load_or_create_config()
            config = cfg.get("llm", {}).get("summarize", {})

        self.config = config
        self.model = config.get("model", "DeepSeek-V3.2")
        self.api_base = config.get("api_base", "https://api.deepseek.com/v1")
        self.api_key_env = config.get("api_key_env", "DEEPSEEK_API_KEY")
        self.provider = config.get("provider", "openai")
        self.stream_enabled = config.get("stream", True)
        self.sys_prompt = load_or_create_prompt()['summary']

        # 获取 API Key
        self.api_key = os.getenv(self.api_key_env)
        if not self.api_key:
            logger.warning(f"环境变量 {self.api_key_env} 未设置，LLM 功能将不可用")

        # 初始化 OpenAI 客户端
        self.client = None
        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

    async def get_unarchived_articles(self) -> List[Article]:
        """
        从数据库获取未归档的文章

        Returns:
            未归档的文章列表
        """
        session = database_manager.get_session()
        try:
            articles = session.query(Article).filter(
                Article.is_archived.is_(False)
            ).order_by(Article.published_at.desc()).all()
            return articles
        finally:
            session.close()

    def format_articles_for_prompt(self, articles: List[Article]) -> str:
        """
        将文章格式化为提示词

        Args:
            articles: 文章列表

        Returns:
            格式化后的提示词文本
        """
        formatted = []
        for i, article in enumerate(articles, 1):
            content = article.content or article.summary or ""
            # 限制内容长度，避免超出上下文限制
            if len(content) > 5000:
                content = content[:5000] + "..."

            formatted.append(f"""[{i}] 标题: {article.title}
来源: {article.source}
内容: {content}
---""")

        return "\n".join(formatted)

    def build_summary_prompt(self, articles_text: str) -> str:
        """
        构建摘要生成的系统提示词

        Args:
            articles_text: 格式化后的文章文本

        Returns:
            完整的提示词
        """
        return f"""以下是待摘要的文章：

{articles_text}

请生成综合摘要："""

    async def generate_summary_stream(self) -> AsyncGenerator[str, None]:
        """
        流式生成摘要

        Yields:
            生成的文本片段
        """
        if not self.client:
            logger.error("LLM 客户端未初始化，请检查 API Key 配置")
            yield "错误：LLM 服务未配置，请设置环境变量 {}".format(self.api_key_env)
            return

        try:
            # 获取未归档文章
            articles = await self.get_unarchived_articles()
            if not articles:
                logger.info("没有未归档的文章需要摘要")
                yield "暂无新闻内容需要摘要。"
                return

            logger.info(f"正在为 {len(articles)} 篇文章生成摘要...")

            # 格式化文章
            articles_text = self.format_articles_for_prompt(articles)
            prompt = self.build_summary_prompt(articles_text)

            # 调用 LLM 生成摘要（流式）
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": self.sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=0.7,
                max_tokens=5000
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            yield f"\n\n生成摘要时出错: {str(e)}"

    async def generate_summary(self) -> str:
        """
        非流式生成完整摘要

        Returns:
            完整的摘要文本
        """
        chunks = []
        async for chunk in self.generate_summary_stream():
            chunks.append(chunk)
        return "".join(chunks)


# 全局摘要生成器实例
_summarizer_instance: LLMSummarizer = None


def get_summarizer() -> LLMSummarizer:
    """获取全局摘要生成器实例（单例模式）"""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = LLMSummarizer()
    return _summarizer_instance


def reset_summarizer():
    """重置摘要生成器实例（用于配置更新后）"""
    global _summarizer_instance
    _summarizer_instance = None


if __name__ == "__main__":
    import asyncio


    async def test():
        summarizer = get_summarizer()
        print("开始生成摘要...")
        async for chunk in summarizer.generate_summary_stream():
            print(chunk, end="", flush=True)
        print("\n摘要生成完成")


    asyncio.run(test())
