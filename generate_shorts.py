#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Shorts 자동 생성 스크립트 v2
- 섹션별 TTS로 완벽한 화면-음성 동기화
- 원문 기사 정보 하단 표시
- 주가 정보 슬라이드 포함
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from moviepy.editor import *
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

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

def extract_shorts_content(summary_text, language="en"):
    """
    요약문에서 쇼츠용 핵심 내용 추출 (3-4개 포인트)
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    if language == "en":
        prompt = f"""From the following AI news summary, extract 3-4 MOST IMPORTANT KEY POINTS for a 60-second YouTube Short.

SELECTION CRITERIA (prioritize in this order):
1. **Breaking news**: New product launches, model releases, major announcements
2. **Market impact**: Funding rounds, M&A, IPOs, major partnerships
3. **Technical breakthroughs**: Research papers, performance improvements
4. **Industry trends**: Regulatory changes, workforce shifts, emerging patterns

For EACH point, return in this format:
• [SOURCE_NAME] Statement here (max 15 words)

Where SOURCE_NAME is the blog/company mentioned (e.g., OpenAI, DeepMind, VentureBeat, etc.)

Requirements:
- Clear, impactful statements
- Newsworthy and engaging
- Simple, conversational English
- Prioritize recency and significance

Summary:
{summary_text[:2000]}

Return ONLY the formatted bullet points (3-4 points), one per line."""
    else:  # Korean
        prompt = f"""다음 AI 뉴스 요약에서 60초 유튜브 쇼츠용 핵심 내용 3-4개를 추출하세요.

각 포인트를 다음 형식으로 반환:
• [소스명] 내용 (최대 15단어)

소스명은 언급된 블로그/회사 (예: OpenAI, DeepMind, VentureBeat 등)

요구사항:
- 명확하고 임팩트 있는 문장
- 뉴스 가치 있고 흥미로운 내용
- 간단한 대화체

요약:
{summary_text[:2000]}

형식에 맞춘 bullet point만 반환하세요."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    content = response.choices[0].message.content.strip()
    
    # 포인트와 출처 분리
    results = []
    for line in content.split("\n"):
        if line.strip().startswith("•"):
            clean_line = line.strip("• ").strip()
            # [SOURCE] content 형식 파싱
            if clean_line.startswith("[") and "]" in clean_line:
                close_bracket = clean_line.index("]")
                source = clean_line[1:close_bracket]
                point_text = clean_line[close_bracket+1:].strip()
                results.append({"text": point_text, "source": source})
            else:
                results.append({"text": clean_line, "source": "Unknown"})
    
    return results[:4]  # 최대 4개

