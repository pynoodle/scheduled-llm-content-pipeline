# 🤖 GitHub Actions 완전 자동화 가이드

**GitHub Actions에서 매일 자동으로 뉴스 수집 → 요약 → 쇼츠 생성 → YouTube 업로드**

## 🎯 자동화 아키텍처

### 방식 1: GitHub Actions + 로컬 업로드 (추천) ⭐

```
[매일 오전 8:00 - GitHub Actions]
  ↓
📰 뉴스 수집 (28개 소스)
  ↓
🧠 GPT-4 요약 생성
  ↓
📊 Notion 자동 저장
  ↓
🎬 YouTube Shorts 생성
  ↓
💾 Artifact 저장 (7일간 보관)
  ↓ (약 3-5분 소요)

[매일 오전 8:10 - 로컬 PC]
  ↓
📥 Artifact 자동 다운로드
  ↓
📤 YouTube 자동 업로드
```

**장점:**
- ✅ 서버 비용 없음 (GitHub Actions 무료)
- ✅ 로컬 PC가 꺼져도 쇼츠 생성됨
- ✅ OAuth 인증 문제 없음
- ✅ 안정적인 운영

### 방식 2: 완전 로컬 자동화

```
[매일 오전 8시 - Windows 작업 스케줄러]
  ↓
📰 뉴스 수집
  ↓
🧠 요약 생성
  ↓
📊 Notion 저장
  ↓
🎬 쇼츠 생성
  ↓
📤 YouTube 업로드
```

**장점:**
- ✅ 설정 간단
- ✅ 모든 과정이 로컬에서
- ✅ 완전 제어 가능

**단점:**
- ⚠️ PC가 켜져 있어야 함
- ⚠️ 네트워크 연결 필요

## 🚀 방식 1 설정: GitHub Actions + 로컬

### 1단계: GitHub Secrets 설정 (최초 1회)

1. GitHub 저장소 접속
   - https://github.com/pynoodle/AI_InsightLens

2. **Settings** > **Secrets and variables** > **Actions**

3. **New repository secret** 클릭하여 다음 추가:

| Secret 이름 | 값 | 필수 여부 |
|------------|-----|----------|
| `OPENAI_API_KEY` | `sk-proj-...` | ✅ 필수 |
| `NOTION_TOKEN` | `ntn_...` | ✅ 필수 |
| `NOTION_DB_ID` | `2879c57f...` | ✅ 필수 |
| `ALPHA_VANTAGE_KEY` | `your-key` | 선택 |
| `EMAIL_ENABLE` | `false` | 선택 |
| `EMAIL_SMTP_HOST` | `smtp.gmail.com` | 선택 |
| `EMAIL_SMTP_PORT` | `587` | 선택 |
| `EMAIL_USERNAME` | `your@email.com` | 선택 |
| `EMAIL_PASSWORD` | `app-password` | 선택 |
| `EMAIL_FROM` | `your@email.com` | 선택 |
| `EMAIL_TO` | `recipient@email.com` | 선택 |

### 2단계: GitHub Actions 테스트

1. GitHub 저장소 > **Actions** 탭

2. **Daily AI InsightLens (Full Pipeline)** 선택

3. **Run workflow** 클릭 > **Run workflow** 확인

4. 진행 상황 모니터링:
   ```
   ✅ Set up Python
   ✅ Install dependencies
   ✅ Run AI InsightLens
   ✅ Generate YouTube Shorts
   ✅ Upload Shorts as Artifact
   ```

5. 완료 후 **Artifacts** 섹션에서 `daily-shorts` 다운로드 가능

### 3단계: 로컬 자동 다운로드 + 업로드 설정

#### A. GitHub CLI 설치 (최초 1회)

**Windows:**
```bash
# Chocolatey 사용
choco install gh

# 또는 수동 다운로드
# https://cli.github.com/
```

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
sudo apt install gh
```

#### B. GitHub CLI 인증

```bash
gh auth login

# 선택:
# - GitHub.com
# - HTTPS
# - Login with a web browser
# - 브라우저에서 코드 입력
```

#### C. 자동 다운로드 + 업로드 스크립트

`auto_upload_daily.bat` 파일 생성:

```batch
@echo off
REM GitHub Actions에서 쇼츠 다운로드 후 YouTube 업로드

echo ============================================================
echo   AI InsightLens - Auto Download & Upload
echo ============================================================
echo.

cd /d C:\Users\yoonj\Documents\AI_InsightLens
call .venv\Scripts\activate.bat

echo [1/2] Downloading latest shorts from GitHub Actions...
python download_and_upload.py

