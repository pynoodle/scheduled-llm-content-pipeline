#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카드뉴스 이미지 생성 스크립트 (Instagram/Threads용)
- 요약문에서 핵심 내용 추출
- 1080x1080 정사각형 카드뉴스 생성
- 화려한 디자인 + 해시태그
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import json

# ---- ENV LOADER ----
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

# 환경변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def extract_cardnews_content(summary_text, language="en", max_slides=5):
    """
    요약문에서 카드뉴스용 핵심 내용 추출 (3-5개 슬라이드)
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    if language == "en":
        prompt = f"""From the following AI news summary, extract {max_slides-2} MOST IMPORTANT KEY POINTS for Instagram/Threads card news.

SELECTION CRITERIA (prioritize in this order):
1. **Breaking news**: New product launches, model releases, major announcements
2. **Market impact**: Funding rounds, M&A, IPOs, major partnerships
3. **Technical breakthroughs**: Research papers, performance improvements
4. **Industry trends**: Regulatory changes, workforce shifts, emerging patterns

For EACH point, return in this JSON format:
{{
  "title": "Short catchy title (max 40 chars)",
  "content": "Main content (max 120 chars)",
  "source": "Source name (e.g., OpenAI, DeepMind, VentureBeat)"
}}

Requirements:
- Clear, impactful statements
- Newsworthy and engaging
- Social media friendly language
- Prioritize visual appeal and shareability

Summary:
{summary_text[:2000]}

Return ONLY a JSON array of {max_slides-2} items (no intro slide, no outro slide - they will be auto-generated)."""
    else:  # Korean
        prompt = f"""다음 AI 뉴스 요약에서 Instagram/Threads 카드뉴스용 핵심 내용 {max_slides-2}개를 추출하세요.

각 포인트를 다음 JSON 형식으로 반환:
{{
  "title": "짧고 임팩트 있는 제목 (최대 40자)",
  "content": "주요 내용 (최대 120자)",
  "source": "출처 (예: OpenAI, DeepMind, VentureBeat)"
}}

요구사항:
- 명확하고 임팩트 있는 문장
- 뉴스 가치 있고 흥미로운 내용
- SNS 친화적인 언어
- 공유하기 좋은 내용

요약:
{summary_text[:2000]}

{max_slides-2}개 항목의 JSON 배열만 반환하세요 (인트로/아웃트로 제외 - 자동 생성됨)."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    content = response.choices[0].message.content.strip()
    
    # JSON 파싱
    try:
        # ```json 블록 제거
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        items = json.loads(content)
        return items[:max_slides-2]  # 인트로/아웃트로 제외
    except:
        # 파싱 실패 시 빈 리스트
        print("[WARN] Failed to parse JSON, using fallback extraction")
        return []

def create_gradient_background_square(size=(1080, 1080), color1=(15, 23, 42), color2=(42, 15, 42)):
    """
    정사각형 그라디언트 배경 생성
    """
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    # 대각선 그라디언트
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return img

