#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI InsightLens – AI-Only, Notion + Email (No Telegram)
- 조회형(RSS/API) + LLM 요약 -> LLM 태그 체인(강화 분류) -> Notion 기록
- 추가 발행: 이메일(SMTP)
- 텔레그램 비활성(코드 제거)

ENV (.env or CI Secrets)
- OPENAI_API_KEY
- NOTION_TOKEN
- NOTION_DB_ID
- EMAIL_ENABLE=true/false
- EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_USERNAME, EMAIL_PASSWORD
- EMAIL_FROM, EMAIL_TO (comma-separated)

작성: ChatGPT
"""

import os, sys, traceback
from datetime import datetime, timezone, timedelta
import feedparser, requests, yfinance as yf
import pandas as pd, time
from notion_client import Client as NotionClient

# OpenAI SDK
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ---- ENV LOADER ----
from pathlib import Path
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NOTION_TOKEN   = os.getenv("NOTION_TOKEN", "")
NOTION_DB_ID   = os.getenv("NOTION_DB_ID", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")  # 선택: 시장 데이터 백업

EMAIL_ENABLE   = os.getenv("EMAIL_ENABLE", "false").lower() == "true"
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME  = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM      = os.getenv("EMAIL_FROM", "")
EMAIL_TO        = [e.strip() for e in os.getenv("EMAIL_TO", "").split(",") if e.strip()]

if not NOTION_TOKEN or not NOTION_DB_ID:
    print("[ERROR] NOTION_TOKEN / NOTION_DB_ID is required.")
    sys.exit(1)

# ---- AI-FOCUSED SOURCES ----
# 연구소 & 기업 AI 블로그
RSS_SOURCES = [
    # AI 연구 논문 & 오픈소스
    "https://huggingface.co/blog/feed.xml",                      # Hugging Face Blog
    "https://openai.com/blog/rss/",                              # OpenAI Blog
    "https://www.anthropic.com/news/rss.xml",                    # Anthropic Blog
    "https://deepmind.google/blog/rss.xml",                      # Google DeepMind Blog
    "https://ai.meta.com/blog/rss/",                             # Meta AI Blog
    "https://www.lesswrong.com/feed.xml",                        # LessWrong AI Safety
    "https://paperswithcode.com/blog/rss",                       # Papers with Code
    
    # 빅테크 AI 블로그
    "https://ai.googleblog.com/atom.xml",                        # Google AI Blog
    "https://aws.amazon.com/blogs/machine-learning/feed/",       # AWS ML Blog
    "https://blogs.microsoft.com/ai/feed/",                      # Microsoft AI Blog
    "https://blogs.nvidia.com/blog/category/deep-learning/feed/", # NVIDIA AI Blog
    "https://machinelearning.apple.com/rss.xml",                 # Apple ML Research
    "https://community.intel.com/t5/Blogs/v2/bg-p/blogs/rss?board.id=artificial-intelligence", # Intel AI
    "https://www.snowflake.com/blog/rss/",                       # Snowflake Blog
    "https://www.databricks.com/blog/category/engineering-blog/feed", # Databricks Blog
    
    # 스타트업 & 투자 뉴스
    "https://techcrunch.com/tag/artificial-intelligence/feed/",  # TechCrunch AI
    "https://venturebeat.com/category/ai/feed/",                 # VentureBeat AI
    "https://news.crunchbase.com/feed/",                         # Crunchbase News
    "https://a16z.com/tag/artificial-intelligence/feed/",        # Andreessen Horowitz
    "https://www.ycombinator.com/blog/feed",                     # Y Combinator Blog
    
    # 주식 & 애널리스트 전망
    "https://seekingalpha.com/feed.xml",                         # Seeking Alpha
    "https://www.marketwatch.com/rss/topstories",                # MarketWatch
    "https://www.barrons.com/articles/rss",                      # Barron's
    "https://www.fool.com/feeds/fool-articles.rss",              # The Motley Fool
]

# arXiv: AI/ML/NLP 통합
ARXIV_QUERY = "cs.AI+OR+cs.LG+OR+cs.CL"
ARXIV_MAX = 5
MAX_ITEMS = 15

# ---- UTIL ----
def iso_date_kst():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def safe_get(d, k, default=""):
    try:
        return d.get(k, default) or default
    except Exception:
        return default

# ---- FETCH ----
def fetch_rss(limit=MAX_ITEMS, hours_limit=24):
    """각 RSS 소스에서 고르게 기사를 수집 (최근 24시간 필터링)"""
    items = []
    per_source = max(2, limit // len(RSS_SOURCES))  # 소스당 최소 2개
    
    from time import mktime, time as current_time
    cutoff_time = current_time() - (hours_limit * 3600)
    
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            source_name = safe_get(feed.feed, "title") or url.split('/')[2]  # 도메인명 사용
            
            for e in feed.entries[:per_source * 3]:  # 더 많이 가져와서 필터링
                # 게시일 추출 및 24시간 필터링
                pub_date = ""
                pub_timestamp = None
                
                if hasattr(e, 'published_parsed') and e.published_parsed:
                    from time import strftime
                    pub_date = strftime("%Y-%m-%d", e.published_parsed)
                    pub_timestamp = mktime(e.published_parsed)
                elif hasattr(e, 'updated_parsed') and e.updated_parsed:
                    from time import strftime
                    pub_date = strftime("%Y-%m-%d", e.updated_parsed)
                    pub_timestamp = mktime(e.updated_parsed)
                
                # 24시간 이내만 수집 (타임스탬프가 있는 경우)
                if pub_timestamp and pub_timestamp < cutoff_time:
                    continue
                
                items.append({
                    "title": safe_get(e, "title"),
                    "link": safe_get(e, "link"),
                    "summary": safe_get(e, "summary"),
                    "source": source_name,
                    "published": pub_date,
                })
                
                if len([x for x in items if x['source'] == source_name]) >= per_source:
                    break
                    
        except Exception as e:
            print(f"[WARN] RSS parse failed: {url} – {e}")
    
    # dedup
    uniq, seen = [], set()
    for it in items:
        key = (it["title"] or "")[:160]
        if key in seen: continue
        seen.add(key); uniq.append(it)
    
    return uniq[:limit * 2]  # 중복 제거 후에도 충분한 개수 확보

def fetch_arxiv(max_n=ARXIV_MAX, hours_limit=24):
    url = "https://export.arxiv.org/api/query"
    params = {"search_query": f"cat:{ARXIV_QUERY}", "max_results": str(max_n * 2), "sortBy":"submittedDate","sortOrder":"descending"}
    try:
        from time import mktime, time as current_time
        cutoff_time = current_time() - (hours_limit * 3600)
        
        r = requests.get(url, params=params, timeout=15); r.raise_for_status()
        feed = feedparser.parse(r.text)
        items = []
        
        for e in feed.entries:
            # arXiv 게시일 추출 및 24시간 필터링
            pub_date = ""
            pub_timestamp = None
            
            if hasattr(e, 'published_parsed') and e.published_parsed:
                from time import strftime
                pub_date = strftime("%Y-%m-%d", e.published_parsed)
                pub_timestamp = mktime(e.published_parsed)
            
            # 24시간 이내만 수집
            if pub_timestamp and pub_timestamp < cutoff_time:
                continue
                
            items.append({
                "title": safe_get(e, "title"),
                "link": safe_get(e, "link"),
                "summary": safe_get(e, "summary"),
                "source": "arXiv",
                "published": pub_date,
            })
            
            if len(items) >= max_n:
                break
                
        return items
    except Exception as e:
        print("[WARN] arXiv fetch failed:", e); return []

# ---- MARKET: Big Tech AI Basket ----
def _stooq_last_close(symbol: str, retries: int = 2, timeout: int = 10):
    """
    Stooq 일일 시세 CSV (미국 종목은 .us 접미사)
    예: https://stooq.com/q/d/l/?s=nvda.us&i=d
    2일치 이상이면 전일 대비 등락 계산, 1일치면 종가만 표시
    """
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d"
    headers = {"User-Agent": "Mozilla/5.0 InsightLens/1.0"}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            # 일부 지역에서 공백/빈 응답이 올 수 있어 df가 비는 경우가 있음
            from io import StringIO
            csv_text = r.text.strip()
            if not csv_text or "404 Not Found" in csv_text:
                raise ValueError("Empty CSV")
            df = pd.read_csv(StringIO(csv_text))
            if len(df) >= 2:
                last = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                chg = (last - prev) / prev * 100.0
                return last, chg
            elif len(df) == 1:
                last = float(df["Close"].iloc[-1])
                return last, None
        except Exception:
            if attempt < retries:
                time.sleep(1.0)
                continue
            return None, None
    return None, None

def _alpha_vantage_last_close(symbol: str, api_key: str, timeout: int = 10):
    """
    Alpha Vantage TIME_SERIES_DAILY_ADJUSTED API로 종가/등락률 계산
    예: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NVDA&apikey=xxx
    """
    if not api_key:
        return None, None
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"  # 최근 100일
    }
    
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        
        if "Time Series (Daily)" not in data:
            return None, None
        
        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) >= 2:
            last_date = dates[0]
            prev_date = dates[1]
            last = float(time_series[last_date]["5. adjusted close"])
            prev = float(time_series[prev_date]["5. adjusted close"])
            chg = (last - prev) / prev * 100.0
            return last, chg
        elif len(dates) == 1:
            last_date = dates[0]
            last = float(time_series[last_date]["5. adjusted close"])
            return last, None
    except Exception:
        pass
    
    return None, None

def fetch_market(tickers=("NVDA","MSFT","AAPL","GOOGL","AMZN","META","AMD","AVGO","ORCL","IBM","TSLA")):
    """
    빅테크 AI 바스켓 스냅샷
    1순위: Stooq CSV → 2순위: Alpha Vantage API
    """
    out = []
    for t in tickers:
        last, chg = None, None
        
        # 1) Stooq 우선 시도
        last, chg = _stooq_last_close(t)
        
        # 2) 실패 시 Alpha Vantage로 대체
        if last is None and ALPHA_VANTAGE_KEY:
            last, chg = _alpha_vantage_last_close(t, ALPHA_VANTAGE_KEY)
        
        # 3) 포맷
        if last is None:
            out.append(f"{t}: N/A")
        elif chg is None:
            out.append(f"{t}: {last:.2f}")
        else:
            out.append(f"{t}: {last:.2f} ({chg:+.2f}%)")
    
    return " | ".join(out) if out else "N/A"

# ---- LLM ----
SUMMARY_PROMPT = """You are an AI & investment analyst.
From the following AI-focused articles grouped by source and market data,
create TWO versions of summary:

