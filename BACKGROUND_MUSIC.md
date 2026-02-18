# 🎵 배경 음악 설정 가이드

쇼츠에 저작권 없는 배경 음악을 추가할 수 있습니다.

## 📥 무료 음원 다운로드

### 추천 사이트 (저작권 Free, YouTube 사용 가능)

1. **YouTube Audio Library** (가장 추천)
   - https://studio.youtube.com/channel/UC.../music
   - YouTube Studio > Audio Library
   - 필터: Genre = Electronic, Mood = Bright/Happy
   - 추천 곡: "A New Beginning", "Vibe Mountain", "Inspiring"

2. **Pixabay Music**
   - https://pixabay.com/music/
   - 완전 무료, 저작권 표시 불필요
   - 검색: "tech", "corporate", "upbeat"

3. **Free Music Archive (FMA)**
   - https://freemusicarchive.org/
   - 라이선스 확인 필수 (CC BY 또는 CC0 선택)

4. **Incompetech**
   - https://incompetech.com/music/
   - Kevin MacLeod 음악
   - 크레딧 표시 권장

5. **Bensound**
   - https://www.bensound.com/
   - 무료 라이선스 (크레딧 필요)

## 🎼 추천 곡 스타일

**YouTube Shorts에 적합한 음악:**
- ⏱ 길이: 30초 이상 (또는 짧아도 자동 반복됨)
- 🎵 장르: Electronic, Corporate, Tech, Ambient
- ⚡ 템포: Moderate to Fast (100-130 BPM)
- 📊 분위기: Energetic, Professional, Modern

**추천 검색 키워드:**
- "tech background music"
- "corporate upbeat"
- "modern electronic"
- "news background music"

## 💾 설치 방법

### 1️⃣ 음악 다운로드

위 사이트에서 마음에 드는 곡을 MP3 형식으로 다운로드

### 2️⃣ 파일 배치

다운로드한 파일을 다음 경로에 저장:

```
shorts_output/background_music.mp3
```

**파일명이 정확히 `background_music.mp3` 여야 합니다!**

### 3️⃣ 자동 적용

다음번 쇼츠 생성 시 자동으로 15% 볼륨으로 배경음악이 추가됩니다!

```bash
python generate_shorts.py summary_2025-10-09.txt
```

## ⚙️ 볼륨 조절

배경음악이 너무 크거나 작으면 `generate_shorts.py` 수정:

```python
# Line 377
bg_music = AudioFileClip(bg_music_path).volumex(0.15)  # 0.15 = 15%

# 볼륨 변경 예시:
# 0.10 = 10% (더 작게)
# 0.20 = 20% (더 크게)
# 0.05 = 5% (매우 작게)
```

## 🎬 권장 설정

**YouTube Shorts 최적 설정:**
- 배경음악 볼륨: **10-15%** (TTS 방해하지 않게)
- 음악 장르: Electronic, Ambient, Chill
- 저작권: **YouTube Content ID 등록 안 된** 곡
- BPM: 100-120 (너무 빠르지 않게)

## ✅ 테스트

배경음악을 추가한 후:

```bash
python generate_shorts.py summary_2025-10-09.txt
```

출력에서 확인:
```
  Background music added (15% volume)
```

## 📋 추천 곡 리스트

**YouTube Audio Library에서:**
1. "A New Beginning" by Bensound (Upbeat, Tech)
2. "Vibe Mountain" by T & Sugah (Electronic)
3. "Sunny" by Vibe Tracks (Bright, Corporate)
4. "Cipher" by Kevin MacLeod (Tech, Modern)

**Pixabay에서:**
1. "Modern Technology" 
2. "Digital Innovation"
3. "Tech Future"

## ❗ 주의사항

- ❌ **유료 음악 절대 사용 금지** (저작권 위반)
- ❌ **YouTube Content ID 등록된 곡** 사용 금지
- ✅ **크레딧 표시 필요한 경우** 영상 설명란에 추가:
  ```
  Music: "Song Name" by Artist Name
  License: CC BY 3.0
  ```

---

**배경음악 없이도 쇼츠는 정상 작동합니다!**