def create_intro_card(date_str, language="en"):
    """
    인트로 카드 생성 (표지)
    """
    size = (1080, 1080)
    
    # 화려한 그라디언트
    img = create_gradient_background_square(size, (10, 30, 60), (80, 20, 80))
    draw = ImageDraw.Draw(img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 90)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 55)
        date_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # 제목
    if language == "en":
        main_title = "AI NEWS"
        sub_title = "TODAY"
    else:
        main_title = "AI 뉴스"
        sub_title = "오늘"
    
    # 메인 타이틀
    bbox1 = draw.textbbox((0, 0), main_title, font=title_font)
    width1 = bbox1[2] - bbox1[0]
    
    # 글로우 효과
    for offset in [8, 6, 4]:
        draw.text(((size[0] - width1) // 2 + offset, 380 + offset), main_title, 
                 font=title_font, fill=(100, 100, 255, 100))
    draw.text(((size[0] - width1) // 2, 380), main_title, 
             font=title_font, fill=(255, 255, 100))
    
    # 서브타이틀
    bbox2 = draw.textbbox((0, 0), sub_title, font=subtitle_font)
    width2 = bbox2[2] - bbox2[0]
    draw.text(((size[0] - width2) // 2, 500), sub_title, 
             font=subtitle_font, fill=(255, 215, 0))
    
    # 날짜
    if date_str:
        bbox_date = draw.textbbox((0, 0), date_str, font=date_font)
        date_width = bbox_date[2] - bbox_date[0]
        draw.text(((size[0] - date_width) // 2, 600), date_str, 
                 font=date_font, fill=(200, 200, 255))
    
    # 장식 라인
    line_y = 700
    draw.line([(200, line_y), (880, line_y)], fill=(255, 215, 0), width=4)
    
    return img

def create_content_card(item, slide_num, language="en"):
    """
    내용 카드 생성
    """
    size = (1080, 1080)
    
    # 슬라이드별로 다른 그라디언트 색상
    colors = [
        ((15, 30, 60), (60, 30, 90)),   # 파란색-보라색
        ((30, 15, 60), (90, 30, 60)),   # 보라색-분홍색
        ((15, 60, 30), (60, 90, 30)),   # 초록색-노란색
        ((60, 30, 15), (90, 60, 30)),   # 주황색-노란색
    ]
    color_pair = colors[slide_num % len(colors)]
    
    img = create_gradient_background_square(size, color_pair[0], color_pair[1])
    draw = ImageDraw.Draw(img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 65)
        content_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 45)
        source_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
        number_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 120)
    except:
        title_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
        source_font = ImageFont.load_default()
        number_font = ImageFont.load_default()
    
    # 슬라이드 번호 (워터마크 스타일)
    number_text = str(slide_num + 1)
    draw.text((50, 50), number_text, font=number_font, fill=(255, 255, 255, 60))
    
    # 제목
    title = item.get('title', '')
    title_lines = textwrap.wrap(title, width=20)
    y = 200
    
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        
        # 그림자
        draw.text((x+3, y+3), line, font=title_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 100))
        y += 80
    
    # 구분선
    y += 20
    draw.line([(150, y), (930, y)], fill=(255, 255, 255), width=3)
    y += 50
    
    # 본문
    content = item.get('content', '')
    content_lines = textwrap.wrap(content, width=28)
    
    for line in content_lines:
        bbox = draw.textbbox((0, 0), line, font=content_font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        
        # 그림자
        draw.text((x+2, y+2), line, font=content_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=content_font, fill=(255, 255, 255))
        y += 60
    
    # 출처 (하단 박스)
    source = item.get('source', 'Unknown')
    source_text = f"Source: {source}"
    
    # 반투명 박스
    box_y = 900
    draw.rectangle([(50, box_y), (1030, box_y + 80)], 
                  fill=(0, 0, 0), outline=(255, 255, 255), width=2)
    
    bbox_source = draw.textbbox((0, 0), source_text, font=source_font)
    source_width = bbox_source[2] - bbox_source[0]
    draw.text(((size[0] - source_width) // 2, box_y + 25), source_text, 
             font=source_font, fill=(200, 200, 200))
    
    return img

def create_market_card(market_data, language="en"):
    """
    주식정보 카드 생성 - 바 그래프 스타일
    """
    size = (1080, 1080)
    
    # 다크 그라디언트 배경
    img = create_gradient_background_square(size, (10, 15, 30), (30, 20, 50))
    draw = ImageDraw.Draw(img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 65)
        ticker_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 45)
        pct_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        ticker_font = ImageFont.load_default()
        pct_font = ImageFont.load_default()
    
    # 제목
    title = "AI STOCK MARKET" if language == "en" else "AI 주식 시장"
    subtitle = "Today's Performance" if language == "en" else "오늘의 성과"
    
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    
    # 그림자 + 제목
    for offset in [4, 2]:
        draw.text(((size[0] - title_width) // 2 + offset, 80 + offset), title, 
                 font=title_font, fill=(0, 0, 0))
    draw.text(((size[0] - title_width) // 2, 80), title, 
             font=title_font, fill=(255, 215, 0))
    
    bbox_sub = draw.textbbox((0, 0), subtitle, font=ticker_font)
    sub_width = bbox_sub[2] - bbox_sub[0]
    draw.text(((size[0] - sub_width) // 2, 160), subtitle, 
             font=ticker_font, fill=(180, 180, 255))
    
    # 주가 데이터 파싱 및 정렬
    items_data = []
    for item in market_data.split(" | ")[:6]:  # 최대 6개
        try:
            ticker = item.split(":")[0].strip()
            if "(" in item:
                pct_str = item.split("(")[1].split(")")[0]
                pct = float(pct_str.replace("+", "").replace("%", ""))
                if "+" in pct_str:
                    items_data.append({"ticker": ticker, "pct": pct, "direction": "up"})
                else:
                    items_data.append({"ticker": ticker, "pct": -pct, "direction": "down"})
            else:
                items_data.append({"ticker": ticker, "pct": 0, "direction": "flat"})
        except:
            pass
    
    # 퍼센트 순으로 정렬
    items_data.sort(key=lambda x: x['pct'], reverse=True)
    
    # 바 그래프 그리기
    y_start = 260
    bar_height = 50
    max_bar_width = 400
    max_pct = max([abs(d['pct']) for d in items_data]) if items_data else 1
    
    for i, data in enumerate(items_data):
        y = y_start + i * 110
        
        # 티커 (왼쪽)
        draw.text((80, y + 5), data['ticker'], font=ticker_font, fill=(255, 255, 255))
        
        # 바 그래프
        bar_width = int((abs(data['pct']) / max_pct) * max_bar_width)
        bar_x_start = 350
        
        if data['direction'] == "up":
            bar_color = (50, 255, 100)
            border_color = (30, 200, 80)
            symbol = "▲"
        elif data['direction'] == "down":
            bar_color = (255, 80, 80)
            border_color = (200, 40, 40)
            symbol = "▼"
        else:
            bar_color = (150, 150, 150)
            border_color = (100, 100, 100)
            symbol = "━"
        
        # 바 그리기
        if bar_width > 0:
            draw.rectangle([bar_x_start, y + 10, bar_x_start + bar_width, y + bar_height], 
                          fill=bar_color, outline=border_color, width=2)
        
        # 퍼센트 표시
        pct_text = f"{symbol} {data['pct']:+.1f}%"
        pct_x = min(bar_x_start + bar_width + 15, 800)
        draw.text((pct_x, y + 5), pct_text, font=pct_font, fill=bar_color)
    
    return img

def create_outro_card(hashtags, language="en"):
    """
    아웃트로 카드 생성 (마무리 + 해시태그)
    """
    size = (1080, 1080)
    
    # 화려한 그라디언트
    img = create_gradient_background_square(size, (80, 20, 60), (20, 60, 100))
    draw = ImageDraw.Draw(img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 75)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
        hashtag_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        hashtag_font = ImageFont.load_default()
    
    # 메시지
    if language == "en":
        msg1 = "FOLLOW FOR MORE"
        msg2 = "AI UPDATES DAILY"
    else:
        msg1 = "팔로우하세요"
        msg2 = "매일 AI 뉴스 업데이트"
    
    # 텍스트 위치
    bbox1 = draw.textbbox((0, 0), msg1, font=title_font)
    width1 = bbox1[2] - bbox1[0]
    bbox2 = draw.textbbox((0, 0), msg2, font=subtitle_font)
    width2 = bbox2[2] - bbox2[0]
    
    # 그림자 효과
    for offset in [6, 4, 2]:
        draw.text(((size[0] - width1) // 2 + offset, 350 + offset), msg1, 
                 font=title_font, fill=(0, 0, 0))
    draw.text(((size[0] - width1) // 2, 350), msg1, 
             font=title_font, fill=(255, 215, 0))
    draw.text(((size[0] - width2) // 2, 450), msg2, 
             font=subtitle_font, fill=(255, 255, 150))
    
    # 구분선
    draw.line([(200, 550), (880, 550)], fill=(255, 215, 0), width=4)
    
    # 해시태그
    if hashtags:
        y = 620
        hashtag_lines = textwrap.wrap(hashtags, width=30)
        
        for line in hashtag_lines[:4]:  # 최대 4줄
            bbox = draw.textbbox((0, 0), line, font=hashtag_font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            
            draw.text((x+2, y+2), line, font=hashtag_font, fill=(0, 0, 0))
            draw.text((x, y), line, font=hashtag_font, fill=(100, 200, 255))
            y += 55
    
    return img

def extract_hashtags(summary_text):
    """
    요약문에서 해시태그 추출 (마지막 줄에서)
    """
    lines = summary_text.strip().split("\n")
    for line in reversed(lines):
        if line.strip().startswith("#"):
            return line.strip()
    return "#AI #Technology #Innovation"

def generate_instagram_caption(content_items, source_articles, hashtags, date_str, language="en"):
    """
    Instagram 캡션 생성 (원문 제목 + 출처 + 날짜 포함)
    """
    if language == "en":
        caption = f"AI News Highlights - {date_str}\n\n"
        caption += "Today's top AI stories:\n\n"
        
        # 핵심 내용
        for i, item in enumerate(content_items, 1):
            title = item.get('title', '')
            caption += f"{i}. {title}\n"
        
        caption += f"\nSwipe to see details →\n\n"
        
        # 출처 정보 (원문 제목 + 날짜)
        caption += "Original Sources:\n"
        caption += "-" * 40 + "\n"
        
        for i, article in enumerate(source_articles[:5], 1):  # 최대 5개
            source = article.get('source', '')
            title = article.get('title', '')
            published = article.get('published', '')
            
            if title:
                # 제목이 너무 길면 줄바꿈
                if len(title) > 60:
                    title = title[:57] + "..."
                
                caption += f"\n{i}. {title}\n"
                
                # 출처와 날짜
                source_line = f"   {source}"
                if published:
                    source_line += f" | {published}"
                caption += f"{source_line}\n"
        
        caption += "\n" + hashtags + "\n"
        
    else:  # Korean
        caption = f"AI 뉴스 하이라이트 - {date_str}\n\n"
        caption += "오늘의 주요 AI 소식:\n\n"
        
        for i, item in enumerate(content_items, 1):
            title = item.get('title', '')
            caption += f"{i}. {title}\n"
        
        caption += f"\n자세한 내용은 스와이프 →\n\n"
        
        caption += "원문 출처:\n"
        caption += "-" * 40 + "\n"
        
        for i, article in enumerate(source_articles[:5], 1):
            source = article.get('source', '')
            title = article.get('title', '')
            published = article.get('published', '')
            
            if title:
                if len(title) > 60:
                    title = title[:57] + "..."
                
                caption += f"\n{i}. {title}\n"
                
                source_line = f"   {source}"
                if published:
                    source_line += f" | {published}"
                caption += f"{source_line}\n"
        
        caption += "\n" + hashtags + "\n"
    
    return caption

def main(summary_file, output_dir="cardnews_output", max_slides=5, language="en"):
    """
    메인 실행 함수
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # 요약문 읽기
    with open(summary_file, 'r', encoding='utf-8') as f:
        full_summary = f.read()
    
    # 날짜 추출
    import re
    from datetime import datetime
    
    date_match = re.search(r'summary_(\d{4}-\d{2}-\d{2})', summary_file)
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
    
    # 영어/한글 분리
    parts = full_summary.split("**[KOREAN VERSION]**")
    english_summary = parts[0].replace("**[ENGLISH VERSION]**", "").strip() if len(parts) > 0 else ""
    korean_summary = parts[1].strip() if len(parts) > 1 else ""
    
    # 언어별 처리
    if language == "en":
        summary_text = english_summary
    else:
        summary_text = korean_summary
    
    if not summary_text:
        print(f"[ERROR] No {language} summary found")
        return []
    
    print(f"\n=== Generating {language.upper()} Card News ===")
    
    # 원문 기사 및 시장 데이터 읽기
    sources_file = summary_file.replace('summary_', 'sources_').replace('.txt', '.json')
    source_articles = []
    market_data = None
    
    if os.path.exists(sources_file):
        try:
            with open(sources_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                source_articles = data.get('articles', [])
                market_data = data.get('market', None)
            else:
                source_articles = data
            
            print(f"[INFO] Loaded {len(source_articles)} source articles")
            if market_data:
                print(f"[INFO] Market data loaded")
        except Exception as e:
            print(f"[WARN] Failed to load sources: {e}")
    
    # 핵심 내용 추출
    content_items = extract_cardnews_content(summary_text, language, max_slides)
    print(f"Key points extracted: {len(content_items)} items")
    
    # 해시태그 추출
    hashtags = extract_hashtags(summary_text)
    print(f"Hashtags: {hashtags}")
    
    # 슬라이드 생성
    slides = []
    
    # 총 슬라이드 수 계산 (인트로 + 콘텐츠 + 주식 + 아웃트로)
    total_slides = len(content_items) + 2 + (1 if market_data else 0)
    
    # 1. 인트로
    print(f"[1/{total_slides}] Creating intro card...")
    intro = create_intro_card(date_str, language)
    intro_path = f"{output_dir}/{language}_card_00_intro_{date_str}.png"
    intro.save(intro_path, quality=95)
    slides.append(intro_path)
    
    # 2. 내용 카드들
    for i, item in enumerate(content_items, 1):
        print(f"[{i+1}/{total_slides}] Creating content card {i}...")
        card = create_content_card(item, i-1, language)
        card_path = f"{output_dir}/{language}_card_{i:02d}_{date_str}.png"
        card.save(card_path, quality=95)
        slides.append(card_path)
    
    # 3. 주식정보 카드 (있을 경우)
    if market_data and market_data != "N/A":
        market_idx = len(content_items) + 1
        print(f"[{market_idx+1}/{total_slides}] Creating market card...")
        market_card = create_market_card(market_data, language)
        market_path = f"{output_dir}/{language}_card_{market_idx:02d}_market_{date_str}.png"
        market_card.save(market_path, quality=95)
        slides.append(market_path)
    
    # 4. 아웃트로
    outro_idx = len(slides)
    print(f"[{total_slides}/{total_slides}] Creating outro card...")
    outro = create_outro_card(hashtags, language)
    outro_path = f"{output_dir}/{language}_card_{outro_idx:02d}_outro_{date_str}.png"
    outro.save(outro_path, quality=95)
    slides.append(outro_path)
    
    print(f"\n[OK] Card news generated: {len(slides)} slides")
    for slide in slides:
        print(f"  - {slide}")
    
    # Instagram 캡션 생성 및 저장
    caption = generate_instagram_caption(content_items, source_articles, hashtags, date_str, language)
    caption_path = f"{output_dir}/{language}_caption_{date_str}.txt"
    
    with open(caption_path, 'w', encoding='utf-8') as f:
        f.write(caption)
    
    print(f"\n[CAPTION] Instagram caption saved: {caption_path}")
    print("=" * 60)
    # PowerShell 인코딩 문제 방지
    try:
        print(caption)
    except UnicodeEncodeError:
        print("[Caption preview skipped due to encoding - check the .txt file]")
    print("=" * 60)
    
    return slides

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Instagram/Threads card news")
    parser.add_argument("summary_file", help="Path to summary text file")
    parser.add_argument("--lang", choices=["en", "ko"], default="en", 
                       help="Language (default: en)")
    parser.add_argument("--slides", type=int, default=5, 
                       help="Max number of slides (default: 5)")
    parser.add_argument("--output", default="cardnews_output", 
                       help="Output directory (default: cardnews_output)")
    
    args = parser.parse_args()
    
    main(args.summary_file, args.output, args.slides, args.lang)

