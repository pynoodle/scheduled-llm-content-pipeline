# 🤖 AI InsightLens

> **Built:** October 2025

**매일 자동으로 AI 뉴스를 수집, 요약하고 YouTube Shorts + Instagram 카드뉴스를 만들어 업로드하는 완전 자동화 시스템**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 주요 기능

### 📰 자동 뉴스 수집 (28개 소스)
- **AI 연구**: arXiv (cs.AI, cs.LG, cs.CL)
- **빅테크**: OpenAI, Anthropic, Google DeepMind, Meta AI, NVIDIA, Microsoft
- **VC/투자**: TechCrunch, VentureBeat, a16z, Y Combinator
- **주식 전망**: 애널리스트 리포트 및 시장 데이터

### 🧠 AI 요약 생성
- **GPT-4o-mini** 기반 고품질 요약
- **영어/한글** 이중 버전
- **소스별** 개조식 정리
- **시장 분석** 및 트렌드 인사이트

### 📊 Notion 자동 연동
- 일일 요약 자동 저장
- 태그 자동 분류
- 출처 및 시장 데이터 기록

### 🎬 YouTube Shorts 자동 생성
- **전문적인 디자인**: 그라디언트, 애니메이션, 글로우 효과
- **바 그래프 주가 차트**: 상승↑/하락↓ 색상 구분
- **OpenAI TTS**: 자연스러운 음성 나레이션
- **배경 음악**: 자동 믹싱 (15% 볼륨)
- **완벽한 동기화**: 화면-음성 타이밍 매칭

### 📸 Instagram/Threads 카드뉴스 생성
- **자동 이미지 생성**: 요약문에서 핵심 내용 3-5개 추출
- **1080x1080 정사각형**: Instagram/Threads 최적화
- **화려한 디자인**: 그라디언트 배경, 슬라이드별 색상 변화
- **해시태그 자동 추출**: SNS 친화적 해시태그 포함
- **다국어 지원**: 영어/한글 카드뉴스

### 📤 자동 업로드
- **YouTube**: OAuth 인증으로 자동 업로드
- **Instagram**: 간편 자동 업로드 (Instagrapi) ✨ NEW
  - 5분 설정 / 로컬 파일 직접 업로드
  - 캐러셀 포스트 자동 생성
  - 캡션 자동 추가
- **메타데이터 자동 생성**: 제목, 설명, 태그, 해시태그

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/pynoodle/AI_InsightLens.git
cd AI_InsightLens

# 가상환경 생성
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```env
# OpenAI API (필수)
OPENAI_API_KEY=sk-proj-your-key-here

# Notion (필수)
NOTION_TOKEN=ntn_your-token-here
NOTION_DB_ID=your-database-id-here

# Instagram 자동 업로드 (선택)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Alpha Vantage (선택 - 시장 데이터 백업)
ALPHA_VANTAGE_KEY=your-key-here

# Email (선택)
EMAIL_ENABLE=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@gmail.com
```

### 3. YouTube API 설정 (선택)

YouTube 자동 업로드를 원한다면:

1. [YOUTUBE_AUTOMATION.md](YOUTUBE_AUTOMATION.md) 가이드 참조
2. Google Cloud Console에서 OAuth credentials 생성
3. `client_secrets.json` 다운로드 및 저장
4. 첫 인증 실행:

```bash
python upload_youtube.py shorts_output/english_short_2025-10-09.mp4 en
```

### 4. Instagram 자동 업로드 설정 (선택) ✨ NEW

Instagram 자동 업로드를 원한다면 (5분 설정!):

1. Instagrapi 설치:
```bash
pip install instagrapi
```

2. `.env`에 로그인 정보 추가 (위 참조)

3. 테스트 실행:
```bash
python upload_instagram_simple.py --test
```

4. 실제 업로드:
```bash
python upload_instagram_simple.py --date 2025-10-09
```

자세한 내용: [INSTAGRAM_QUICK_START.md](INSTAGRAM_QUICK_START.md)

## 📖 사용법

### 방법 1: 개별 실행

```bash
# 1. 뉴스 수집 및 요약 생성
python run_insightlens_ai_only.py

# 2. YouTube Shorts 생성
python generate_shorts.py summary_2025-10-09.txt

# 3. Instagram 카드뉴스 생성
python generate_cardnews.py summary_2025-10-09.txt --lang en --slides 5

# 4. YouTube 업로드
python upload_youtube.py shorts_output/english_short_2025-10-09.mp4 en

# 5. Instagram 업로드 (간편 자동화) ✨ NEW
python upload_instagram_simple.py --date 2025-10-09
```

### 방법 2: 전체 파이프라인 실행 (추천!)

