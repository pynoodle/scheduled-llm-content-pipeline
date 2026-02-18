#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI InsightLens 완전 자동화 파이프라인
1. 뉴스/논문 수집 → 요약 생성
2. YouTube Shorts 생성
3. 카드뉴스 이미지 생성 (Instagram/Threads)
4. YouTube 자동 업로드
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

def iso_date_kst():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def run_pipeline():
    """
    전체 파이프라인 실행
    """
    date_kst = iso_date_kst()
    print(f"\n{'='*60}")
    print(f"  AI InsightLens Full Pipeline - {date_kst}")
    print(f"{'='*60}\n")
    
    # 1단계: 뉴스 수집 및 요약 생성
    print("📰 [STEP 1/4] Collecting news and generating summary...")
    print("-" * 60)
    
    try:
        import run_insightlens_ai_only
        run_insightlens_ai_only.run()
        print("✅ Summary generated successfully!")
    except Exception as e:
        print(f"❌ Failed to generate summary: {e}")
        return False
    
    summary_file = f"summary_{date_kst}.txt"
    if not os.path.exists(summary_file):
        print(f"❌ Summary file not found: {summary_file}")
        return False
    
    # 2단계: YouTube Shorts 생성
    print(f"\n🎬 [STEP 2/4] Generating YouTube Shorts...")
    print("-" * 60)
    
    try:
        import generate_shorts
        results = generate_shorts.main(summary_file)
        print("✅ Shorts generated successfully!")
        
        if not results:
            print("❌ No shorts were generated")
            return False
            
        video_path = results[0][1]  # 영어 쇼츠 경로
        
    except Exception as e:
        print(f"❌ Failed to generate shorts: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3단계: 카드뉴스 이미지 생성
    print(f"\n🎨 [STEP 3/4] Generating Card News (Instagram/Threads)...")
    print("-" * 60)
    
    try:
        import generate_cardnews
        
        # 영어 카드뉴스 생성 (주식정보 포함)
        en_slides = generate_cardnews.main(summary_file, output_dir="cardnews_output", 
                                          max_slides=5, language="en")
        print(f"[OK] English card news generated: {len(en_slides)} slides")
        print(f"    Includes: Intro + {len(en_slides)-3} news + Market + Outro")
        print(f"    Caption saved: cardnews_output/en_caption_{{date}}.txt")
        
        # 한글 카드뉴스 생성 (선택적)
        # ko_slides = generate_cardnews.main(summary_file, output_dir="cardnews_output", 
        #                                   max_slides=5, language="ko")
        # print(f"✅ Korean card news generated: {len(ko_slides)} slides")
        
    except Exception as e:
        print(f"⚠️  Failed to generate card news: {e}")
        import traceback
        traceback.print_exc()
        print("   Continuing with YouTube upload...")
    
    # 4단계: YouTube 업로드
    print(f"\n📤 [STEP 4/4] Uploading to YouTube...")
    print("-" * 60)
    
    try:
        import upload_youtube
        video_url = upload_youtube.main(video_path, language="en", date_str=date_kst)
        print(f"✅ Uploaded successfully!")
        print(f"🔗 Video URL: {video_url}")
        
    except FileNotFoundError:
        print("⚠️  YouTube credentials not found.")
        print("   Run this command first to authenticate:")
        print(f"   python upload_youtube.py {video_path} en {date_kst}")
        print("\n   After first authentication, future runs will be automatic!")
        return False
        
    except Exception as e:
        print(f"❌ Failed to upload: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 완료
    print(f"\n{'='*60}")
    print(f"  🎉 All steps completed successfully!")
    print(f"{'='*60}")
    print(f"\n📊 Summary: Notion")
    print(f"🎬 Video: {video_path}")
    print(f"🎨 Card News: cardnews_output/")
    print(f"🔗 YouTube: {video_url if 'video_url' in locals() else 'Not uploaded'}")
    print(f"\n💡 Next steps:")
    print(f"   - Upload card news to Instagram/Threads manually")
    print(f"   - Or use Instagram Graph API for automation")
    print(f"\n")
    
    return True

if __name__ == "__main__":
    try:
        success = run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

