# 📱 Instagram 자동 업로드 빠른 시작 가이드

**5분이면 설정 완료!**

---

## 🚀 1단계: 라이브러리 설치 (1분)

```bash
pip install instagrapi
```

---

## 🔑 2단계: Instagram 로그인 정보 설정 (1분)

`.env` 파일에 추가:

```env
# Instagram 자동 업로드
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### ⚠️ 2FA(이중 인증) 사용 중이라면?

Instagram 앱 비밀번호를 사용하세요:

1. Instagram 앱 → 설정 → 보안 → 앱 및 웹사이트
2. "비밀번호 생성" 클릭
3. 생성된 비밀번호를 `.env`에 입력

---

## 📸 3단계: 업로드 실행 (1분)

### 기본 사용법

```bash
# 가장 최근 카드뉴스 자동 업로드
python upload_instagram_simple.py

# 특정 날짜 카드뉴스 업로드
python upload_instagram_simple.py --date 2025-10-09

# 캡션 파일 지정
python upload_instagram_simple.py --date 2025-10-09 --caption cardnews_output/en_caption_2025-10-09.txt
```

### 테스트 (업로드 없이 파일만 확인)

```bash
python upload_instagram_simple.py --test --date 2025-10-09
```

---

## 🎉 완료!

업로드가 성공하면 다음과 같이 표시됩니다:

```
============================================================
  업로드 성공!
============================================================
  Media ID: 1234567890
  URL: https://www.instagram.com/p/ABC123/
  이미지: 6장
  날짜: 2025-10-09
============================================================
```

---

## 🔄 전체 파이프라인에 통합

`run_full_pipeline.py`에 Instagram 업로드 단계를 추가할 수 있습니다:

```python
# 5단계: Instagram 자동 업로드
print(f"\n📱 [STEP 5/5] Uploading to Instagram...")
print("-" * 60)

try:
    import upload_instagram_simple
    
    success = upload_instagram_simple.upload_cardnews_to_instagram(
        "cardnews_output",
        date_str=date_kst
    )
    
    if success:
        print("✅ Instagram upload successful!")
    else:
        print("⚠️  Instagram upload skipped")
        
except Exception as e:
    print(f"⚠️  Instagram upload failed: {e}")
    print("   You can upload manually from cardnews_output/")
```

---

## ⚠️ 중요 주의사항

### 1. 사용량 제한
- **하루 20개 이하** 포스팅 권장
- 너무 자주 업로드하면 봇으로 감지될 수 있음
- 최소 1-2분 간격 유지

### 2. 계정 보안
- `.env` 파일을 절대 공유하지 마세요
- `.gitignore`에 포함되어 있는지 확인

### 3. 비공식 API 사용
- Instagrapi는 비공식 API입니다
- Instagram 정책 변경 시 작동 중단 가능
- 개인 사용 목적으로만 권장

---

## 🛠️ 문제 해결

### Q1: "로그인 실패" 에러

**원인**: 비밀번호 오류 또는 2FA 활성화

**해결**:
1. Instagram 앱에서 로그인이 되는지 확인
2. 2FA 사용 중이면 앱 비밀번호 생성
3. `.env` 파일의 아이디/비밀번호 확인

### Q2: "Challenge required" 에러

**원인**: Instagram 보안 확인 필요

**해결**:
1. Instagram 앱 또는 웹에서 로그인
2. 보안 확인 완료 (문자 인증 등)
3. 다시 시도

### Q3: "Upload failed" 에러

**원인**: 이미지 형식 문제 또는 네트워크 오류

**해결**:
1. 이미지 파일이 존재하는지 확인
2. 파일 크기 확인 (10MB 이하 권장)
3. VPN 사용 중이면 해제
4. 인터넷 연결 확인

### Q4: "Too many requests" 에러

**원인**: 업로드를 너무 자주 시도함

**해결**:
1. 1-2시간 후 다시 시도
2. 하루 20개 이하로 제한
3. 업로드 간격 2-3분 유지

---

## 🎯 고급 기능

### 예약 포스팅

현재 Instagrapi는 즉시 포스팅만 지원합니다. 예약 포스팅이 필요하다면:

1. **Windows 작업 스케줄러** 사용
2. **Buffer, Hootsuite** 같은 유료 서비스 사용
3. **Instagram Graph API** 사용 (비즈니스 계정)

### 여러 계정 관리

`.env` 파일을 여러 개 만들어 관리:

```bash
# 계정 1 업로드
python upload_instagram_simple.py --env .env.account1

# 계정 2 업로드  
python upload_instagram_simple.py --env .env.account2
```

---

## 📚 더 알아보기

- **안정적인 방법**: `CARDNEWS_AUTOMATION.md` - Instagram Graph API 가이드
- **방법 비교**: `INSTAGRAM_AUTOMATION_OPTIONS.md` - 4가지 방법 비교
- **Instagrapi 문서**: https://github.com/subzeroid/instagrapi

---

## 🎉 이제 완전 자동화!

```
매일 자동으로:
1. AI 뉴스 수집 ✅
2. 요약 생성 ✅
3. YouTube Shorts 생성 ✅
4. Instagram 카드뉴스 생성 ✅
5. YouTube 업로드 ✅
6. Instagram 업로드 ✅ NEW!
```

모두 자동화되었습니다! 🚀