```bash
# 뉴스 수집 → 요약 → 쇼츠 → 카드뉴스 → 업로드 (한 번에!)
python run_full_pipeline.py
```

**자동으로 생성되는 콘텐츠:**
- ✅ Notion에 요약 저장
- ✅ YouTube Shorts 영상
- ✅ Instagram 카드뉴스 이미지 (주식정보 포함)
- ✅ Instagram 캡션 (출처 포함)
- ✅ YouTube 자동 업로드
- ✅ Instagram 자동 업로드 (선택) ✨ NEW

### 방법 3: Windows 배치 파일

```bash
# 더블클릭 실행
run_daily.bat
```

### 방법 4: 완전 자동화 (작업 스케줄러)

Windows 작업 스케줄러 설정:
- [YOUTUBE_AUTOMATION.md](YOUTUBE_AUTOMATION.md) 참조
- 매일 오전 10시 자동 실행
- 컴퓨터만 켜져 있으면 자동!

## 📁 프로젝트 구조

```
AI_InsightLens/
├── run_insightlens_ai_only.py   # 뉴스 수집 및 요약 생성
├── generate_shorts.py            # YouTube Shorts 생성
├── generate_cardnews.py          # Instagram 카드뉴스 생성
├── upload_youtube.py             # YouTube 자동 업로드
├── upload_instagram.py           # Instagram 업로드 (Graph API)
├── upload_instagram_simple.py   # Instagram 간편 업로드 ✨ NEW
├── run_full_pipeline.py          # 전체 파이프라인 통합
├── run_daily.bat                 # Windows 배치 파일
├── requirements.txt              # Python 의존성
├── .env                          # 환경 변수 (생성 필요)
├── .gitignore                    # Git 제외 파일
├── README.md                     # 이 파일
├── YOUTUBE_AUTOMATION.md         # YouTube 자동화 가이드
├── CARDNEWS_AUTOMATION.md        # 카드뉴스 자동화 가이드
├── INSTAGRAM_QUICK_START.md     # Instagram 5분 설정 ✨ NEW
├── INSTAGRAM_AUTOMATION_OPTIONS.md  # Instagram 방법 비교 ✨ NEW
├── SHORTS_SETUP.md               # 쇼츠 생성 가이드
├── BACKGROUND_MUSIC.md           # 배경 음악 가이드
├── shorts_output/                # 생성된 쇼츠 (자동 생성)
│   ├── english_short_YYYY-MM-DD.mp4
│   ├── background_music.mp3      # 선택 사항
│   └── temp_*.png                # 임시 파일 (자동 삭제)
└── cardnews_output/              # 생성된 카드뉴스 (자동 생성)
    ├── en_card_00_intro_YYYY-MM-DD.png
    ├── en_card_01~03_YYYY-MM-DD.png  # 뉴스 카드
    ├── en_card_04_market_YYYY-MM-DD.png  # 주식정보 ✨ NEW
    ├── en_card_05_outro_YYYY-MM-DD.png
    └── en_caption_YYYY-MM-DD.txt  # Instagram 캡션 ✨ NEW
```

## 🎨 콘텐츠 예시

### YouTube Shorts (44초)

1. **인트로** (2초) - 날짜 및 제목
2. **핵심 포인트 4개** (27초) - 주요 뉴스
3. **주가 차트** (11초) - 바 그래프 시각화
4. **아웃트로** (2초) - 구독 유도

**디자인 특징:**
- 🎨 그라디언트 배경
- ✨ 페이드 인/아웃 애니메이션
- 💫 글로우 효과
- 📊 색상 구분 (상승↑ 초록, 하락↓ 빨강)
- 🎵 배경 음악 (15% 볼륨)

### Instagram 카드뉴스 (5장)

1. **인트로** - "AI NEWS TODAY" + 날짜
2. **뉴스 1-3** - 제목 + 내용 + 출처
3. **아웃트로** - "FOLLOW FOR MORE" + 해시태그

**디자인 특징:**
- 📱 1080x1080 정사각형
- 🎨 슬라이드별 다른 그라디언트
- ✨ 글로우 효과 & 그림자
- 📊 깔끔한 타이포그래피
- #️⃣ 자동 해시태그

## 💰 비용

### 일일 운영 비용 (약 $0.08/일)

| 항목 | 비용 |
|------|------|
| OpenAI GPT-4o-mini (요약) | ~$0.02 |
| OpenAI TTS (5개 섹션) | ~$0.04 |
| OpenAI GPT-4o-mini (카드뉴스 추출) | ~$0.01 |
| PIL 이미지 생성 | 무료 |
| **합계** | **~$0.07/일** |

