# 📹 YouTube 자동 업로드 설정 가이드

YouTube Shorts를 자동으로 업로드하는 완전 자동화 시스템입니다.

## 🎯 자동화 개요

```
매일 실행 → 뉴스 수집 → 요약 생성 → 쇼츠 생성 → YouTube 자동 업로드
```

**한 번만 인증하면 이후 완전 자동!**

## 🔐 1단계: YouTube API 설정 (최초 1회)

### A. Google Cloud 프로젝트 생성

1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성: **"AI InsightLens"**
3. 프로젝트 선택

### B. YouTube Data API v3 활성화

1. **APIs & Services** > **Library** 클릭
2. "YouTube Data API v3" 검색
3. **Enable** 클릭

### C. OAuth 2.0 Credentials 생성

1. **APIs & Services** > **Credentials**
2. **Create Credentials** > **OAuth client ID**
3. **Configure Consent Screen** (처음이면)
   - User Type: **External**
   - App name: `AI InsightLens`
   - User support email: 본인 이메일
   - Developer contact: 본인 이메일
   - **Save and Continue** (나머지 기본값)
   
4. **Scopes** 설정
   - **Add or Remove Scopes** 클릭
   - `YouTube Data API v3` 검색
   - `.../auth/youtube.upload` 체크
   - **Update** > **Save and Continue**

5. **Test users** 추가
   - **Add Users** 클릭
   - YouTube 채널 소유자 이메일 추가
   - **Save and Continue**

6. 다시 **Credentials** 탭으로
   - **Create Credentials** > **OAuth client ID**
   - Application type: **Desktop app**
   - Name: "AI InsightLens Desktop"
   - **Create**

7. **Download JSON** 클릭
   - 파일 다운로드: `client_secret_xxxxx.json`

### D. Credentials 파일 저장

다운로드한 JSON 파일을:
```bash
# 프로젝트 루트에 저장하고 파일명 변경
C:\Users\yoonj\Documents\AI_InsightLens\client_secrets.json
```

**⚠️ 주의:** 이 파일은 `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다.

## 🔑 2단계: 첫 인증 (최초 1회)

### 테스트 업로드

```bash
# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 쇼츠가 있는지 확인
dir shorts_output\*.mp4

# 첫 업로드 (인증 필요)
python upload_youtube.py shorts_output\english_short_2025-10-09.mp4 en 2025-10-09
```

### 인증 프로세스

1. **브라우저가 자동으로 열립니다**
2. Google 계정 로그인
3. **"AI InsightLens" 앱 권한 허용**
   - "This app isn't verified" 경고가 나올 수 있음
   - **Advanced** > **Go to AI InsightLens (unsafe)** 클릭
   - **Allow** 클릭
4. "The authentication flow has completed" 메시지 확인
5. **`token.pickle` 파일이 자동 생성됨**

### ✅ 인증 완료 확인

```bash
# token.pickle 파일이 생성되었는지 확인
dir token.pickle
```

**이 파일이 있으면 이후 자동 업로드 가능!**

## 🤖 3단계: 완전 자동 실행

### 방법 1: 수동 실행 (테스트)

```bash
# 전체 파이프라인 실행 (뉴스 수집 → 쇼츠 생성 → 업로드)
python run_full_pipeline.py
```

**실행 순서:**
1. RSS/arXiv 뉴스 수집
2. GPT-4로 요약 생성
3. Notion에 저장
4. 쇼츠 영상 생성
5. YouTube 자동 업로드

**소요 시간:** 약 3-5분

### 방법 2: Windows 작업 스케줄러 (완전 자동)

#### A. 배치 파일 생성

`run_daily.bat` 파일 생성:

```batch
@echo off
cd C:\Users\yoonj\Documents\AI_InsightLens
call .venv\Scripts\activate.bat

echo Starting AI InsightLens Pipeline...
python run_full_pipeline.py

if %ERRORLEVEL% EQU 0 (
    echo ✅ Pipeline completed successfully!
) else (
    echo ❌ Pipeline failed with error code %ERRORLEVEL%
)

pause
```

#### B. 작업 스케줄러 설정

1. **작업 스케줄러** 열기 (Windows + R > `taskschd.msc`)
2. **작업 만들기** 클릭

**일반 탭:**
- 이름: `AI InsightLens Daily`
- 설명: `Daily AI news shorts generation and upload`
- **가장 높은 수준의 권한으로 실행** 체크

**트리거 탭:**
- **새로 만들기** 클릭
- 작업 시작: **일정**
- 설정: **매일**
- 시작 시간: **오전 8:00** (완전 로컬 실행용)
- **사용** 체크
- **확인**

**참고:** GitHub Actions와 함께 사용하는 경우, 로컬 업로드 작업은 **오전 8:10**에 설정하세요.

**동작 탭:**
- **새로 만들기** 클릭
- 작업: **프로그램 시작**
- 프로그램/스크립트: `C:\Users\yoonj\Documents\AI_InsightLens\run_daily.bat`
- 시작 위치: `C:\Users\yoonj\Documents\AI_InsightLens`
- **확인**

**조건 탭:**
- **컴퓨터의 전원이 AC일 때만** 체크 해제
- **확인**

**설정 탭:**
- **작업이 실패할 경우 다시 시작** 간격: 1분, 횟수: 3
- **확인**

#### C. 테스트

작업 스케줄러에서:
- 생성한 작업 우클릭
- **실행** 클릭
- 로그 확인

## 🔄 일일 워크플로우

### 자동 실행 흐름 (매일 오전 8시)

```
8:00 AM - 작업 스케줄러 시작
    ↓
