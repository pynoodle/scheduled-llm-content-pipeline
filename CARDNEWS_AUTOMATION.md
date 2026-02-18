# 📸 카드뉴스 자동화 가이드 (Instagram/Threads)

AI InsightLens에서 생성된 요약문을 카드뉴스 이미지로 자동 변환하고 Instagram/Threads에 업로드하는 방법입니다.

## 📋 목차
1. [개요](#개요)
2. [카드뉴스 생성](#카드뉴스-생성)
3. [Instagram 업로드 설정](#instagram-업로드-설정)
4. [자동화 파이프라인](#자동화-파이프라인)
5. [문제해결](#문제해결)

---

## 🎯 개요

### 기능
- ✅ **자동 카드뉴스 생성**: 요약문에서 핵심 내용 3-5개 추출
- ✅ **Instagram/Threads 최적화**: 1080x1080 정사각형 이미지
- ✅ **화려한 디자인**: 그라디언트 배경, 폰트 효과, 자동 색상 변화
- ✅ **해시태그 자동 추출**: 요약문에서 해시태그 자동 포함
- ✅ **다국어 지원**: 영어/한글 카드뉴스 생성

### 생성 예시
```
📸 Slide 1: 인트로 (AI NEWS TODAY + 날짜)
📸 Slide 2-4: 핵심 뉴스 (제목 + 내용 + 출처)
📸 Slide 5: 아웃트로 (팔로우 유도 + 해시태그)
```

---

## 🎨 카드뉴스 생성

### 1. 수동 생성 (개별 실행)

```bash
# 영어 카드뉴스 생성
python generate_cardnews.py summary_2025-10-09.txt --lang en --slides 5

# 한글 카드뉴스 생성
python generate_cardnews.py summary_2025-10-09.txt --lang ko --slides 5

# 출력 디렉토리 지정
python generate_cardnews.py summary_2025-10-09.txt --output my_cardnews --lang en
```

### 2. 자동 생성 (파이프라인 포함)

```bash
# 전체 파이프라인 실행 (뉴스 수집 → 요약 → 쇼츠 → 카드뉴스 → YouTube 업로드)
python run_full_pipeline.py
```

파이프라인에서 카드뉴스는 **STEP 3/4**에서 자동 생성됩니다.

### 3. 생성된 파일 확인

```
cardnews_output/
├── en_card_00_intro_2025-10-09.png       # 인트로
├── en_card_01_2025-10-09.png             # 뉴스 1
├── en_card_02_2025-10-09.png             # 뉴스 2
├── en_card_03_2025-10-09.png             # 뉴스 3
└── en_card_04_outro_2025-10-09.png       # 아웃트로
```

---

## 📱 Instagram 업로드 설정

### 방법 1: 수동 업로드 (추천 - 간단함)

1. `cardnews_output/` 폴더의 이미지를 확인
2. Instagram 또는 Threads 앱에서 **캐러셀 포스트** 생성
3. 이미지를 순서대로 업로드
4. 캡션과 해시태그 추가

**장점**: 설정 불필요, 즉시 사용 가능  
**단점**: 매번 수동 작업 필요

---

### 방법 2: 자동 업로드 (Instagram Graph API)

Instagram Graph API를 사용하여 자동 업로드가 가능하지만, 다음 조건이 필요합니다:

#### ✅ 사전 요구사항

1. **Instagram 비즈니스 계정** 또는 **Creator 계정**
2. **Facebook 페이지** (Instagram 계정과 연결)
3. **Facebook 개발자 계정** (https://developers.facebook.com)
4. **공개 이미지 URL** (S3, Cloudinary 등 클라우드 스토리지)

#### 🔧 설정 단계

##### 1. Facebook 앱 생성

1. https://developers.facebook.com 접속
2. **My Apps** → **Create App** 클릭
3. **App Type**: "Business" 선택
4. 앱 정보 입력 후 생성

##### 2. Instagram Graph API 활성화

1. 앱 대시보드에서 **Add Product** → **Instagram** 선택
2. **Instagram Graph API** 활성화

##### 3. Access Token 발급

1. **Graph API Explorer** 열기
2. User Token 생성:
   - Permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
3. **Access Token을 장기 토큰으로 변환**:

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}"
```

##### 4. Instagram Business Account ID 확인

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token={your-access-token}"
```

응답에서 `instagram_business_account` ID 확인

##### 5. .env 파일에 추가

```bash
# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

##### 6. 이미지 클라우드 업로드 설정

Instagram API는 **공개 URL**만 지원하므로 클라우드 스토리지 필요:

**옵션 A: AWS S3 + CloudFront**
```python
import boto3

def upload_to_s3(image_path):
    s3 = boto3.client('s3')
    bucket = 'your-bucket-name'
    key = f'cardnews/{os.path.basename(image_path)}'
    
    s3.upload_file(image_path, bucket, key, 
                   ExtraArgs={'ACL': 'public-read'})
    
    return f"https://{bucket}.s3.amazonaws.com/{key}"
```

**옵션 B: Cloudinary**
```python
import cloudinary.uploader

def upload_to_cloudinary(image_path):
    result = cloudinary.uploader.upload(image_path)
    return result['secure_url']
```

**옵션 C: ImgBB (무료)**
```python
import requests

def upload_to_imgbb(image_path):
    url = "https://api.imgbb.com/1/upload"
    
    with open(image_path, 'rb') as f:
        payload = {
            'key': 'your_imgbb_api_key',
            'image': f.read()
        }
    
    response = requests.post(url, payload)
    return response.json()['data']['url']
```

##### 7. upload_instagram.py 수정

`upload_instagram.py` 파일에서 `upload_to_cloud()` 함수를 실제 클라우드 서비스로 교체:

```python
def upload_cardnews_to_instagram(cardnews_dir, caption, hashtags="", date_str=None):
    # ... 이미지 파일 찾기 ...
    
    # 이미지를 클라우드에 업로드하여 공개 URL 획득
    image_urls = []
    for img in image_files:
        url = upload_to_s3(img)  # 또는 upload_to_cloudinary(img)
        image_urls.append(url)
    
    # Instagram에 캐러셀 포스트 업로드
    return create_carousel_post(image_urls, caption, hashtags)
```

##### 8. 자동 업로드 실행

```bash
python upload_instagram.py cardnews_output --date 2025-10-09 --caption "AI News Today 📰" --hashtags "#AI #Technology"
```

---

## 🔄 자동화 파이프라인

### 전체 워크플로우

```
1️⃣ AI 뉴스 수집 (RSS/API)
    ↓
2️⃣ 요약 + 해시태그 생성 (LLM)
    ↓
3️⃣ 텍스트 → TTS → 영상 (YouTube Shorts)
    ↓
4️⃣ 텍스트 → PIL → 카드뉴스 이미지 (Instagram, Threads)
    ↓
5️⃣ YouTube 자동 업로드
    ↓
6️⃣ Instagram 수동/자동 업로드
```

### run_full_pipeline.py 커스터마이징

파이프라인에서 카드뉴스만 생성하고 싶다면:

```python
# run_full_pipeline.py의 67-88줄 참고

# 한글 카드뉴스도 생성하려면 주석 제거
ko_slides = generate_cardnews.main(summary_file, output_dir="cardnews_output", 
                                   max_slides=5, language="ko")
```

### Windows 작업 스케줄러 자동화

```batch
# auto_upload_daily.bat 수정

@echo off
REM 전체 파이프라인 실행 (카드뉴스 포함)
cd /d C:\Users\YourName\Documents\AI_InsightLens
python run_full_pipeline.py

REM Instagram 업로드 (설정 완료 시)
REM python upload_instagram.py cardnews_output --date %date:~0,10%

pause
```

---

## 🎨 디자인 커스터마이징

### 색상 변경

`generate_cardnews.py`에서 그라디언트 색상 수정:

```python
# 슬라이드별 색상 (RGB)
colors = [
    ((15, 30, 60), (60, 30, 90)),   # 파란색-보라색
    ((30, 15, 60), (90, 30, 60)),   # 보라색-분홍색
    ((15, 60, 30), (60, 90, 30)),   # 초록색-노란색
    ((60, 30, 15), (90, 60, 30)),   # 주황색-노란색
]
```

### 폰트 변경

```python
# Windows 폰트 경로
try:
    title_font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 65)  # Impact
    content_font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 45)  # Georgia
except:
    # 기본 폰트 사용
    pass
```

### 슬라이드 개수 조정

```bash
# 3개 슬라이드 (인트로 + 1개 뉴스 + 아웃트로)
python generate_cardnews.py summary.txt --slides 3

# 7개 슬라이드 (인트로 + 5개 뉴스 + 아웃트로)
python generate_cardnews.py summary.txt --slides 7
```

---

## ❓ 문제해결

### Q1: 이미지가 생성되지 않아요

**원인**: OpenAI API 키 누락 또는 요약 파일 오류

**해결**:
```bash
# .env 파일 확인
OPENAI_API_KEY=sk-...

# 요약 파일 확인
dir summary_*.txt
```

### Q2: 폰트가 이상해요

**원인**: 시스템 폰트 경로 문제

**해결**:
```python
# generate_cardnews.py에서 폰트 경로 확인
# Windows: C:/Windows/Fonts/
# Mac: /System/Library/Fonts/
# Linux: /usr/share/fonts/
```

### Q3: Instagram 업로드가 안 돼요

**원인 1**: Access Token 만료  
**해결**: 장기 토큰으로 재발급 (위 설정 참조)

**원인 2**: 권한 부족  
**해결**: `instagram_content_publish` 권한 확인

**원인 3**: 이미지 URL이 공개되지 않음  
**해결**: S3 버킷 정책에서 `public-read` 권한 설정

### Q4: 캐러셀이 10개 이상이에요

**원인**: Instagram은 캐러셀당 최대 10개 이미지만 지원

**해결**:
```bash
# 슬라이드 개수 제한
python generate_cardnews.py summary.txt --slides 8  # 최대 10개 (인트로+아웃트로 포함)
```

### Q5: Threads에는 어떻게 올리나요?

**답변**: 
- Threads는 현재 별도 API 없음 (2025년 기준)
- Instagram 캐러셀 포스트를 Threads에서도 재사용 가능
- 또는 Threads 앱에서 수동 업로드

---

## 🔗 참고 자료

- [Instagram Graph API 공식 문서](https://developers.facebook.com/docs/instagram-api)
- [Instagram Publishing API](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
- [Cloudinary 무료 플랜](https://cloudinary.com/pricing)
- [AWS S3 가격](https://aws.amazon.com/s3/pricing/)
- [ImgBB API 문서](https://api.imgbb.com/)

---

## 📌 추가 기능 아이디어

1. **동영상 카드뉴스**: 슬라이드를 연결하여 짧은 동영상 생성
2. **A/B 테스팅**: 여러 디자인 변형 생성
3. **Analytics 연동**: Instagram Insights API로 성과 분석
4. **스케줄링**: Instagram Business Suite로 예약 포스팅
5. **자동 태깅**: 이미지 내용 분석하여 관련 계정 자동 태그

---

**🎉 카드뉴스 자동화 완료!**

문제가 있거나 개선 아이디어가 있다면 이슈를 등록해 주세요.

