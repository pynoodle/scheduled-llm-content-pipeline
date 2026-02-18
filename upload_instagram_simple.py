#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 간편 업로드 스크립트 (Instagrapi 사용)
- 로컬 파일 직접 업로드 (클라우드 불필요)
- 캐러셀 포스트 자동 생성
- 캡션 자동 추가
"""

import os
import sys
from pathlib import Path
from PIL import Image

# ---- ENV LOADER ----
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

# Instagram 로그인 정보
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")

def upload_cardnews_to_instagram(cardnews_dir, date_str=None, caption_file=None):
    """
    카드뉴스를 Instagram 캐러셀로 업로드
    
    Args:
        cardnews_dir: 카드뉴스 이미지 디렉토리
        date_str: 날짜 (파일명 필터링용)
        caption_file: 캡션 파일 경로
    """
    try:
        from instagrapi import Client
    except ImportError:
        print("[ERROR] instagrapi가 설치되지 않았습니다.")
        print("        실행: pip install instagrapi")
        return False
    
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        print("[ERROR] Instagram 로그인 정보가 없습니다.")
        print("        .env 파일에 다음 정보를 추가하세요:")
        print("        INSTAGRAM_USERNAME=your_username")
        print("        INSTAGRAM_PASSWORD=your_password")
        return False
    
    print(f"\n{'='*60}")
    print(f"  Instagram Auto Upload")
    print(f"{'='*60}\n")
    
    # Instagram 클라이언트 생성
    cl = Client()
    
    # 로그인
    print(f"[1/4] Logging in to Instagram...")
    try:
        # 세션 파일이 있으면 재사용 (빠른 로그인)
        session_file = "instagram_session.json"
        if os.path.exists(session_file):
            print(f"      Using session file: {session_file}")
            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            # 세션 저장 (다음 로그인 빠르게)
            cl.dump_settings(session_file)
            print(f"      Session saved: {session_file}")
        
        print(f"      Login successful: @{INSTAGRAM_USERNAME}")
        
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        print("        If 2FA is enabled, use app password.")
        return False
    
    # 이미지 파일 찾기
    print(f"\n[2/4] Finding card news images...")
    cardnews_path = Path(cardnews_dir)
    
    if date_str:
        pattern = f"en_card_*_{date_str}.png"
    else:
        # 가장 최근 날짜 파일 찾기
        all_files = list(cardnews_path.glob("en_card_*.png"))
        if not all_files:
            print(f"[ERROR] No card news files found: {cardnews_dir}")
            return False
        
        # 날짜별로 그룹화
        dates = set()
        for f in all_files:
            parts = f.stem.split('_')
            if len(parts) >= 4:
                dates.add(parts[-1])
        
        if not dates:
            print(f"[ERROR] No dated files found")
            return False
        
        date_str = sorted(dates)[-1]  # 가장 최근 날짜
        pattern = f"en_card_*_{date_str}.png"
    
    image_files = sorted(cardnews_path.glob(pattern))
    
    if not image_files:
        print(f"[ERROR] No card news images found: {pattern}")
        return False
    
    print(f"      Found {len(image_files)} images:")
    for img in image_files:
        print(f"      - {img.name}")
    
    # 캡션 읽기
    print(f"\n[3/4] Loading caption...")
    caption = ""
    
    if caption_file and os.path.exists(caption_file):
        with open(caption_file, 'r', encoding='utf-8') as f:
            caption = f.read()
        print(f"      Using caption file: {caption_file}")
    else:
        # 자동으로 캡션 파일 찾기
        auto_caption = cardnews_path / f"en_caption_{date_str}.txt"
        if auto_caption.exists():
            with open(auto_caption, 'r', encoding='utf-8') as f:
                caption = f.read()
            print(f"      Auto-detected caption: {auto_caption.name}")
        else:
            caption = f"AI News Highlights - {date_str}\n\n#AI #Technology #Innovation"
            print(f"      Using default caption")
    
    print(f"\n      Caption preview:")
    print(f"      {'-'*50}")
    for line in caption.split('\n')[:5]:
        print(f"      {line}")
    if len(caption.split('\n')) > 5:
        print(f"      ...")
    print(f"      {'-'*50}")
    
    # Instagram 업로드
    print(f"\n[4/4] Uploading to Instagram...")
    print(f"      Creating carousel post ({len(image_files)} images)...")
    
    try:
        # PNG를 JPEG로 변환 (Instagram은 JPEG를 선호함)
        print(f"      Converting PNG to JPEG...")
        jpeg_paths = []
        temp_dir = Path("temp_instagram")
        temp_dir.mkdir(exist_ok=True)
        
        for img_file in image_files:
            # PNG 열기
            img = Image.open(img_file)
            
            # RGB 모드로 변환 (JPEG는 RGBA 지원 안 함)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # JPEG로 저장
            jpeg_path = temp_dir / f"{img_file.stem}.jpg"
            img.save(jpeg_path, 'JPEG', quality=95)
            jpeg_paths.append(str(jpeg_path.absolute()))
        
        print(f"      Converted {len(jpeg_paths)} images to JPEG")
        
        # 캐러셀 업로드
        media = cl.album_upload(
            paths=jpeg_paths,
            caption=caption
        )
        
        # 임시 파일 정리
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n{'='*60}")
        print(f"  Upload Successful!")
        print(f"{'='*60}")
        print(f"  Media ID: {media.pk}")
        print(f"  URL: https://www.instagram.com/p/{media.code}/")
        print(f"  Images: {len(image_files)}")
        print(f"  Date: {date_str}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n[TIP] Troubleshooting:")
        print("      1. Check if you can login via Instagram app")
        print("      2. Use app password if 2FA is enabled")
        print("      3. Don't upload too frequently (max 20/day recommended)")
        print("      4. Disable VPN if active")
        
        return False

def main():
    """
    메인 실행 함수
    """
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Instagram 간편 업로드 (Instagrapi)")
    parser.add_argument("--dir", default="cardnews_output",
                       help="카드뉴스 디렉토리 (기본: cardnews_output)")
    parser.add_argument("--date", help="날짜 필터 (YYYY-MM-DD)")
    parser.add_argument("--caption", help="캡션 파일 경로")
    parser.add_argument("--test", action="store_true",
                       help="테스트 모드 (업로드 안 함, 파일만 확인)")
    
    args = parser.parse_args()
    
    # 테스트 모드
    if args.test:
        print("\n[TEST MODE] Checking files only...")
        cardnews_path = Path(args.dir)
        
        if args.date:
            pattern = f"en_card_*_{args.date}.png"
        else:
            pattern = "en_card_*.png"
        
        files = sorted(cardnews_path.glob(pattern))
        print(f"\nFound {len(files)} files:")
        for f in files:
            print(f"  - {f.name}")
        
        if args.caption:
            caption_file = args.caption
        else:
            caption_file = cardnews_path / f"en_caption_{args.date or 'latest'}.txt"
        
        if os.path.exists(caption_file):
            print(f"\nCaption file: {caption_file}")
            try:
                with open(caption_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            except UnicodeEncodeError:
                print("[Preview skipped due to encoding]")
        
        return 0
    
    # 실제 업로드
    try:
        success = upload_cardnews_to_instagram(
            args.dir,
            args.date,
            args.caption
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nUpload cancelled")
        return 130
    
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

