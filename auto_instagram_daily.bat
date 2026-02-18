@echo off
REM AI InsightLens - Instagram Card News Auto Upload (Local)
REM GitHub Actions에서 이미지 생성 완료 후 로컬에서 Instagram 업로드

echo ============================================================
echo   AI InsightLens - Instagram Auto Upload
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
echo [Step 2/3] Checking for today's card news images...
for /f "tokens=*" %%a in ('python -c "from datetime import datetime; print(datetime.now().strftime('%%Y-%%m-%%d'))"') do set TODAY=%%a
echo Today's date: %TODAY%

if not exist "cardnews_output\en_card_00_intro_%TODAY%.png" (
    echo [ERROR] Card news images not found for %TODAY%
    echo Please check if GitHub Actions completed successfully.
    echo GitHub Actions URL: https://github.com/pynoodle/AI_InsightLens/actions
    pause
    exit /b 1
)

echo [OK] Card news images found!

echo.
echo [Step 3/3] Uploading to Instagram...
python upload_instagram_simple.py --date %TODAY%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   Instagram Upload Complete! ✓
    echo ============================================================
) else (
    echo.
    echo [ERROR] Instagram upload failed. Please check the error above.
    pause
    exit /b 1
)

echo.
echo Done!
REM Auto-close after 3 seconds
timeout /t 3 /nobreak >nul 2>&1