**[ENGLISH VERSION]**
For EACH source group:
- Source name as heading (e.g., "## OpenAI Blog")
- 2-3 concise bullet points (• ) summarizing key insights (max 25 words each)
- Focus on: new models, research, products, investments, technical breakthroughs

At the end, add:
- "## Market Trends" section: Analyze stock market snapshot
  * Brief commentary on overall market sentiment
  * Highlight biggest movers
  * Connect to AI news if relevant
- "## Overall Analysis" section with 3-4 bullets on trends and market implications
- Three hashtags: #tag1 #tag2 #tag3

**[KOREAN VERSION]**
Same structure but in Korean (한글로 작성):
- 각 소스별 헤딩 (예: "## OpenAI Blog")
- 2-3개 bullet points (• )
- "## 시장 동향" 섹션
- "## 종합 분석" 섹션
- 해시태그 3개

Be factual and neutral. Use '추정' or 'estimated' when uncertain."""

TAG_PROMPT = """You are a taxonomy classifier for AI industry topics.
Given the same articles and the summary below, assign up to 6 tags from the following controlled vocabulary ONLY:

[Tags]
AI, AGI, LLM, Multimodal, Vision, Speech, Audio, TTS, ASR,
RAG, Retrieval, Vector DB, Embeddings, Agents, Tools, Orchestration,
Safety, Alignment, Red Teaming, Evaluation, Benchmark,
MLOps, Data Infra, Data Pipeline, Prompting, Fine-tuning, Distillation,
Inference, Inference Cost, Quantization, Acceleration, GPU, TPU, NPU, Chips,
On-device, Edge AI, Mobile, Robotics,
Cloud, Serving, Observability, Monitoring,
Open Source, Licensing, Model Release, Dataset,
Search, Productivity, Developer Tools,
Healthcare, Finance, Legal, Education, Gov/Policy, Regulation, Privacy, Security,
Funding, Investment, M&A, Roadmap

