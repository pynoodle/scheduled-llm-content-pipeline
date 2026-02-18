# 🏠 로컬 자동화 설정 가이드

**Instagram 보안 문제 해결**: GitHub Actions 대신 로컬 PC에서 자동 업로드

---

## 🎯 자동화 구조

### GitHub Actions (서버에서 실행)
- **8:00 AM** - 뉴스 수집 + AI 요약 + Notion 업로드 ✅
- **8:10 AM** - YouTube Shorts 영상 생성 ✅
- **8:15 AM** - Instagram 카드뉴스 이미지 생성 ✅

### 로컬 PC (Windows 작업 스케줄러)
- **8:20 AM** - YouTube Shorts 업로드 🏠
- **8:25 AM** - Instagram 카드뉴스 업로드 🏠

**장점:**
- ✅ 항상 같은 위치/디바이스에서 로그인
- ✅ Instagram 보안 경고 없음
- ✅ 계정 안전

---

## ⚙️ Windows 작업 스케줄러 설정

### 1단계: 작업 스케줄러 열기

1. **Win + R** 키를 누름
2. `taskschd.msc` 입력 후 **확인**
3. 작업 스케줄러가 열림

---

### 2단계: YouTube 자동 업로드 작업 생성

#### 2-1. 새 작업 만들기

1. 오른쪽 패널에서 **"작업 만들기..."** 클릭

#### 2-2. 일반 탭

- **이름**: `AI InsightLens - YouTube Upload`
- **설명**: `GitHub Actions에서 생성된 YouTube Shorts 자동 업로드`
- **보안 옵션**:
  - ✅ 사용자가 로그온할 때만 실행
  - ⬜ 가장 높은 수준의 권한으로 실행 (체크 해제)

#### 2-3. 트리거 탭

1. **새로 만들기** 클릭
2. **작업 시작**: "일정에 따라"
3. **설정**: 매일
4. **시작 시간**: `오전 8:20`
5. **고급 설정**:
   - ✅ 사용
   - 반복 간격: (비워두기)
6. **확인**

#### 2-4. 동작 탭

1. **새로 만들기** 클릭
2. **동작**: "프로그램 시작"
3. **프로그램/스크립트**:
   ```
   C:\Users\yoonj\Documents\AI_InsightLens\auto_upload_daily.bat
   ```
4. **시작 위치(선택 사항)**:
   ```
   C:\Users\yoonj\Documents\AI_InsightLens
   ```
5. **확인**

#### 2-5. 조건 탭

- ⬜ 컴퓨터의 전원이 AC 전원일 때만 작업 시작 (체크 해제)
- ⬜ 작업을 실행하려면 컴퓨터를 절전 모드에서 해제 (체크 해제)

#### 2-6. 설정 탭

- ✅ 작업이 실패하면 다시 시작 간격: 1분
- 다시 시도 횟수: 3번

#### 2-7. 저장

**확인** 클릭하여 작업 저장

---

### 3단계: Instagram 자동 업로드 작업 생성

#### 3-1. 새 작업 만들기

1. 오른쪽 패널에서 **"작업 만들기..."** 클릭

#### 3-2. 일반 탭

- **이름**: `AI InsightLens - Instagram Upload`
- **설명**: `GitHub Actions에서 생성된 Instagram 카드뉴스 자동 업로드`
- **보안 옵션**:
  - ✅ 사용자가 로그온할 때만 실행
  - ⬜ 가장 높은 수준의 권한으로 실행 (체크 해제)

#### 3-3. 트리거 탭

1. **새로 만들기** 클릭
2. **작업 시작**: "일정에 따라"
3. **설정**: 매일
4. **시작 시간**: `오전 8:25`
5. **고급 설정**:
   - ✅ 사용
6. **확인**

#### 3-4. 동작 탭

1. **새로 만들기** 클릭
2. **동작**: "프로그램 시작"
3. **프로그램/스크립트**:
   ```
   C:\Users\yoonj\Documents\AI_InsightLens\auto_instagram_daily.bat
   ```
4. **시작 위치(선택 사항)**:
   ```
   C:\Users\yoonj\Documents\AI_InsightLens
   ```
5. **확인**

#### 3-5. 조건 탭

- ⬜ 컴퓨터의 전원이 AC 전원일 때만 작업 시작 (체크 해제)
- ⬜ 작업을 실행하려면 컴퓨터를 절전 모드에서 해제 (체크 해제)