**월 비용: $2 이하!**

### 무료 항목
- ✅ YouTube API (일일 할당량 내)
- ✅ Instagram Graph API (무료)
- ✅ Notion API
- ✅ RSS/arXiv 수집
- ✅ Alpha Vantage (무료 플랜)
- ✅ PIL/Pillow (이미지 생성)

## 🔧 고급 설정

### 배경 음악 추가

1. 무료 음원 다운로드:
   - [Pixabay Music](https://pixabay.com/music/)
   - [YouTube Audio Library](https://studio.youtube.com/channel/audio_library)

2. 저장:
   ```
   shorts_output/background_music.mp3
   ```

3. 자동으로 15% 볼륨으로 믹싱됨!

### RSS 소스 커스터마이징

`run_insightlens_ai_only.py`에서 `RSS_SOURCES` 수정:

```python
RSS_SOURCES = [
    "https://blog.openai.com/rss/",  # 추가/삭제 가능
    # ... 더 많은 소스
]
```

### 쇼츠 디자인 변경

`generate_shorts.py`에서:
- `create_text_image()`: 색상, 폰트 크기
- `create_market_image_pro()`: 바 그래프 스타일
- 배경색, 애니메이션 효과 등

### 카드뉴스 디자인 변경

`generate_cardnews.py`에서:
- `colors`: 슬라이드별 그라디언트 색상
- `create_intro_card()`: 인트로 디자인
- `create_content_card()`: 본문 카드 레이아웃
- 폰트 크기, 텍스트 래핑 등

자세한 내용은 [CARDNEWS_AUTOMATION.md](CARDNEWS_AUTOMATION.md) 참조

## 🌟 GitHub Actions 완전 자동화 ✨ NEW

**매일 아침 8시 자동 실행** (3단계 순차):

- **8:00** - 뉴스 수집 & 요약 생성
- **8:10** - YouTube Shorts 생성
- **8:15** - Instagram 카드뉴스 + 자동 업로드

**설정 방법**: [GITHUB_AUTOMATION_GUIDE.md](GITHUB_AUTOMATION_GUIDE.md) 참조

**장점**:
- ✅ 컴퓨터 꺼져 있어도 자동 실행
- ✅ Instagram 자동 게시
- ✅ 모든 파일 GitHub Artifacts 백업
- ⚠️ YouTube만 수동 업로드 (1분 소요)

## 🛠️ 문제 해결

### "OpenAI API Error"

```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# 키가 유효한지 테스트
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### "Notion 404 Not Found"

```bash
# 데이터베이스 ID 확인
# Notion 페이지 URL에서: 
# https://www.notion.so/{DATABASE_ID}?v=...

# Integration이 데이터베이스에 공유되었는지 확인
```

### "YouTube upload failed"

```bash
# 재인증
del token.pickle
python upload_youtube.py shorts_output/english_short_2025-10-09.mp4 en

# client_secrets.json 확인
dir client_secrets.json
```

### "ffmpeg not found"

Windows:
```bash
# Chocolatey 사용
choco install ffmpeg

# 또는 수동 설치
# https://www.gyan.dev/ffmpeg/builds/
```

macOS:
```bash
brew install ffmpeg
```

Linux:
```bash
sudo apt-get install ffmpeg
```

## 📚 참고 문서

- [YOUTUBE_AUTOMATION.md](YOUTUBE_AUTOMATION.md) - YouTube 자동화 완전 가이드
- [CARDNEWS_AUTOMATION.md](CARDNEWS_AUTOMATION.md) - 카드뉴스 자동화 가이드
- **[INSTAGRAM_QUICK_START.md](INSTAGRAM_QUICK_START.md) - Instagram 5분 설정 가이드** ✨ NEW
- [INSTAGRAM_AUTOMATION_OPTIONS.md](INSTAGRAM_AUTOMATION_OPTIONS.md) - Instagram 자동화 방법 비교
- [SHORTS_SETUP.md](SHORTS_SETUP.md) - 쇼츠 생성 상세 가이드
- [BACKGROUND_MUSIC.md](BACKGROUND_MUSIC.md) - 배경 음악 추가 방법

## 🤝 기여

이슈 및 PR 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

## 🙏 감사

- OpenAI (GPT-4, TTS)
- Notion API
- YouTube Data API v3
- MoviePy
- Pillow (PIL)
- feedparser

## 📧 연락처

문의: GitHub Issues를 통해 문의해 주세요

GitHub: [@pynoodle](https://github.com/pynoodle)

---

**⭐ 이 프로젝트가 유용하다면 Star를 눌러주세요!**

Made with ❤️ by AI & Automation