Return JSON with:
{{"tags": ["Tag1","Tag2",...]}}

[ARTICLES]
{articles}

[SUMMARY]
{summary}
"""

def llm_call(messages, model="gpt-4o-mini", temperature=0.4):
    if not OPENAI_API_KEY or OpenAI is None:
        return None
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    return resp.choices[0].message.content.strip()

def build_articles_block(items):
    """소스별로 그룹화하여 기사 블록 생성 (게시일 포함)"""
    from collections import defaultdict
    grouped = defaultdict(list)
    
    # 소스별로 그룹화
    for it in items:
        source = it.get('source', 'Unknown')
        grouped[source].append(it)
    
    # 소스별로 포맷팅
    blocks = []
    for source, articles in grouped.items():
        blocks.append(f"[{source}]")
        for i, art in enumerate(articles, 1):
            title = art.get('title', 'No title')
            link = art.get('link', '')
            summary = (art.get('summary', '') or '')[:200]
            pub_date = art.get('published', '')
            
            # 제목 뒤에 게시일 추가
            if pub_date:
                title_with_date = f"{title} ({pub_date})"
            else:
                title_with_date = title
                
            blocks.append(f"  {i}. {title_with_date}\n     {link}\n     {summary}")
        blocks.append("")  # 빈 줄
    
    return "\n".join(blocks)

def summarize(items, market_data=""):
    body = build_articles_block(items)
    
    # 시장 데이터 추가
    if market_data and market_data != "N/A":
        body += f"\n\n[시장 스냅샷 - AI 주요 기업 주가]\n{market_data}"
    
    out = llm_call([{"role":"system","content":SUMMARY_PROMPT},
                    {"role":"user","content": body}])
    if not out:
        # fallback
        out = """**[ENGLISH VERSION]**