#### 3-6. 설정 탭

- ✅ 작업이 실패하면 다시 시작 간격: 1분
- 다시 시도 횟수: 3번

#### 3-7. 저장

**확인** 클릭하여 작업 저장

---

## ✅ 설정 완료 확인

### 작업 목록에서 확인

1. 작업 스케줄러 왼쪽 패널: **작업 스케줄러 라이브러리**
2. 생성된 작업 확인:
   - ✅ `AI InsightLens - YouTube Upload` (매일 8:20 AM)
   - ✅ `AI InsightLens - Instagram Upload` (매일 8:25 AM)

### 수동 테스트

각 작업을 우클릭 → **실행** 클릭하여 즉시 테스트 가능

---

## 📋 전체 자동화 흐름

```
매일 오전 8:00 (GitHub Actions - 자동)
    ↓
[1] 뉴스 수집 + AI 요약 생성 ✅
    ↓ Notion 자동 저장
    ↓
매일 오전 8:10 (GitHub Actions - 자동)
    ↓
[2] YouTube Shorts 영상 생성 ✅
    ↓ Artifacts 저장
    ↓
매일 오전 8:15 (GitHub Actions - 자동)
    ↓
[3] Instagram 카드뉴스 이미지 생성 ✅
    ↓ Artifacts 저장
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
매일 오전 8:20 (로컬 PC - 자동) 🏠
    ↓
[4] YouTube Shorts 다운로드 + 업로드 ✅
    ↓
매일 오전 8:25 (로컬 PC - 자동) 🏠
    ↓
[5] Instagram 카드뉴스 업로드 ✅
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
완료! 🎉
```

**총 소요 시간**: 약 25분 (8:00 ~ 8:25)

---

## 🔧 문제 해결

### Q1: "Failed to activate virtual environment"

**원인**: 가상환경이 없거나 경로가 다름

**해결**:
```bash
cd C:\Users\yoonj\Documents\AI_InsightLens
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Q2: "Card news images not found"

**원인**: GitHub Actions가 아직 완료되지 않음

**해결**:
- GitHub Actions 완료 여부 확인: https://github.com/pynoodle/AI_InsightLens/actions
- 8:15 이후에 실행되는지 확인
- 트리거 시간을 8:25 → 8:30으로 변경

### Q3: "GitHub CLI not authenticated"

**원인**: GitHub CLI 인증이 안됨 (YouTube 업로드용)

**해결**:
```bash
# GitHub CLI 설치
winget install GitHub.cli

# 인증
gh auth login
```

### Q4: "Instagram login failed"

**원인**: Instagram 세션 만료

**해결**:
1. 수동으로 한 번 로그인:
   ```bash
   python upload_instagram_simple.py --date 2025-10-10
   ```
2. 세션이 저장되면 이후 자동 로그인

### Q5: PC가 꺼져 있으면?

**원인**: 로컬 자동화는 PC가 켜져 있어야 함

**해결**:
- **옵션 1**: 매일 아침 8시에 PC를 켜두기
- **옵션 2**: Windows 자동 부팅 설정
  - BIOS → Power Management → "Wake on RTC Alarm" 활성화
  - 매일 7:55 AM에 자동 부팅
- **옵션 3**: 오후/저녁 시간대로 스케줄 변경

---

## 🎯 다음 단계

1. ✅ Windows 작업 스케줄러에 2개 작업 등록 완료
2. 🧪 내일(10월 11일) 아침 8시 자동 실행 확인
3. 📊 1주일 후 성과 측정:
   - YouTube 조회수
   - Instagram 도달률
   - 자동화 안정성

---

## 📝 중요 사항

### PC 요구사항
- ⚠️ **매일 아침 8:20~8:30 사이에 PC가 켜져 있어야 함**
- ⚠️ 인터넷 연결 필요
- ⚠️ 절전 모드 해제 설정

### 백업 플랜
- 자동화 실패 시 수동 업로드:
  ```bash
  # YouTube
  auto_upload_daily.bat
  
  # Instagram
  auto_instagram_daily.bat
  ```

---

**완료!** 이제 Instagram 보안 경고 없이 안전하게 자동 업로드됩니다! 🎉

**문의**: GitHub Issues를 통해 문의해 주세요

