# ⏰ Windows 작업 스케줄러 설정 가이드

**로컬 PC에서 매일 자동 실행을 위한 상세 가이드**

## 🎯 설정할 작업

### 방식 1: GitHub Actions + 로컬 업로드

**작업 1: Artifact 다운로드 및 YouTube 업로드**
- 실행 시간: **매일 오전 8:10**
- 배치 파일: `auto_upload_daily.bat`
- 소요 시간: 1-2분

### 방식 2: 완전 로컬 실행

**작업 2: 전체 파이프라인 (뉴스→요약→쇼츠→업로드)**
- 실행 시간: **매일 오전 8:00**
- 배치 파일: `run_daily.bat`
- 소요 시간: 3-5분

## 📋 상세 설정 방법

### 1단계: 작업 스케줄러 열기

```
Windows + R 키 누르기
  ↓
"taskschd.msc" 입력
  ↓
Enter 키 누르기
```

### 2단계: 작업 만들기

1. **왼쪽 패널**: "작업 스케줄러 라이브러리" 클릭
2. **오른쪽 패널**: "작업 만들기..." 클릭

### 3단계: 일반 탭 설정

| 항목 | 설정값 |
|------|--------|
| **이름** | `AI InsightLens Auto Upload` |
| **설명** | `GitHub Actions에서 생성된 쇼츠를 YouTube에 자동 업로드` |
| **보안 옵션** | ✅ 사용자의 로그온 여부에 관계없이 실행 |
| | ✅ 가장 높은 수준의 권한으로 실행 |
| **구성 대상** | Windows 10 |

### 4단계: 트리거 탭 설정

1. **"새로 만들기..." 버튼** 클릭

2. **기본 설정**:
   - 작업 시작: **일정**
   - 설정: **한 번**
   - 시작: **오늘 날짜, 오전 8:10:00**
   
3. **고급 설정**:
   - ✅ **사용**
   - 반복 간격: 설정 안 함 (매일 실행)
   - 작업 중지 시간: 설정 안 함
   
4. **매일 실행으로 변경**:
   - 설정을 **한 번**에서 **매일**로 변경
   - 시작: **2025-10-09 오전 8:10:00**
   - 되풀이 간격: **1일마다**
   
5. **확인** 클릭

### 5단계: 동작 탭 설정

1. **"새로 만들기..." 버튼** 클릭

2. **동작 설정**:
   - 작업: **프로그램 시작**
   - 프로그램/스크립트: 
     ```
     C:\Users\yoonj\Documents\AI_InsightLens\auto_upload_daily.bat
     ```
   - 인수 추가(옵션): 비워둠
   - 시작 위치(옵션):
     ```
     C:\Users\yoonj\Documents\AI_InsightLens
     ```

3. **확인** 클릭

### 6단계: 조건 탭 설정

**전원 옵션 (중요!)**:
- ❌ **컴퓨터의 전원이 AC일 때만 작업 시작** (체크 해제)
- ❌ **작업을 실행하기 위해 컴퓨터를 절전 모드에서 해제** (선택 사항)

**네트워크 옵션**:
- 설정 안 함 (기본값)

### 7단계: 설정 탭 설정

| 옵션 | 설정 |
|------|------|
| **요청 시 작업 실행 허용** | ✅ |
| **예정된 시작을 놓친 경우 즉시 작업 실행** | ✅ |
| **작업이 실패하면 다시 시작** | ✅ (간격: 1분, 시도: 3회) |
| **작업이 요청 시 중지되지 않으면 강제로 중지** | ✅ (3시간 후) |
| **작업이 이미 실행 중인 경우** | 새 인스턴스 시작 안 함 |

### 8단계: 저장 및 확인

1. **확인** 버튼 클릭
2. Windows 계정 암호 입력 (필요한 경우)
3. 작업 목록에서 생성된 작업 확인

## ✅ 테스트 실행

### 즉시 테스트하기

1. 작업 목록에서 **"AI InsightLens Auto Upload"** 우클릭
2. **"실행"** 클릭
3. 명령 프롬프트 창이 열리면서 실행
4. 완료 후 결과 확인:
   - ✅ Notion 페이지 생성
   - ✅ YouTube 쇼츠 업로드
   - ✅ 로그 출력

