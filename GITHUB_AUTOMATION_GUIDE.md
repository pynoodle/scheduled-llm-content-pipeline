# 🤖 GitHub Actions 완전 자동화 가이드

**매일 자동으로 AI 뉴스 수집 → 요약 → 쇼츠 → 카드뉴스 → Instagram 업로드까지!**

---

## 🎯 자동화 범위

### ✅ 완전 자동화 (GitHub Actions)
1. **AI 뉴스 수집** - RSS/API에서 자동 수집
2. **요약 생성** - GPT-4o-mini로 요약
3. **YouTube Shorts 생성** - TTS + 영상 자동 생성
4. **Instagram 카드뉴스 생성** - 6장 이미지 자동 생성
5. **Instagram 자동 업로드** - 즉시 게시 ✨
6. **Notion 저장** - 요약문 자동 저장

### ⚠️ 수동 작업 필요
7. **YouTube 업로드** - OAuth 인증 문제로 로컬에서 업로드
   - GitHub Actions에서 생성된 영상을 다운로드
   - 로컬에서 `python upload_youtube.py` 실행

---

## 🚀 설정 방법 (15분)

### 1단계: GitHub Repository 설정

#### 1-1. Secrets 등록

GitHub Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

다음 secrets를 추가:

```
OPENAI_API_KEY=sk-proj-your-key-here
NOTION_TOKEN=ntn_your-token-here
NOTION_DB_ID=your-database-id-here
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
ALPHA_VANTAGE_KEY=your-key-here
```

**⚠️ 중요**: 
- Instagram 비밀번호는 **앱 비밀번호** 사용 (2FA 사용 시)
- Secrets는 암호화되어 안전하게 저장됨

---

### 2단계: GitHub Actions 활성화

#### 2-1. 워크플로우 파일 확인

`.github/workflows/daily-ai-content.yml` 파일이 생성되었는지 확인

#### 2-2. Actions 권한 설정

Repository → **Settings** → **Actions** → **General**

- ✅ "Allow all actions and reusable workflows" 선택
- ✅ "Read and write permissions" 선택 (파일 커밋용)

---

### 3단계: 실행 스케줄

**3단계로 분리된 자동 실행**:

- **8:00 AM** - 뉴스 수집 및 요약 생성 (`1-daily-summary.yml`)
- **8:10 AM** - YouTube Shorts 생성 (`2-youtube-shorts.yml`)
- **8:15 AM** - Instagram 카드뉴스 생성 + 자동 업로드 (`3-instagram-cardnews.yml`)

**장점**:
- ✅ 각 단계가 독립적으로 실행
- ✅ 한 단계 실패해도 다음 단계 진행
- ✅ 단계별로 수동 실행 가능

**시간 변경** (예: 오전 6시로 변경하려면):

각 워크플로우 파일에서 cron 수정:
```yaml
# 6:00 AM KST = UTC 전날 21시
- cron: '0 21 * * *'   # 1-daily-summary.yml
- cron: '10 21 * * *'  # 2-youtube-shorts.yml  
- cron: '15 21 * * *'  # 3-instagram-cardnews.yml
```

**Cron 계산**: KST - 9시간 = UTC (전날)

---

## 🎬 사용 방법

### 방법 1: 자동 실행 (권장)
매일 아침 8시부터 자동으로 순차 실행됩니다:

- **8:00** - 뉴스 수집 & 요약 (약 2-3분 소요)
- **8:10** - YouTube Shorts 생성 (약 3-5분 소요)
- **8:15** - Instagram 카드뉴스 + 업로드 (약 2-3분 소요)

**아무것도 안 해도 됩니다!**

### 방법 2: 수동 실행 (개별 단계)

특정 단계만 실행하려면:

1. GitHub Repository → **Actions** 탭
2. 원하는 워크플로우 선택:
   - `1. Daily AI Summary (8:00 AM)`
   - `2. YouTube Shorts (8:10 AM)`
   - `3. Instagram Card News (8:15 AM)`
3. **Run workflow** 버튼 클릭

### 방법 3: 전체 수동 실행

3개 워크플로우를 순서대로 수동 실행

---

## 📥 생성된 파일 다운로드

### 영상/이미지 다운로드

1. **Actions** 탭 → 실행된 워크플로우 클릭
2. 하단 **Artifacts** 섹션에서 `daily-content` 다운로드
3. ZIP 파일 압축 해제

**포함 내용**:
- `summary_YYYY-MM-DD.txt` - 요약문
- `sources_YYYY-MM-DD.json` - 원문 정보
- `shorts_output/english_short_YYYY-MM-DD.mp4` - YouTube Shorts
- `cardnews_output/en_card_*.png` - Instagram 카드뉴스 (6장)
- `cardnews_output/en_caption_YYYY-MM-DD.txt` - Instagram 캡션

---

## 📤 YouTube 업로드 (수동)

GitHub Actions는 YouTube OAuth를 지원하지 않으므로 로컬에서 업로드:

```bash
# 1. Artifacts에서 영상 다운로드
# 2. shorts_output/ 폴더에 복사
# 3. 업로드 실행

python upload_youtube.py shorts_output/english_short_2025-10-09.mp4 en
```

---

## 🔄 전체 워크플로우 (3단계 순차 실행)

