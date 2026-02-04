# agent_discovery
我在用的信息获取app


# future palns

**LLM Assistance**
- [ ] LLM-based Information retrieval
- [ ] LLM-based Information reranking. Based on Prompts or user's action 
- [ ] LLM-based Information summarize


**More Information Sources**
- [x] arXiv
- [x] RSS
- Social Media:
    - [ ] Reddit Api
    - [ ] X Api
- News Api:
    - [ ] NewsAPI.org
    - [ ] Associated Press API
- Technical Sources:
  - [ ] GitHub API for trending repositories
  - [ ] Stack Overflow API for trending questions
  - [ ] Dev.to API for developer articles

- Academic Sources:
  - [ ] PubMed for medical research
  - [ ] IEEE Xplore for technical papers
  - [ ] Google Scholar integration







# How to Use

<!-- ## 安装

```shell
pip install agent-discovery
```

## 运行

启动 API 服务：

```shell
python -m agent_discovery.api.main
```

启动前端开发服务器：

```shell
python -m agent_discovery.frontend.server
```

首次运行会在当前目录生成默认配置目录 `agent_discovery_config`。

## 本地开发 -->

```shell
sh start.sh
```

# 配置项

配置模版参考：[config.yaml](./agent_discovery/config/config.yaml)

## arXiv

```yaml
arXiv:
  # query 直接沿用 arXiv 的 query 语法：
  # https://arxiv.org/help/api/user-manual#query_details
  - query: "transformer"
    max_results: 10
  - query: '("llm" OR "large language model" OR "large language models")'
    max_results: 30
```


## 新闻源

```yaml
ews_source:
  enabled: true  # 是否启用
  sources: # 不想使用的源可以注释掉
    - id: v2ex-share
      name: V2EX-最新分享
    - id: zhihu
      name: 知乎
    - id: weibo
      name: 微博-实时热搜
    - id: zaobao
      name: 联合早报 
    # - id: coolapk
    #   name: 酷安-今日最热
    - id: mktnews-flash
      name: MKTNews-快讯
    - id: wallstreetcn-quick
      name: 华尔街见闻-快讯
    - id: wallstreetcn-news
      name: 华尔街见闻-最新
    - id: wallstreetcn-hot
      name: 华尔街见闻-最热
    - id: 36kr-quick
      name: 36氪-快讯
    - id: 36kr-renqi
      name: 36氪-人气榜
    - id: douyin
      name: 抖音
    - id: hupu
      name: 虎扑-主干道热帖
    - id: tieba
      name: 百度贴吧-热议
    - id: toutiao
      name: 今日头条
    - id: ithome
      name: IT之家
    - id: thepaper
      name: 澎湃新闻-热榜
    - id: sputniknewscn
      name: 卫星通讯社
    - id: cankaoxiaoxi
      name: 参考消息
    - id: pcbeta-windows11
      name: 远景论坛-Win11
    - id: cls-telegraph
      name: 财联社-电报
    - id: cls-depth
      name: 财联社-深度
    - id: cls-hot
      name: 财联社-热门
    - id: xueqiu-hotstock
      name: 雪球-热门股票
    - id: gelonghui
      name: 格隆汇-事件
    - id: fastbull-express
      name: 法布财经-快讯
    - id: fastbull-news
      name: 法布财经-头条
    - id: solidot
      name: Solidot
    - id: hackernews
      name: Hacker News
    - id: producthunt
      name: Product Hunt
    - id: github-trending-today
      name: Github-Today
    - id: bilibili-hot-search
      name: 哔哩哔哩-热搜
    - id: kuaishou
      name: 快手
    - id: kaopu
      name: 靠谱新闻
    - id: jin10
      name: 金十数据
    - id: baidu
      name: 百度热搜
    - id: nowcoder
      name: 牛客
    - id: sspai
      name: 少数派
    - id: juejin
      name: 稀土掘金
    - id: ifeng
      name: 凤凰网-热点资讯
    - id: chongbuluo-latest
      name: 虫部落-最新
    - id: chongbuluo-hot
      name: 虫部落-最热
    - id: douban
      name: 豆瓣-热门电影
    - id: steam
      name: Steam-在线人数
    - id: tencent-hot
      name: 腾讯新闻-综合早报
    - id: freebuf
      name: Freebuf-网络安全
    - id: qqvideo-tv-hotsearch
      name: 腾讯视频-热搜榜
    - id: iqiyi-hot-ranklist
      name: 爱奇艺-热播榜
```

## RSS

```yaml
rss:
  enabled: true
  freshness_filter:
    enabled: true                     # 是否启用新鲜度过滤（默认启用）

    max_age_days: 3                   # 最大文章年龄（天）
  feeds:
    - id: "hacker-news"
      name: "Hacker News"
      url: "https://hnrss.org/frontpage"
      # max_age_days: 1               # 示例：只推送1天内的文章

    - id: "ruanyifeng"
      name: "阮一峰的网络日志"
      url: "http://www.ruanyifeng.com/blog/atom.xml"
      # max_age_days: 7               # 示例：推送7天内的文章（更新较慢的博客）

    - id: "yahoo-finance"
      name: "雅虎财经"
      url: "https://finance.yahoo.com/news/rssindex"
```


# Thanks to

- newsnow: [https://github.com/ourongxing/newsnow](https://github.com/ourongxing/newsnow)
- arxiv.py: [https://github.com/lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py)