echo.
echo [2/2] Done!
pause
```

#### D. Windows 작업 스케줄러 설정

1. **작업 스케줄러** 열기 (Win + R > `taskschd.msc`)

2. **작업 만들기**:
   - 이름: `AI InsightLens Auto Upload`
   - 트리거: **매일 오전 8:10** (GitHub Actions 후 10분 - 충분한 여유)
   - 동작: `C:\Users\yoonj\Documents\AI_InsightLens\auto_upload_daily.bat`
   - 조건: 전원 옵션 체크 해제

3. **저장**

### 4단계: 완전 자동화 확인

#### 매일 오전 8:00 (GitHub Actions):
- ✅ 뉴스 수집
- ✅ AI 요약
- ✅ Notion 저장
- ✅ 쇼츠 생성
- ✅ Artifact 업로드
- ⏱️ 소요 시간: 3-5분

#### 매일 오전 8:10 (로컬 PC):
- ✅ Artifact 다운로드
- ✅ YouTube 업로드
- ⏱️ 소요 시간: 1-2분

## 🚀 방식 2 설정: 완전 로컬 자동화

### Windows 작업 스케줄러 설정

1. **작업 스케줄러** 열기

2. **작업 만들기**:
   - 이름: `AI InsightLens Daily (Local)`
   - 트리거: **매일 오전 8:00**
   - 동작: `C:\Users\yoonj\Documents\AI_InsightLens\run_daily.bat`
   - 조건: 전원 옵션 체크 해제

3. **저장**

### 작업 내용

`run_daily.bat`가 다음을 실행:
```
1. 뉴스 수집 (28개 소스)
2. GPT-4 요약 생성
3. Notion 자동 저장
4. YouTube Shorts 생성
5. YouTube 자동 업로드
```

**소요 시간**: 약 3-5분

## 📊 비용 비교

### GitHub Actions (무료 플랜)

| 항목 | 월 제공량 | 사용량 |
|------|----------|--------|
| 실행 시간 | 2,000분 | ~60분 (2분/일 × 30일) |
| 스토리지 | 500MB | ~50MB (artifact) |
| **비용** | **$0** | **무료!** |

### OpenAI API

| 항목 | 일일 비용 | 월 비용 |
|------|----------|---------|
| GPT-4o-mini | $0.02 | $0.60 |
| TTS (5섹션) | $0.04 | $1.20 |
| **합계** | **$0.06** | **$2** |

**총 운영 비용: 월 $2 이하!**

## 🔍 모니터링

### GitHub Actions 로그 확인

1. GitHub 저장소 > **Actions** 탭
2. 최신 워크플로우 실행 클릭
3. 각 단계별 로그 확인

### Notion 확인

- https://www.notion.so/your-database
- 매일 오전 8:05 이후 새 페이지 생성 확인

### YouTube 확인

- https://studio.youtube.com
- 매일 오전 8:15 이후 새 쇼츠 업로드 확인

## 🛠️ 문제 해결

### "GitHub Actions failed"

```bash
# Actions 탭에서 에러 로그 확인
# 대부분 API 키 문제

# Secrets 재확인
Settings > Secrets and variables > Actions
```

### "Artifact download failed"

```bash
# GitHub CLI 재인증
gh auth logout
gh auth login

# 수동 다운로드
# Actions 탭 > 워크플로우 > Artifacts 섹션
```

### "YouTube upload failed"

```bash
# token.pickle 확인
dir token.pickle

# 재인증
del token.pickle
python upload_youtube.py shorts_output\english_short_2025-10-09.mp4 en
```

## 📈 성과 측정 (30일 후)

### 예상 결과

- 📹 **30개 YouTube Shorts** 자동 생성
- 📊 **30개 Notion 요약** 데이터베이스
- 👥 **채널 성장**: 구독자 증가 시작
- ⏰ **시간 절약**: 90시간 (3시간/일 × 30일)
- 💰 **총 비용**: $2

### KPI 추적

| 지표 | 목표 (30일) |
|------|------------|
| YouTube 조회수 | 1,000+ |
| 평균 시청 시간 | 20초+ |
| 구독자 증가 | 50+ |
| Notion 페이지 | 30개 |

## 🎯 최적화 팁

### 1. 실행 시간 조정

`.github/workflows/daily-insightlens.yml`:
```yaml
schedule:
  - cron: '0 23 * * *'  # UTC 23:00 (전날) = KST 08:00
  # 변경 예: '0 0 * * *' = KST 09:00
```

### 2. Artifact 보관 기간 조정

```yaml
retention-days: 7  # 기본 7일
# 변경 예: retention-days: 3  # 3일로 단축
```

### 3. 쇼츠 품질 향상

- 배경 음악 추가 (`shorts_output/background_music.mp3`)
- 디자인 커스터마이징 (`generate_shorts.py`)
- RSS 소스 최적화 (`run_insightlens_ai_only.py`)

## 🔄 업데이트 방법

### 코드 변경 후

```bash
# 로컬에서 수정
git add .
git commit -m "Update feature"
git push

# GitHub Actions가 자동으로 최신 코드 사용
```

### 환경 변수 변경

```bash
# GitHub Secrets 업데이트
Settings > Secrets and variables > Actions
# 해당 Secret 클릭 > Update
```

## 📚 다음 단계

1. ✅ GitHub Secrets 설정
2. ✅ GitHub Actions 테스트 실행
3. ✅ 로컬 자동 업로드 설정
4. ✅ 작업 스케줄러 등록
5. 📊 일주일 운영 후 성과 분석
6. 🎨 필요시 디자인/내용 개선

---

**완전 자동화 완성!** 이제 매일 아침 자동으로 AI 뉴스 쇼츠가 생성되고 YouTube에 업로드됩니다! 🎉

**문의**: GitHub Issues를 통해 문의해 주세요

