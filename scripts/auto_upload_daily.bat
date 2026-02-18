@echo off
REM GitHub Actions에서 생성된 쇼츠를 자동으로 다운로드하고 YouTube에 업로드

echo ============================================================
echo   AI InsightLens - Auto Download ^& Upload to YouTube
echo ============================================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 가상환경 활성화
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Artifact 다운로드 및 YouTube 업로드
echo [2/3] Downloading latest shorts and uploading to YouTube...
echo ============================================================
python download_and_upload.py
set UPLOAD_EXIT_CODE=%ERRORLEVEL%
echo.

REM 결과 확인
if %UPLOAD_EXIT_CODE% EQU 0 (
    echo ============================================================
    echo   🎉 Upload completed successfully!
    echo ============================================================
    echo.
    echo ✅ Check YouTube Studio for the new video
    echo 🔗 https://studio.youtube.com
    echo.
) else (
    echo ============================================================
    echo   ⚠️  Upload failed or no new video to upload
    echo ============================================================
    echo.
    echo Common issues:
    echo   - No new artifact from GitHub Actions
    echo   - GitHub CLI not authenticated (run: gh auth login)
    echo   - YouTube token expired (run: python upload_youtube.py ...)
    echo.
)

REM 가상환경 비활성화
echo [3/3] Deactivating virtual environment...
deactivate
echo.

echo Done!
pause
exit /b %UPLOAD_EXIT_CODE%

