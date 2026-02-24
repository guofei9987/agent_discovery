"""
Arxiv论文获取器
"""

import arxiv
from datetime import datetime
from typing import List, Dict, Optional


class ArxivFetcher:
    """Arxiv论文获取器类"""

    def __init__(self, max_results: int = 10):
        """
        初始化Arxiv获取器

        Args:
            max_results: 最大返回结果数
        """
        self.max_results = max_results
        self.client = arxiv.Client()

    def fetch_one(self, search_query: str, max_results: Optional[int] = None,
                  lifecycle_days: int = 3600) -> List[Dict]:
        """
        根据查询获取arxiv论文

        Args:
            search_query: 搜索查询词
            max_results: 最大返回结果数（覆盖初始化时的设置）
            lifecycle_days: 生命周期（天）

        Returns:
            论文信息列表
        """
        if max_results is None:
            max_results = self.max_results

        try:
            # ❗️这里缺个逻辑：按照 lifecycle_days 过滤
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            results = self.client.results(search)

            papers = []
            for item in results:
                papers.append({
                    "title": item.title,
                    "content": item.summary,
                    "url": item.entry_id,  # 带版本号的 url，未来是否去除？
                    "source": "arXiv",
                    "source_type": "arXiv",
                    "published_at": item.published,
                    "fetched_at": datetime.now(),
                    "lifecycle_days": lifecycle_days,
                })

            print(f"✅ 【arXiv】获取成功: 查询='{search_query}', 条目数: {len(papers)}")
            return papers

        except Exception as e:
            print(f"❌ 【arXiv】获取失败: 查询='{search_query}', 错误: {e}")
            return []

    def fetch_all(self, cfg) -> List[Dict]:
        """
        获取所有配置的arxiv论文

        Args:
            cfg: 配置字典

        Returns:
            统一格式的论文字典列表
        """
        print("获取arXiv论文...")

        if 'arXiv' not in cfg:
            return list()

        papers = list()
        for query_case in cfg['arXiv']:
            paper = self.fetch_one(
                query_case['query'],
                max_results=query_case.get('max_results', 5),
                lifecycle_days=query_case.get('lifecycle_days', 3600),
            )
            papers.extend(paper)

        print(f"从arXiv获取了 {len(papers)} 篇论文")
        return papers
