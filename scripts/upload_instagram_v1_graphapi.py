#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram/Threads 카드뉴스 자동 업로드 스크립트
Instagram Graph API를 사용한 캐러셀(다중 이미지) 포스트 업로드
"""

import os
import sys
import time
import requests
from pathlib import Path

# ---- ENV LOADER ----
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

# Instagram Graph API 설정
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

# API Base URL
GRAPH_API_VERSION = "v21.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

def upload_image_to_instagram(image_path, caption="", is_carousel_item=False):
    """
    이미지를 Instagram에 업로드
    
    Args:
        image_path: 이미지 파일 경로
        caption: 게시물 설명
        is_carousel_item: 캐러셀 항목 여부
    
    Returns:
        container_id: 컨테이너 ID (캐러셀용) 또는 media_id (단일 이미지)
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        raise ValueError("Instagram credentials not found in .env file")
    
    # 이미지 URL (공개 URL이어야 함)
    # 로컬 파일의 경우 먼저 웹 서버에 업로드하거나 임시 공개 URL 생성 필요
    # 여기서는 placeholder - 실제로는 S3, Cloudinary 등 사용
    print(f"[INFO] Image to upload: {image_path}")
    print("[WARN] Local files need to be uploaded to a public URL first")
    print("       Please use S3, Cloudinary, or similar service")
    
    # 예시: Cloudinary, S3 등에 업로드하여 공개 URL 획득
    # image_url = upload_to_cloud(image_path)
    
    # Instagram Graph API는 공개 URL만 지원
    # 이 스크립트는 교육 목적이므로 실제 구현은 사용자가 해야 함
    
    raise NotImplementedError(
        "Instagram Graph API requires public image URLs. "
        "Please upload images to a cloud storage service (S3, Cloudinary, etc.) first."
    )

def create_carousel_post(image_urls, caption, hashtags=""):
    """
    여러 이미지로 캐러셀 포스트 생성
    
    Args:
        image_urls: 공개 이미지 URL 리스트 (최대 10개)
        caption: 게시물 설명
        hashtags: 해시태그
    
    Returns:
        post_id: 게시물 ID
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        raise ValueError("Instagram credentials not found in .env file")
    
    print(f"\n=== Creating Instagram Carousel Post ===")
    print(f"Images: {len(image_urls)}")
    print(f"Caption: {caption[:50]}...")
    
    # 1. 각 이미지의 컨테이너 생성
    container_ids = []
    
    for i, image_url in enumerate(image_urls, 1):
        print(f"[{i}/{len(image_urls)}] Creating container for image...")
        
        # 컨테이너 생성 API
        url = f"{GRAPH_API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
        params = {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to create container: {response.text}")
            raise Exception(f"Failed to create container for image {i}")
        
        container_id = response.json().get("id")
        container_ids.append(container_id)
        print(f"  Container created: {container_id}")
        
        # API rate limit 방지
        time.sleep(1)
    
    # 2. 캐러셀 컨테이너 생성
    print("\n[CAROUSEL] Creating carousel container...")
    
    full_caption = f"{caption}\n\n{hashtags}" if hashtags else caption
    
    carousel_url = f"{GRAPH_API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    carousel_params = {
        "media_type": "CAROUSEL",
        "children": ",".join(container_ids),
        "caption": full_caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    carousel_response = requests.post(carousel_url, params=carousel_params)
    
    if carousel_response.status_code != 200:
        print(f"[ERROR] Failed to create carousel: {carousel_response.text}")
        raise Exception("Failed to create carousel container")
    
    carousel_container_id = carousel_response.json().get("id")
    print(f"  Carousel container created: {carousel_container_id}")
    
    # 3. 게시물 발행
    print("\n[PUBLISH] Publishing carousel post...")
    
    publish_url = f"{GRAPH_API_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    publish_params = {
        "creation_id": carousel_container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    publish_response = requests.post(publish_url, params=publish_params)
    
    if publish_response.status_code != 200:
        print(f"[ERROR] Failed to publish: {publish_response.text}")
        raise Exception("Failed to publish carousel post")
    
    post_id = publish_response.json().get("id")
    print(f"✅ Post published successfully!")
    print(f"   Post ID: {post_id}")
    
    return post_id

def upload_cardnews_to_instagram(cardnews_dir, caption, hashtags="", date_str=None):
    """
    카드뉴스 디렉토리의 모든 이미지를 Instagram 캐러셀로 업로드
    
    Args:
        cardnews_dir: 카드뉴스 이미지 디렉토리
        caption: 게시물 설명
        hashtags: 해시태그
        date_str: 날짜 (파일명 필터링용)
    
    Returns:
        post_id: 게시물 ID
    """
    # 이미지 파일 찾기
    cardnews_path = Path(cardnews_dir)
    
    if date_str:
        # 특정 날짜의 파일만
        pattern = f"en_card_*_{date_str}.png"
    else:
        # 모든 카드뉴스 파일
        pattern = "en_card_*.png"
    
    image_files = sorted(cardnews_path.glob(pattern))
    
    if not image_files:
        raise FileNotFoundError(f"No card news images found in {cardnews_dir}")
    
    print(f"\n=== Found {len(image_files)} images ===")
    for img in image_files:
        print(f"  - {img.name}")
    
    # 실제 구현에서는 이미지를 클라우드에 업로드하여 공개 URL 획득
    print("\n⚠️  Instagram Graph API requires public image URLs")
    print("   Steps to complete upload:")
    print("   1. Upload images to cloud storage (S3, Cloudinary, etc.)")
    print("   2. Get public URLs for each image")
    print("   3. Use create_carousel_post() with those URLs")
    print("\n   Example services:")
    print("   - AWS S3 + CloudFront")
    print("   - Cloudinary")
    print("   - ImgBB")
    print("   - Firebase Storage")
    
    # 예시 코드 (실제 URL로 교체 필요)
    # image_urls = [upload_to_s3(img) for img in image_files]
    # return create_carousel_post(image_urls, caption, hashtags)
    
    return None

def main():
    """
    메인 실행 함수
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload card news to Instagram")
    parser.add_argument("cardnews_dir", nargs="?", default="cardnews_output",
                       help="Card news directory (default: cardnews_output)")
    parser.add_argument("--caption", default="AI News Today 📰",
                       help="Post caption")
    parser.add_argument("--hashtags", default="#AI #Technology #Innovation #News",
                       help="Hashtags")
    parser.add_argument("--date", help="Date filter (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    try:
        post_id = upload_cardnews_to_instagram(
            args.cardnews_dir,
            args.caption,
            args.hashtags,
            args.date
        )
        
        if post_id:
            print(f"\n✅ Upload complete!")
            print(f"   Post ID: {post_id}")
        else:
            print(f"\n⚠️  Manual upload required")
            print(f"   Please upload images from: {args.cardnews_dir}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

