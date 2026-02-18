#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions에서 생성된 쇼츠를 다운로드하고 YouTube에 업로드
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path

def download_latest_artifact():
    """
    GitHub Actions에서 생성된 최신 artifact 다운로드
    
    Note: GitHub CLI (gh) 사용
    """
    
    print("📥 Downloading latest shorts from GitHub Actions...")
    
    # GitHub CLI로 최신 artifact 다운로드
    os.system('gh run download --name daily-shorts --dir downloads')
    
    # 다운로드된 파일 확인
    download_dir = Path("downloads")
    if not download_dir.exists():
        print("❌ Download directory not found")
        return None
    
    # 최신 .mp4 파일 찾기
    mp4_files = list(download_dir.glob("**/*.mp4"))
    if not mp4_files:
        print("❌ No video files found in downloads")
        return None
    
    # 가장 최근 파일
    latest_video = max(mp4_files, key=lambda p: p.stat().st_mtime)
    print(f"✅ Found: {latest_video}")
    
    return str(latest_video)

def main():
    """
    메인 함수
    """
    
    # 1. GitHub Actions에서 artifact 다운로드
    video_path = download_latest_artifact()
    
    if not video_path:
        print("\n⚠️  No video to upload. Exiting.")
        return False
    
    # 2. YouTube 업로드
    print("\n📤 Uploading to YouTube...")
    
    try:
        import upload_youtube
        
        # 파일명에서 날짜 추출 (예: english_short_2025-10-09.mp4)
        filename = os.path.basename(video_path)
        parts = filename.replace(".mp4", "").split("_")
        
        language = "en" if "english" in filename else "ko"
        date_str = parts[-1] if len(parts) > 2 else datetime.now().strftime("%Y-%m-%d")
        
        video_url = upload_youtube.main(video_path, language, date_str)
        
        try:
            print(f"\n🎉 Upload successful!")
            print(f"🔗 {video_url}\n")
        except UnicodeEncodeError:
            print(f"\n[SUCCESS] Upload successful!")
            print(f"URL: {video_url}\n")
        
        return True
        
    except Exception as e:
        try:
            print(f"\n❌ Upload failed: {e}\n")
        except UnicodeEncodeError:
            print(f"\n[ERROR] Upload failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

