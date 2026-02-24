

import arxiv
from typing import List, Dict, Optional


client = arxiv.Client()
search = arxiv.Search(
    query="transformer",
    max_results=2,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

results = client.results(search)

papers = []
for item in results:
    papers.append({
        "platform_id": "arXiv",
        "platform_name": "arXiv",
        "news_id": item.entry_id,
        "title": item.title,
        "url": item.entry_id,  # arxiv entry_id is also the URL
        "content": item.summary,
        "published_at": item.published
    })
#%%
