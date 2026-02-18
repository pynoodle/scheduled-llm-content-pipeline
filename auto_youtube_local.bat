@echo off
REM AI InsightLens - YouTube Shorts Local Generation & Upload
REM 로컬에서 영상 생성 및 YouTube 업로드

echo ============================================================
echo   AI InsightLens - YouTube Shorts (Local)
echo ============================================================
echo.

cd /d C:\Users\yoonj\Documents\AI_InsightLens

REM 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment not found, using global Python
)

echo [Step 1/3] Pulling latest changes from GitHub...
git pull origin main

echo.
echo [Step 2/3] Checking for today's summary...
for /f "tokens=*" %%a in ('python -c "from datetime import datetime; print(datetime.now().strftime('%%Y-%%m-%%d'))"') do set TODAY=%%a
echo Today's date: %TODAY%

if not exist "summary_%TODAY%.txt" (
    echo [ERROR] Summary file not found for %TODAY%
    echo Please check if GitHub Actions completed successfully.
    echo GitHub Actions URL: https://github.com/pynoodle/AI_InsightLens/actions
    pause
    exit /b 1
)

echo [OK] Summary file found!

REM 오늘 영상이 이미 있는지 확인
if exist "shorts_output\english_short_%TODAY%.mp4" (
    echo [INFO] Video already exists for today
) else (
    echo.
    echo [Generating] Creating YouTube Shorts from summary...
    python generate_shorts.py "summary_%TODAY%.txt"
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to generate shorts
        pause
        exit /b 1
    )
    
    echo [OK] Shorts generated successfully!
)

echo.
echo [Step 3/3] Uploading to YouTube...
python upload_youtube.py "shorts_output\english_short_%TODAY%.mp4" en

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   YouTube Upload Complete! ✓
    echo ============================================================
    echo.
    echo Check: https://studio.youtube.com
) else (
    echo.
    echo [ERROR] YouTube upload failed. Please check the error above.
    pause
    exit /b 1
)

echo.
echo Done!
REM Auto-close after 3 seconds
timeout /t 3 /nobreak >nul 2>&1

