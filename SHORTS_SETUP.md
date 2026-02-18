# 📹 YouTube Shorts 자동화 설정 가이드

## 🎬 개요

매일 생성되는 AI 뉴스 요약을 자동으로 YouTube Shorts로 만들어 업로드합니다.
- **영어 채널**: AI News Today
- **한글 채널**: 오늘의 AI 뉴스

## 🛠 로컬 테스트 (먼저 해보세요!)

### 1️⃣ 패키지 설치

```bash
pip install -r requirements.txt
```

**주의**: moviepy 설치 시 ffmpeg가 필요합니다.
- Windows: `choco install ffmpeg` 또는 https://ffmpeg.org/download.html
- Mac: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### 2️⃣ 쇼츠 생성 테스트

```bash
# 먼저 요약문 생성
python run_insightlens_ai_only.py

# 쇼츠 생성 (summary_2025-10-09.txt 파일 사용)
python generate_shorts.py summary_2025-10-09.txt
```

**생성 결과**:
- `shorts_output/english_short.mp4` - 영어 쇼츠
- `shorts_output/korean_short.mp4` - 한글 쇼츠
- `shorts_output/english_audio.mp3` - 영어 TTS
- `shorts_output/korean_audio.mp3` - 한글 TTS

### 3️⃣ YouTube 업로드 설정

#### A. YouTube API 프로젝트 생성

1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성: "AI InsightLens Shorts"
3. **APIs & Services** > **Enable APIs** 클릭
4. "YouTube Data API v3" 검색 후 **Enable**

#### B. OAuth 2.0 Credentials 생성

1. **APIs & Services** > **Credentials**
2. **Create Credentials** > **OAuth client ID**
3. Application type: **Desktop app**
4. Name: "AI InsightLens Desktop"
5. **Download JSON** (파일명: `client_secrets.json`)
6. 다운로드한 파일을 프로젝트 루트에 저장

#### C. 첫 업로드 (인증)

```bash
# 영어 쇼츠 업로드
python upload_youtube.py shorts_output/english_short.mp4 en

# 한글 쇼츠 업로드  
python upload_youtube.py shorts_output/korean_short.mp4 ko
```

**첫 실행 시**:
- 브라우저가 자동으로 열림
- Google 계정으로 로그인
- "AI InsightLens Shorts" 앱 권한 허용
- `token.pickle` 파일 자동 생성 (재사용됨)

## 🤖 GitHub Actions 자동화 (선택)

### ⚠️ 제한사항

YouTube API는 OAuth 2.0 인증이 필요해서 **GitHub Actions에서 완전 자동화가 어렵습니다**.

### 💡 권장 방법

**옵션 1: 반자동 (권장)**
1. GitHub Actions가 매일 쇼츠 생성
2. GitHub Artifacts에 영상 저장
3. 사용자가 다운로드 후 수동 업로드

**옵션 2: 로컬 자동화**
1. 로컬 PC에서 cron/Task Scheduler 설정
2. 매일 정해진 시간에 스크립트 실행
3. 완전 자동 업로드

**옵션 3: 서비스 계정 (고급)**
1. YouTube Brand Account 생성
2. 서비스 계정 설정
3. GitHub Secrets에 credentials 저장

## 📅 로컬 자동화 설정

### Windows (Task Scheduler)

1. **작업 스케줄러** 열기
2. **기본 작업 만들기**
3. 이름: "AI Shorts Daily"
4. 트리거: 매일 오전 10시
5. 작업: 프로그램 시작
6. 프로그램: `python`
7. 인수: `C:\path\to\run_shorts_pipeline.bat`

**run_shorts_pipeline.bat** 생성:
```batch
@echo off
cd C:\Users\yoonj\Documents\AI_InsightLens
call .venv\Scripts\activate.bat

REM 1. 요약 생성
python run_insightlens_ai_only.py

REM 2. 쇼츠 생성
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
python generate_shorts.py summary_%mydate%.txt

REM 3. YouTube 업로드
python upload_youtube.py shorts_output/english_short.mp4 en %mydate%
python upload_youtube.py shorts_output/korean_short.mp4 ko %mydate%

echo Shorts uploaded successfully!
pause
```

### Mac/Linux (cron)

```bash
# crontab 편집
crontab -e

# 매일 오전 10시 실행
0 10 * * * /path/to/run_shorts_pipeline.sh
```

**run_shorts_pipeline.sh** 생성:
```bash
#!/bin/bash
cd /Users/yoonj/Documents/AI_InsightLens
source .venv/bin/activate

# 1. 요약 생성
python run_insightlens_ai_only.py

# 2. 쇼츠 생성
TODAY=$(date +%Y-%m-%d)
python generate_shorts.py summary_${TODAY}.txt

# 3. YouTube 업로드
python upload_youtube.py shorts_output/english_short.mp4 en $TODAY
python upload_youtube.py shorts_output/korean_short.mp4 ko $TODAY

echo "Shorts uploaded successfully!"
```

```bash
chmod +x run_shorts_pipeline.sh
```

## 🎨 커스터마이징

### 배경 색상 변경

`generate_shorts.py`에서:
```python
# 라인 126
bg_color = (15, 23, 42)  # RGB 값 변경
```

### 폰트 크기 조정

```python
# 라인 130 (제목)
fontsize=100

# 라인 149 (본문)
fontsize=70
```

### TTS 목소리 변경

```python
# 라인 54
voice = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
```

### 쇼츠 길이 조정

```python
# 라인 136
point_duration = 10  # 각 포인트당 초 단위
```

## 💰 예상 비용

**일일 비용** (영어 + 한글 2개 쇼츠):
- OpenAI TTS: ~$0.02
- GPT-4 Mini (포인트 추출): ~$0.01
- YouTube API: 무료
- **합계: ~$0.03/일** (월 $1 이하)

## ❓ 문제 해결

### moviepy 오류

```bash
# imagemagick 설치 필요
# Windows
choco install imagemagick

# Mac
brew install imagemagick

# Linux
sudo apt-get install imagemagick
```

### ffmpeg 오류

```bash
# Windows
choco install ffmpeg

# Mac
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### YouTube 업로드 실패

1. `client_secrets.json` 파일 확인
2. YouTube Data API v3 활성화 확인
3. `token.pickle` 삭제 후 재인증
4. YouTube 계정의 업로드 한도 확인 (일일 6개)

## 📊 성과 확인

- YouTube Studio에서 쇼츠 조회수 확인
- #Shorts 태그가 자동으로 적용되는지 확인
- 첫 24시간 내 성과가 중요함

## 🚀 다음 단계

1. ✅ 로컬에서 쇼츠 생성 테스트
2. ✅ YouTube 업로드 테스트
3. ✅ 로컬 자동화 설정
4. 📊 성과 분석 후 개선

---

**문의사항이 있으면 알려주세요!**