8:01 AM - 뉴스 수집 (28개 소스)
    ↓
8:02 AM - GPT-4 요약 생성
    ↓
8:03 AM - Notion 저장
    ↓
8:04 AM - 쇼츠 영상 생성 (TTS + 편집)
    ↓
8:05 AM - YouTube 자동 업로드
    ↓
8:06 AM - 완료! ✅
```

**모든 과정이 자동으로 실행됩니다!**

## 📊 YouTube 채널 전략

### 영어 채널: "AI News Today"

**채널 설정:**
- 채널명: AI News Today
- 설명: Daily AI news, research, and market analysis
- 카테고리: Science & Technology

**업로드 설정:**
- 공개 상태: **Public** (즉시 공개)
- 카테고리: Science & Technology
- 태그: #AI #ArtificialIntelligence #Tech #Shorts
- 썸네일: 자동 (첫 프레임)

### 한글 채널 (선택): "오늘의 AI 뉴스"

한글 쇼츠를 활성화하려면:

`generate_shorts.py`에서 주석 해제:
```python
# 라인 368-377 주석 제거
if korean_summary:
    print("\n=== Generating Korean Short ===")
    ko_points = extract_shorts_content(korean_summary, "ko")
    ...
```

## ⚙️ 고급 설정

### A. 업로드 실패 시 재시도

`run_full_pipeline.py`에 이미 포함됨

### B. 이메일 알림 (선택)

`.env` 파일에서:
```env
EMAIL_ENABLE=true
EMAIL_TO=your_email@gmail.com
```

업로드 성공/실패 시 이메일 알림 받기

### C. 배경 음악 자동 적용

```bash
# 무료 음원 다운로드 (Pixabay 등)
# 다음 경로에 저장
shorts_output/background_music.mp3

# 자동으로 15% 볼륨 적용
```

## 🔍 문제 해결

### "token.pickle not found"

```bash
# 첫 인증 필요
python upload_youtube.py shorts_output\english_short_2025-10-09.mp4 en
```

### "client_secrets.json not found"

1. Google Cloud Console에서 OAuth credentials 다운로드
2. `client_secrets.json`으로 저장
3. 프로젝트 루트에 배치

### "Quota exceeded"

YouTube API 일일 할당량:
- **일일 업로드 제한**: 6개 영상
- **API 할당량**: 10,000 units/day
- **업로드 비용**: 1,600 units

**솔루션:**
- 하루 1-2개 쇼츠만 업로드 (충분함)
- 할당량 증가 요청 (Google)

### token 만료

```bash
# token.pickle 삭제 후 재인증
del token.pickle
python upload_youtube.py shorts_output\english_short_2025-10-09.mp4 en
```

## 📈 성과 측정

### YouTube Analytics 확인

- YouTube Studio > Analytics
- **Shorts** 탭 선택
- 주요 지표:
  - 조회수
  - 평균 시청 시간
  - 구독자 증가
  - 클릭률 (CTR)

### 최적화 팁

1. **제목 A/B 테스트**
   - `upload_youtube.py`에서 제목 형식 변경
   
2. **업로드 시간 최적화**
   - 작업 스케줄러에서 시간 변경
   - 추천: 오전 9-11시 또는 오후 6-8시

3. **해시태그 최적화**
   - 인기 키워드 추가
   - YouTube 검색 트렌드 반영

## 🚀 운영 체크리스트

### 매일
- ✅ Notion 페이지 확인
- ✅ YouTube 업로드 확인
- ✅ 조회수 모니터링

### 매주
- ✅ 상위 성과 쇼츠 분석
- ✅ 트렌드 키워드 업데이트
- ✅ 채널 성장률 체크

### 매월
- ✅ API 비용 확인 (~$2-3)
- ✅ YouTube 할당량 사용량 확인
- ✅ 구독자 증가 분석

## 💡 다음 단계

1. ✅ 첫 인증 완료 (`token.pickle` 생성)
2. ✅ `run_full_pipeline.py` 테스트
3. ✅ Windows 작업 스케줄러 설정
4. 📊 일주일 운영 후 성과 분석
5. 🎨 필요시 디자인/내용 개선

---

**완전 자동화 완료!** 이제 매일 아침 자동으로 AI 뉴스 쇼츠가 YouTube에 업로드됩니다! 🎉

