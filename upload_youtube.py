#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Shorts 자동 업로드 스크립트
OAuth 인증 후 자동 업로드
"""

import os
import sys
import pickle
import argparse
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# OAuth 2.0 Scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Credentials 파일 경로
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_PICKLE_FILE = "token.pickle"

def get_authenticated_service():
    """
    YouTube API 인증 및 서비스 객체 반환
    token.pickle이 있으면 재사용, 없으면 새로 인증
    """
    creds = None
    
    # 기존 토큰 로드
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 토큰이 없거나 유효하지 않으면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"❌ {CLIENT_SECRETS_FILE} not found!\n"
                    "Please download OAuth credentials from Google Cloud Console.\n"
                    "See YOUTUBE_AUTOMATION.md for setup instructions."
                )
            
            print("Starting OAuth authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
        try:
            print(f"✅ Token saved to {TOKEN_PICKLE_FILE}")
        except UnicodeEncodeError:
            print(f"[OK] Token saved to {TOKEN_PICKLE_FILE}")
    
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_file, title, description, tags, category_id="28", 
                privacy_status="public", made_for_kids=False):
    """
    YouTube에 영상 업로드
    
    Args:
        youtube: YouTube API 서비스 객체
        video_file: 업로드할 영상 파일 경로
        title: 영상 제목
        description: 영상 설명
        tags: 태그 리스트
        category_id: 카테고리 (28=Science & Technology)
        privacy_status: public/private/unlisted
        made_for_kids: 어린이용 콘텐츠 여부
    
    Returns:
        video_id: 업로드된 영상 ID
    """
    
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': made_for_kids
        }
    }
    
    # 미디어 파일 업로드
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, 
                           mimetype='video/mp4')
    
    try:
        print(f"\n📤 Uploading: {os.path.basename(video_file)}")
    except UnicodeEncodeError:
        print(f"\n[UPLOAD] Uploading: {os.path.basename(video_file)}")
    print(f"   Title: {title}")
    print(f"   Tags: {', '.join(tags[:5])}...")
    
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Progress: {progress}%")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                print(f"   Retrying after HTTP {e.resp.status} error...")
                continue
            else:
                raise
    
    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        print(f"\n✅ Upload successful!")
    except UnicodeEncodeError:
        print(f"\n[SUCCESS] Upload successful!")
    print(f"   Video ID: {video_id}")
    print(f"   URL: {video_url}")
    
    return video_id, video_url

def create_video_metadata(language="en", date_str=None):
    """
    영상 메타데이터 생성
    
    Args:
        language: en/ko
        date_str: 날짜 (YYYY-MM-DD)
    
    Returns:
        (title, description, tags)
    """
    
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    if language == "ko":
        title = f"오늘의 AI 뉴스 요약 ({date_str}) #Shorts"
        description = f"""오늘의 AI 뉴스를 60초로 요약했습니다.

📅 {date_str}
🤖 AI 연구, 빅테크, 투자, 시장 동향

주요 소스:
- arXiv AI 논문
- OpenAI, Anthropic, Google DeepMind 블로그
- TechCrunch, VentureBeat
- 주요 AI 기업 주가

자동 생성: AI InsightLens
GitHub: https://github.com/pynoodle/AI_InsightLens

#AI #인공지능 #기술뉴스 #Shorts #오늘의뉴스 #GPT #머신러닝 #딥러닝
"""
        tags = [
            "AI", "인공지능", "기술뉴스", "오늘의뉴스", "Shorts",
            "머신러닝", "딥러닝", "GPT", "ChatGPT", "OpenAI",
            "빅테크", "테크뉴스", "IT뉴스", "주식", "투자"
        ]
    
    else:  # English
        title = f"AI News Summary ({date_str}) #Shorts"
        description = f"""Today's AI news in 60 seconds.

📅 {date_str}
🤖 AI Research, Big Tech, Investment, Market Trends

Key Sources:
- arXiv AI Papers
- OpenAI, Anthropic, Google DeepMind Blogs
- TechCrunch, VentureBeat
- AI Stock Market Snapshot

Auto-generated by AI InsightLens
GitHub: https://github.com/pynoodle/AI_InsightLens

#AI #ArtificialIntelligence #Tech #Shorts #News #GPT #MachineLearning #DeepLearning
"""
        tags = [
            "AI", "Artificial Intelligence", "Tech News", "Shorts", "Daily News",
            "Machine Learning", "Deep Learning", "GPT", "ChatGPT", "OpenAI",
            "Big Tech", "Tech", "Technology", "Stocks", "Investment",
            "AI Research", "Google", "Microsoft", "NVIDIA"
        ]
    
    return title, description, tags

def main(video_path=None, language="en", date_str=None):
    """
    메인 함수
    
    Args:
        video_path: 업로드할 영상 경로
        language: en/ko
        date_str: 날짜 (YYYY-MM-DD)
    
    Returns:
        video_url: 업로드된 영상 URL
    """
    
    # 인증
    youtube = get_authenticated_service()
    
    # 영상 경로 확인
    if not video_path:
        # 기본: 오늘 날짜 영상
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        lang_prefix = "korean" if language == "ko" else "english"
        video_path = f"shorts_output/{lang_prefix}_short_{date_str}.mp4"
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    # 메타데이터 생성
    title, description, tags = create_video_metadata(language, date_str)
    
    # 업로드
    video_id, video_url = upload_video(
        youtube=youtube,
        video_file=video_path,
        title=title,
        description=description,
        tags=tags,
        category_id="28",  # Science & Technology
        privacy_status="public",  # 즉시 공개
        made_for_kids=False
    )
    
    return video_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload AI InsightLens Shorts to YouTube"
    )
    parser.add_argument(
        "video_path", 
        nargs="?",
        help="Path to video file (default: today's shorts_output/english_short_YYYY-MM-DD.mp4)"
    )
    parser.add_argument(
        "language",
        nargs="?",
        default="en",
        choices=["en", "ko"],
        help="Language: en (English) or ko (Korean)"
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Date in YYYY-MM-DD format (default: today)"
    )
    
    args = parser.parse_args()
    
    try:
        video_url = main(args.video_path, args.language, args.date)
        try:
            print(f"\n🎉 Success! Video uploaded to YouTube")
            print(f"🔗 {video_url}\n")
        except UnicodeEncodeError:
            print(f"\n[SUCCESS] Video uploaded to YouTube")
            print(f"URL: {video_url}\n")
        sys.exit(0)
        
    except FileNotFoundError as e:
        try:
            print(f"\n❌ {e}\n")
        except UnicodeEncodeError:
            print(f"\n[ERROR] {e}\n")
        sys.exit(1)
        
    except HttpError as e:
        try:
            print(f"\n❌ YouTube API Error: {e}\n")
        except UnicodeEncodeError:
            print(f"\n[ERROR] YouTube API Error: {e}\n")
        sys.exit(1)
        
    except Exception as e:
        try:
            print(f"\n❌ Unexpected error: {e}\n")
        except UnicodeEncodeError:
            print(f"\n[ERROR] Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