### 스케줄 확인

1. 작업 우클릭 > **"속성"**
2. **트리거** 탭에서 다음 실행 시간 확인
3. **기록** 탭에서 실행 이력 확인

## 🎯 두 가지 작업 설정 (권장)

### 작업 1: Auto Upload (GitHub Actions용)

| 설정 | 값 |
|------|-----|
| 이름 | `AI InsightLens Auto Upload` |
| 시간 | **매일 오전 8:10** |
| 파일 | `auto_upload_daily.bat` |
| 설명 | GitHub Actions 쇼츠를 YouTube 업로드 |

### 작업 2: Full Pipeline (완전 로컬용)

| 설정 | 값 |
|------|-----|
| 이름 | `AI InsightLens Full Pipeline` |
| 시간 | **매일 오전 8:00** |
| 파일 | `run_daily.bat` |
| 설명 | 뉴스 수집부터 업로드까지 전체 실행 |
| 상태 | **비활성화** (GitHub Actions 사용 시) |

**참고:** 두 작업을 동시에 활성화하지 마세요! 하나만 선택하세요.

## 📊 실행 시간표

### GitHub Actions + 로컬 업로드 (추천)

```
8:00 AM - GitHub Actions 시작 (서버)
  ↓
8:05 AM - Notion 저장 완료
  ↓
8:10 AM - 로컬 PC: Artifact 다운로드 시작
  ↓
8:11 AM - YouTube 업로드 완료
```

### 완전 로컬 실행

```
8:00 AM - 로컬 PC: 전체 파이프라인 시작
  ↓
8:05 AM - YouTube 업로드 완료
```

## 🛠️ 문제 해결

### "작업이 실행되지 않음"

**확인 사항:**
1. 트리거 시간이 올바른지 확인
2. "사용" 체크박스가 선택되어 있는지 확인
3. "컴퓨터의 전원이 AC일 때만" 옵션 **해제** 확인
4. PC가 해당 시간에 켜져 있는지 확인

**해결:**
```
작업 우클릭 > 속성 > 트리거 탭
  ↓
시간 재확인 및 수정
  ↓
확인 > 다시 실행
```

### "배치 파일 경로를 찾을 수 없음"

**확인:**
```powershell
# PowerShell에서 경로 확인
Test-Path "C:\Users\yoonj\Documents\AI_InsightLens\auto_upload_daily.bat"
# True가 나와야 정상
```

**해결:**
- 프로그램/스크립트 경로를 절대 경로로 다시 입력
- 시작 위치도 함께 설정

### "권한 오류"

**해결:**
1. 작업 우클릭 > 속성 > 일반 탭
2. "가장 높은 수준의 권한으로 실행" 체크
3. 확인 > 암호 재입력

### "GitHub CLI 인증 오류" (auto_upload_daily.bat)

**해결:**
```bash
# PowerShell에서
gh auth login

# 브라우저에서 인증 완료
```

## 📝 배치 파일 위치

### 파일 확인

```
C:\Users\yoonj\Documents\AI_InsightLens\
  ├── auto_upload_daily.bat    (Artifact 다운로드 + YouTube 업로드)
  ├── run_daily.bat             (전체 파이프라인)
  ├── run_full_pipeline.py      (Python 통합 스크립트)
  ├── download_and_upload.py    (Artifact 다운로드)
  └── upload_youtube.py         (YouTube 업로드)
```

## 🔔 알림 설정 (선택)

### 이메일 알림

`.env` 파일에서:
```env
EMAIL_ENABLE=true
EMAIL_TO=your_email@gmail.com
```

### Windows 알림

작업 설정 > 설정 탭:
- "작업이 완료되면 알림 표시" (Windows 11)

## 📚 관련 문서

- [GITHUB_AUTOMATION.md](GITHUB_AUTOMATION.md) - GitHub Actions 자동화
- [YOUTUBE_AUTOMATION.md](YOUTUBE_AUTOMATION.md) - YouTube 업로드
- [README.md](README.md) - 전체 가이드

---

**작업 스케줄러 설정 완료!** 이제 매일 자동으로 실행됩니다! ⏰