## Key Updates
• OpenAI announces API price reduction and performance improvements
• Google DeepMind unveils new multimodal model research
• Major VCs increase investments in AI infrastructure startups

## Market Trends
• AI stocks show overall upward trend
• NVIDIA and cloud companies maintain strong momentum

## Overall Analysis
• Intensifying LLM cost competition expected to accelerate AI adoption
• Multimodal AI emerging as next-generation trend
• AI infrastructure and tooling market continues growth trajectory

#AI #LLM #Investment

---

**[KOREAN VERSION]**

## 주요 소식
• OpenAI API 가격 인하 및 성능 개선 발표
• Google DeepMind의 새로운 멀티모달 모델 연구 공개
• 주요 VC들의 AI 인프라 스타트업 투자 증가

## 시장 동향
• AI 주요 기업 주가 대체로 상승세
• NVIDIA 및 클라우드 기업 강세 지속

## 종합 분석
• LLM 비용 경쟁 심화로 AI 도입 가속화 예상
• 멀티모달 AI가 차세대 트렌드로 부상
• AI 인프라 및 도구 시장 성장세 지속

#AI #LLM #투자"""
    return out

def classify_tags(items, summary_text):
    body = TAG_PROMPT.format(articles=build_articles_block(items), summary=summary_text)
    raw = llm_call([{"role":"user","content": body}], temperature=0.0)
    tags = []
    if raw:
        try:
            import json
            data = json.loads(raw)
            tags = [t for t in data.get("tags", []) if isinstance(t, str)]
        except Exception:
            pass
    tags = list(dict.fromkeys(tags))[:6]
    return tags

def format_sources(items):
    """출처 기사/논문 링크를 소스별로 그룹화하여 포맷팅 (게시일 포함)"""
    from collections import defaultdict
    grouped = defaultdict(list)
    
    # 소스별로 그룹화
    for it in items:
        source = it.get('source', 'Unknown')
        grouped[source].append(it)
    
    # 소스별로 포맷팅
    lines = []
    for source, articles in sorted(grouped.items()):
        lines.append(f"\n[{source}]")
        for i, art in enumerate(articles, 1):
            title = art.get('title', 'No title')[:80]
            link = art.get('link', '')
            pub_date = art.get('published', '')
            
            # 제목 뒤에 게시일 표시 (있는 경우)
            if pub_date:
                lines.append(f"{i}. {title} ({pub_date})")
            else:
                lines.append(f"{i}. {title}")
            lines.append(f"   {link}")
    
    return "\n".join(lines)