```
매일 오전 8:00 (자동)
    ↓
[워크플로우 1 시작] 🕐
    ↓
1. AI 뉴스 수집 ✅
2. 요약 생성 (GPT-4o-mini) ✅
3. Notion 저장 ✅
4. GitHub 커밋 ✅
    ↓
[완료 - 8:03]
    ↓
    
매일 오전 8:10 (자동)
    ↓
[워크플로우 2 시작] 🕐
    ↓
5. 최신 요약 가져오기 ✅
6. YouTube Shorts 생성 ✅
7. Artifacts 저장 ✅
    ↓
[완료 - 8:15]
    ↓
    
매일 오전 8:15 (자동)
    ↓
[워크플로우 3 시작] 🕐
    ↓
8. 최신 요약 가져오기 ✅
9. Instagram 카드뉴스 생성 ✅
10. Instagram 자동 업로드 ✅
11. Artifacts 저장 ✅
    ↓
[완료 - 8:18] 🎉
    ↓
[수동] YouTube 업로드 (로컬에서)
```

**총 소요 시간**: 약 18분 (8:00 ~ 8:18)

---

## 📊 실행 결과 확인

### Actions 로그 보기

**전체 실행 상태 확인**:
1. **Actions** 탭에서 3개 워크플로우 상태 확인
   - ✅ 1. Daily AI Summary (8:00 AM)
   - ✅ 2. YouTube Shorts (8:10 AM)
   - ✅ 3. Instagram Card News (8:15 AM)

**개별 로그 확인**:
1. 워크플로우 클릭
2. 각 단계별 로그 확인
3. 성공/실패 여부 확인

### Instagram 확인
자동 업로드가 성공하면 즉시 Instagram에 게시됩니다!
- 계정: `.env`의 `INSTAGRAM_USERNAME`에 설정한 계정
- 캐러셀 포스트로 6장 업로드됨

### Notion 확인
요약문이 자동으로 Notion 데이터베이스에 저장됩니다.

---

## ⚙️ 고급 설정

### 1. 여러 SNS 계정 관리

다중 계정을 위한 Matrix 전략:

```yaml
jobs:
  generate-content:
    strategy:
      matrix:
        account: [account1, account2]
    steps:
      - name: Upload to Instagram
        env:
          INSTAGRAM_USERNAME: ${{ secrets[format('INSTAGRAM_USERNAME_{0}', matrix.account)] }}
          INSTAGRAM_PASSWORD: ${{ secrets[format('INSTAGRAM_PASSWORD_{0}', matrix.account)] }}
```

### 2. 알림 설정

Slack/Discord 알림 추가:

```yaml
- name: Send notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 3. 실패 시 재시도

```yaml
- name: Upload to Instagram
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: python upload_instagram_simple.py --date $(date +%Y-%m-%d)
```

---

## 🛠️ 문제 해결

### Q1: Actions가 실행되지 않아요

**원인**: Actions 권한 문제

**해결**:
1. Settings → Actions → General
2. "Allow all actions" 활성화
3. "Read and write permissions" 활성화

### Q2: Instagram 업로드 실패

**원인**: 비밀번호 오류 또는 2FA

**해결**:
1. 2FA 사용 시 앱 비밀번호 생성
2. Secrets에 올바른 비밀번호 등록
3. Actions 로그에서 상세 에러 확인

### Q3: FFmpeg 에러

**원인**: Ubuntu에서 FFmpeg 설치 문제

**해결**: 워크플로우에 이미 포함됨 (자동 설치)

### Q4: 용량 초과

**원인**: GitHub Artifacts 용량 제한 (500MB)

**해결**:
- 영상 압축 설정 조정
- retention-days를 7일로 제한 (기본값)

---

## 💰 비용

### GitHub Actions
- **무료 플랜**: 월 2,000분 제공
- **이 워크플로우**: 약 5-10분/일 소요
- **월 사용량**: 150-300분 (무료 한도 내)

### API 비용
- OpenAI: ~$0.07/일
- Notion: 무료
- Instagram: 무료
- **월 총 비용**: ~$2

---

## 🎉 완전 자동화 달성!

이제 컴퓨터를 켜지 않아도:
- ✅ 매일 자동으로 AI 뉴스 수집
- ✅ 요약문 생성 및 Notion 저장
- ✅ YouTube Shorts 생성
- ✅ Instagram 카드뉴스 생성 및 업로드
- ✅ 모든 파일 GitHub에 백업

**단 한 번만 수동**: YouTube 영상 업로드 (OAuth 제약)

---

## 📚 참고 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Cron 표현식 생성기](https://crontab.guru/)
- [GitHub Actions 사용량](https://github.com/settings/billing)

---

## 🔐 보안 주의사항

1. **절대 공개하지 마세요**:
   - `.env` 파일
   - API 키
   - Instagram 비밀번호

2. **GitHub Secrets 사용**:
   - 모든 민감 정보는 Secrets에 저장
   - 코드에 직접 작성 금지

3. **Private Repository 권장**:
   - API 키가 포함된 프로젝트는 Private으로 설정

---

**🚀 이제 완전 자동화된 AI 뉴스 콘텐츠 생산 시스템이 완성되었습니다!**