def generate_tts(text, output_path, language="en"):
    """
    OpenAI TTS로 음성 생성
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    voice = "alloy" if language == "en" else "nova"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    
    response.stream_to_file(output_path)
    return output_path

def create_gradient_background(size=(1080, 1920), color1=(15, 23, 42), color2=(42, 15, 42)):
    """
    그라디언트 배경 생성
    """
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    # 수직 그라디언트
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return img

def create_text_image(text, size=(1080, 1920), bg_color=(20, 20, 40), text_color=(255, 255, 255), fontsize=70, footer_text=None, use_gradient=True):
    """
    PIL로 멋진 텍스트 이미지 생성
    """
    # 그라디언트 배경 또는 단색
    if use_gradient:
        color2 = (bg_color[0] + 20, bg_color[1] + 10, bg_color[2] + 30)
        img = create_gradient_background(size, bg_color, color2)
    else:
        img = Image.new('RGB', size, color=bg_color)
    
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드 (굵은 폰트 시도)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", fontsize)  # Arial Bold
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", fontsize)
            small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # 텍스트 줄바꿈
    max_chars = 25 if fontsize > 60 else 30
    wrapped_lines = []
    for line in text.split('\n'):
        if line.strip():
            wrapped_lines.extend(textwrap.wrap(line, width=max_chars))
        else:
            wrapped_lines.append("")
    
    # 텍스트 중앙 정렬
    y_offset = (size[1] - len(wrapped_lines) * (fontsize + 25)) // 2
    
    for i, line in enumerate(wrapped_lines):
        if not line:
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        y = y_offset + i * (fontsize + 25)
        
        # 진한 그림자 (3겹)
        draw.text((x+4, y+4), line, font=font, fill=(0, 0, 0, 200))
        draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 150))
        # 메인 텍스트
        draw.text((x, y), line, font=font, fill=text_color)
    
    # 하단 출처 정보 (박스 배경)
    if footer_text:
        footer_lines = textwrap.wrap(footer_text, width=50)
        footer_y = size[1] - 200 - (len(footer_lines) * 35)
        
        # 반투명 박스 배경
        box_height = len(footer_lines) * 35 + 20
        draw.rectangle([(40, footer_y - 10), (size[0] - 40, footer_y + box_height)], 
                      fill=(0, 0, 0), outline=(80, 80, 80), width=2)
        
        for i, line in enumerate(footer_lines):
            bbox = draw.textbbox((0, 0), line, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            y = footer_y + i * 35
            draw.text((x, y), line, font=small_font, fill=(200, 200, 200))
    
    return img

def create_market_image_pro(market_data, size=(1080, 1920), bg_color=(15, 23, 42)):
    """
    전문적인 주가 화면 - 바 그래프 + 색상 구분
    """
    # 다크 그라디언트 배경
    img = create_gradient_background(size, (10, 15, 30), (30, 20, 50))
    draw = ImageDraw.Draw(img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 75)
        ticker_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 55)
        pct_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    except:
        title_font = ImageFont.load_default()
        ticker_font = ImageFont.load_default()
        pct_font = ImageFont.load_default()
    
    # 제목
    title = "AI STOCK MARKET"
    subtitle = "Today's Performance"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    
    # 그림자 + 제목
    for offset in [4, 2]:
        draw.text(((size[0] - title_width) // 2 + offset, 120 + offset), title, font=title_font, fill=(0, 0, 0))
    draw.text(((size[0] - title_width) // 2, 120), title, font=title_font, fill=(255, 215, 0))
    
    bbox_sub = draw.textbbox((0, 0), subtitle, font=ticker_font)
    sub_width = bbox_sub[2] - bbox_sub[0]
    draw.text(((size[0] - sub_width) // 2, 210), subtitle, font=ticker_font, fill=(180, 180, 255))
    
    # 주가 데이터 파싱 및 정렬
    items_data = []
    for item in market_data.split(" | ")[:7]:
        try:
            ticker = item.split(":")[0].strip()
            price = item.split(":")[1].split("(")[0].strip()
            if "(" in item:
                pct_str = item.split("(")[1].split(")")[0]
                pct = float(pct_str.replace("+", "").replace("%", ""))
                if "+" in pct_str:
                    items_data.append({"ticker": ticker, "price": price, "pct": pct, "direction": "up"})
                else:
                    items_data.append({"ticker": ticker, "price": price, "pct": -pct, "direction": "down"})
            else:
                items_data.append({"ticker": ticker, "price": price, "pct": 0, "direction": "flat"})
        except:
            pass
    
    # 퍼센트 순으로 정렬
    items_data.sort(key=lambda x: x['pct'], reverse=True)
    
    # 바 그래프 그리기
    y_start = 350
    bar_height = 60
    max_bar_width = 450  # 화면 안전 영역 고려
    max_pct = max([abs(d['pct']) for d in items_data]) if items_data else 1
    
    for i, data in enumerate(items_data):
        y = y_start + i * 110
        
        # 티커 (왼쪽)
        draw.text((60, y + 10), data['ticker'], font=ticker_font, fill=(255, 255, 255))
        
        # 바 그래프 (스케일링 개선)
        bar_width = int((abs(data['pct']) / max_pct) * max_bar_width)
        bar_x_start = 380
        
        if data['direction'] == "up":
            bar_color = (50, 255, 100)  # 밝은 초록
            border_color = (30, 200, 80)
            symbol = "▲"
        elif data['direction'] == "down":
            bar_color = (255, 80, 80)  # 밝은 빨강
            border_color = (200, 40, 40)
            symbol = "▼"
        else:
            bar_color = (150, 150, 150)
            border_color = (100, 100, 100)
            symbol = "━"
        
        # 바 그리기 (테두리 + 채우기)
        if bar_width > 0:
            draw.rectangle([bar_x_start, y + 15, bar_x_start + bar_width, y + bar_height - 5], 
                          fill=bar_color, outline=border_color, width=3)
        
        # 퍼센트 표시 (바 오른쪽, 안전 영역)
        pct_text = f"{symbol} {data['pct']:+.1f}%"
        pct_x = min(bar_x_start + bar_width + 20, 900)  # 최대 x 위치 제한
        draw.text((pct_x, y + 10), pct_text, font=pct_font, fill=bar_color)
    
    return img

def generate_short(points, output_path, title, language="en", date_str=None, sources=None, market_data=None, output_dir="shorts_output"):
    """
    쇼츠 영상 생성 - 섹션별 개별 TTS로 완벽한 동기화
    """
    bg_color = (15, 23, 42) if language == "en" else (25, 15, 42)
    
    clips = []
    temp_files = []
    
    print(f"\n[VIDEO] Creating {language.upper()} short...")
    
    # 1. 인트로 (2초, 음성 없음) - 화려한 디자인
    intro_img = create_gradient_background(size=(1080, 1920), 
                                          color1=(10, 30, 60), 
                                          color2=(60, 20, 80))
    draw = ImageDraw.Draw(intro_img)
    
    # 폰트
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 95)
        date_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 55)
    except:
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # 제목
    title_text = "AI NEWS TODAY"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = bbox[2] - bbox[0]
    x = (1080 - title_width) // 2
    y = 800
    
    # 글로우 효과 (여러 겹 그림자)
    for offset in [8, 6, 4]:
        draw.text((x+offset, y+offset), title_text, font=title_font, fill=(100, 100, 255, 100))
    draw.text((x, y), title_text, font=title_font, fill=(255, 255, 100))
    
    # 날짜
    if date_str:
        bbox_date = draw.textbbox((0, 0), date_str, font=date_font)
        date_width = bbox_date[2] - bbox_date[0]
        draw.text(((1080 - date_width) // 2, 950), date_str, font=date_font, fill=(200, 200, 255))
    
    intro_path = f"{output_dir}/temp_intro.png"
    intro_img.save(intro_path)
    temp_files.append(intro_path)
    
    intro_clip = ImageClip(intro_path).set_duration(2).fx(fadein, 0.5)
    clips.append(intro_clip)
    
    # 2. 각 포인트 (개별 TTS)
    for i, point_data in enumerate(points, 1):
        point_text = point_data.get('text', '') if isinstance(point_data, dict) else str(point_data)
        
        # 개별 TTS 생성
        point_audio_path = f"{output_dir}/temp_point_{i}.mp3"
        generate_tts(point_text, point_audio_path, language)
        temp_files.append(point_audio_path)
        
        # 음성 길이 측정
        audio_clip = AudioFileClip(point_audio_path)
        duration = audio_clip.duration + 0.5  # 여유
        audio_clip.close()
        
        # 화면 생성 (더 큰 폰트, 그라디언트 배경)
        text = f"{i}.\n\n{point_text}"
        footer = None
        if sources and len(sources) >= i:
            article = sources[i-1]
            footer = f"{article.get('title', '')[:60]}\n{article.get('source', '')} | {article.get('published', '')}"
        
        # 포인트별로 약간 다른 그라디언트
        point_bg = (bg_color[0] + i*3, bg_color[1] + i*2, bg_color[2] + i*5)
        img = create_text_image(text, bg_color=point_bg, fontsize=65, footer_text=footer, use_gradient=True)
        img_path = f"{output_dir}/temp_point_{i}.png"
        img.save(img_path)
        temp_files.append(img_path)
        
        # 비디오+오디오 클립 (페이드 효과)
        vid_clip = ImageClip(img_path).set_duration(duration)
        vid_clip = vid_clip.fx(fadein, 0.2).fx(fadeout, 0.2)  # 부드러운 전환
        vid_clip = vid_clip.set_audio(AudioFileClip(point_audio_path))
        clips.append(vid_clip)
        print(f"  Point {i}: {duration:.1f}s")
    
    # 3. 주가 정보 (개별 TTS) - 요약 버전
    if market_data and market_data != "N/A":
        market_items = market_data.split(" | ")
        
        # 주가 분석 및 요약
        up_stocks = []
        down_stocks = []
        for item in market_items:
            try:
                ticker = item.split(":")[0].strip()
                if "(+" in item:
                    pct = float(item.split("(+")[1].split("%")[0])
                    up_stocks.append((ticker, pct))
                elif "(-" in item:
                    pct = float(item.split("(-")[1].split("%")[0])
                    down_stocks.append((ticker, pct))
            except:
                pass
        
        # 가장 큰 상승/하락
        up_stocks.sort(key=lambda x: x[1], reverse=True)
        down_stocks.sort(key=lambda x: x[1], reverse=True)
        
        # 요약 스크립트 (전체 트렌드 + 특징)
        market_script = "Now the AI stock market snapshot. "
        
        if len(up_stocks) > len(down_stocks):
            market_script += "Overall positive trend today. "
        elif len(down_stocks) > len(up_stocks):
            market_script += "Mixed signals in the market today. "
        else:
            market_script += "Markets showing balanced performance. "
        
        # 최대 상승 종목
        if up_stocks:
            top_up = up_stocks[0]
            market_script += f"{top_up[0]} led gains with {top_up[1]:.1f} percent up. "
            if len(up_stocks) > 1:
                market_script += f"{up_stocks[1][0]} also rose. "
        
        # 최대 하락 종목 (있으면)
        if down_stocks:
            top_down = down_stocks[0]
            market_script += f"{top_down[0]} down {top_down[1]:.1f} percent. "
        
        market_script += "Stay tuned for more updates."
        
        # TTS 생성
        market_audio_path = f"{output_dir}/temp_market.mp3"
        generate_tts(market_script, market_audio_path, language)
        temp_files.append(market_audio_path)
        
        # 음성 길이
        market_audio = AudioFileClip(market_audio_path)
        market_duration = market_audio.duration + 0.5
        market_audio.close()
        
        # 화면 생성 (전문적인 바 그래프)
        market_img = create_market_image_pro(market_data, bg_color=bg_color)
        market_img_path = f"{output_dir}/temp_market.png"
        market_img.save(market_img_path)
        temp_files.append(market_img_path)
        
        # 페이드 인 효과
        market_clip = ImageClip(market_img_path).set_duration(market_duration)
        market_clip = market_clip.fx(fadein, 0.3).fx(fadeout, 0.3)  # 부드러운 전환
        market_clip = market_clip.set_audio(AudioFileClip(market_audio_path))
        clips.append(market_clip)
        print(f"  Market: {market_duration:.1f}s")
    
    # 4. 아웃트로 (개별 TTS) - 화려한 디자인
    outro_text = "Follow for more AI updates!" if language == "en" else "팔로우하세요!"
    outro_audio_path = f"{output_dir}/temp_outro.mp3"
    generate_tts(outro_text, outro_audio_path, language)
    temp_files.append(outro_audio_path)
    
    outro_audio = AudioFileClip(outro_audio_path)
    outro_duration = outro_audio.duration + 0.5
    outro_audio.close()
    
    # 화려한 아웃트로 화면
    outro_img = create_gradient_background(size=(1080, 1920), 
                                          color1=(80, 20, 60), 
                                          color2=(20, 40, 80))
    draw = ImageDraw.Draw(outro_img)
    
    try:
        outro_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 75)
        sub_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 45)
    except:
        outro_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
    
    # 메시지
    msg1 = "FOLLOW FOR MORE"
    msg2 = "AI UPDATES DAILY"
    
    # 텍스트 위치
    bbox1 = draw.textbbox((0, 0), msg1, font=outro_font)
    width1 = bbox1[2] - bbox1[0]
    bbox2 = draw.textbbox((0, 0), msg2, font=sub_font)
    width2 = bbox2[2] - bbox2[0]
    
    # 그림자 효과
    for offset in [6, 4, 2]:
        draw.text(((1080 - width1) // 2 + offset, 820 + offset), msg1, font=outro_font, fill=(0, 0, 0))
    draw.text(((1080 - width1) // 2, 820), msg1, font=outro_font, fill=(255, 215, 0))
    draw.text(((1080 - width2) // 2, 930), msg2, font=sub_font, fill=(255, 255, 150))
    
    outro_img_path = f"{output_dir}/temp_outro.png"
    outro_img.save(outro_img_path)
    temp_files.append(outro_img_path)
    
    outro_clip = ImageClip(outro_img_path).set_duration(outro_duration)
    outro_clip = outro_clip.fx(fadein, 0.3).fx(fadeout, 0.5)  # 부드럽게 사라짐
    outro_clip = outro_clip.set_audio(AudioFileClip(outro_audio_path))
    clips.append(outro_clip)
    print(f"  Outro: {outro_duration:.1f}s")
    
    # 5. 최종 영상 합성
    final_clip = concatenate_videoclips(clips, method="compose")
    total_duration = final_clip.duration
    print(f"  Total: {total_duration:.1f}s")
    
    # 6. 배경 음악 추가 (선택적)
    bg_music_path = f"{output_dir}/background_music.mp3"
    if os.path.exists(bg_music_path):
        try:
            from moviepy.audio.AudioClip import CompositeAudioClip
            
            # 기존 오디오
            original_audio = final_clip.audio
            
            # 배경 음악 로드 및 볼륨 조절
            bg_music = AudioFileClip(bg_music_path).volumex(0.15)  # 15% 볼륨
            
            # 영상 길이에 맞춰 음악 자르거나 반복
            if bg_music.duration < total_duration:
                # 음악을 반복
                repeats = int(total_duration / bg_music.duration) + 1
                bg_music = concatenate_audioclips([bg_music] * repeats)
            bg_music = bg_music.subclip(0, total_duration)
            
            # 오디오 믹스 (TTS + 배경음악)
            final_audio = CompositeAudioClip([original_audio, bg_music])
            final_clip = final_clip.set_audio(final_audio)
            print(f"  Background music added (15% volume)")
        except Exception as e:
            print(f"  [WARN] Failed to add background music: {e}")
    
    # 영상 저장
    final_clip.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='ultrafast',
        threads=4
    )
    
    # 임시 파일 정리
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except:
            pass
    
    print(f"[VIDEO] Generated: {output_path}")
    return output_path

def main(summary_file, output_dir="shorts_output"):
    """
    메인 실행 함수
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # 요약문 읽기
    with open(summary_file, 'r', encoding='utf-8') as f:
        full_summary = f.read()
    
    # 날짜 추출
    import re, json
    from datetime import datetime
    
    date_match = re.search(r'summary_(\d{4}-\d{2}-\d{2})', summary_file)
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
    
    # 원문 기사 정보 및 시장 데이터 읽기
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
    
    # 영어/한글 분리
    parts = full_summary.split("**[KOREAN VERSION]**")
    english_summary = parts[0].replace("**[ENGLISH VERSION]**", "").strip() if len(parts) > 0 else ""
    korean_summary = parts[1].strip() if len(parts) > 1 else ""
    
    results = []
    
    # 영어 쇼츠 생성
    if english_summary:
        print("\n=== Generating English Short ===")
        en_points = extract_shorts_content(english_summary, "en")
        print(f"Key points extracted: {len(en_points)} items")
        
        en_video = f"{output_dir}/english_short_{date_str}.mp4"
        generate_short(en_points, en_video, "AI News Today", "en", 
                      date_str=date_str, sources=source_articles, market_data=market_data, output_dir=output_dir)
        results.append(("en", en_video))
    
    # 한글 쇼츠 (주석 처리 - 영어만)
    # if korean_summary:
    #     print("\n=== Generating Korean Short ===")
    #     ko_points = extract_shorts_content(korean_summary, "ko")
    #     ko_video = f"{output_dir}/korean_short_{date_str}.mp4"
    #     generate_short(ko_points, ko_video, "AI News", "ko", 
    #                   date_str=date_str, sources=source_articles, market_data=market_data, output_dir=output_dir)
    #     results.append(("ko", ko_video))
    
    print("\n=== All shorts generated! ===")
    for lang, video_path in results:
        print(f"  [{lang.upper()}] {video_path}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_shorts.py <summary_file>")
        sys.exit(1)
    
    summary_file = sys.argv[1]
    main(summary_file)