# ---- Notion ----
def notion_append(date_str, summary_text, tags, market_text, sources_text, notion_token, notion_db_id):
    notion = NotionClient(auth=notion_token)
    
    # Description: 첫 200자만 (간단한 미리보기)
    first_line = summary_text.split('\n')[0] if summary_text else "AI 뉴스 요약"
    short_desc = first_line[:200] + "..." if len(first_line) > 200 else first_line
    
    props = {
        "Title": {"title":[{"text":{"content": f"AI InsightLens (EN/한글) – {date_str}"}}]},
        "Date": {"date":{"start":date_str}},
        "Description": {"rich_text":[{"text":{"content": short_desc}}]}
    }
    if tags:
        props["Tags"] = {"multi_select":[{"name":t} for t in tags]}
    
    # Key Findings: 출처 링크들 + 시장 데이터 (2000자 제한)
    findings_content = ""
    if sources_text:
        findings_content = f"📰 출처\n{sources_text[:1800]}"
    if market_text:
        market_section = f"\n\n📈 시장 데이터\n{market_text}"
        if len(findings_content) + len(market_section) <= 1900:
            findings_content += market_section
    
    if findings_content:
        props["Key Findings"] = {"rich_text":[{"text":{"content":findings_content[:1900]}}]}
    
    # 페이지 생성
    page = notion.pages.create(parent={"database_id": notion_db_id}, properties=props)
    page_id = page.get("id", None)
    
    # 본문에 전체 요약 추가 (제한 없음)
    if page_id and summary_text:
        children = []
        
        # 요약문을 줄 단위로 나누어 paragraph blocks 생성
        lines = summary_text.split('\n')
        for line in lines:
            if not line.strip():
                # 빈 줄은 빈 paragraph로
                children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}})
            else:
                # 텍스트가 있는 줄 (2000자 제한 있으므로 긴 줄은 분할)
                if len(line) <= 2000:
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
                    })
                else:
                    # 2000자 넘는 경우 분할
                    for i in range(0, len(line), 1900):
                        chunk = line[i:i+1900]
                        children.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}
                        })
        
        # 100개씩 나눠서 추가 (Notion API 제한)
        for i in range(0, len(children), 100):
            batch = children[i:i+100]
            try:
                notion.blocks.children.append(block_id=page_id, children=batch)
            except Exception as e:
                print(f"[WARN] Failed to append blocks batch {i//100 + 1}: {e}")
    
    return page_id

# ---- Email ----
def send_email(subject, body):
    if not EMAIL_ENABLE: 
        return False, "EMAIL_ENABLE=false"
    import smtplib
    from email.mime.text import MIMEText
    if not (EMAIL_SMTP_HOST and EMAIL_SMTP_PORT and EMAIL_USERNAME and EMAIL_PASSWORD and EMAIL_FROM and EMAIL_TO):
        return False, "Email env incomplete"
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        return True, "sent"
    except Exception as e:
        return False, str(e)

# ---- RUN ----
def run():
    date_kst = iso_date_kst()
    print(f"[Run] InsightLens – AI Only – {date_kst}")

    rss = fetch_rss()
    arxiv = fetch_arxiv()
    items = rss + arxiv
    if not items:
        items = [{"title":"No items","source":"System","link":"","summary":"데이터 없음","published":""}]

    # 시장 데이터를 먼저 가져와서 요약에 포함
    market = fetch_market()
    summary = summarize(items, market)
    tags = classify_tags(items, summary)
    sources = format_sources(items)

    text_block = f"""[AI InsightLens – {date_kst}]
🧠 AI 요약
{summary}

🏷 태그: {", ".join(tags) if tags else "N/A"}
📈 시장: {market}

📰 출처
{sources}
"""

    page_id = notion_append(date_kst, summary, tags, market, sources, NOTION_TOKEN, NOTION_DB_ID)
    print("[OK] Notion page:", page_id)

    # 요약문을 파일로 저장 (쇼츠 생성용)
    summary_file = f"summary_{date_kst}.txt"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"[SAVE] Summary saved: {summary_file}")
    except Exception as e:
        print(f"[WARN] Failed to save summary: {e}")
    
    # 원문 기사 정보를 JSON으로 저장 (쇼츠 출처용)
    import json
    sources_file = f"sources_{date_kst}.json"
    try:
        sources_data = {
            "articles": [{
                "title": item.get("title", "")[:100],
                "source": item.get("source", "Unknown"),
                "published": item.get("published", date_kst),
                "link": item.get("link", "")
            } for item in items[:10]],  # 최대 10개
            "market": market  # 시장 데이터 추가
        }
        
        with open(sources_file, 'w', encoding='utf-8') as f:
            json.dump(sources_data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] Sources saved: {sources_file}")
    except Exception as e:
        print(f"[WARN] Failed to save sources: {e}")

    ok_e, info_e = send_email(subject=f"[InsightLens AI] {date_kst}", body=text_block)
    print("[Email]", ok_e, info_e)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        try:
            print("[FATAL]", str(e))
        except UnicodeEncodeError:
            print("[FATAL] Error occurred (encoding issue)")
        traceback.print_exc()
        sys.exit(2)
