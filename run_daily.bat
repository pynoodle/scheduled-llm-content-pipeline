@echo off
REM AI InsightLens 완전 자동화 파이프라인
REM 매일 실행: 뉴스 수집 → 요약 생성 → 쇼츠 생성 → YouTube 업로드

echo ============================================================
echo   AI InsightLens - Full Automation Pipeline
echo ============================================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 가상환경 활성화
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    echo    Please run: python -m venv .venv
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM 전체 파이프라인 실행
echo [2/4] Running full pipeline...
echo ============================================================
python run_full_pipeline.py
set PIPELINE_EXIT_CODE=%ERRORLEVEL%
echo.

REM 결과 확인
if %PIPELINE_EXIT_CODE% EQU 0 (
    echo ============================================================
    echo   🎉 All steps completed successfully!
    echo ============================================================
    echo.
    echo 📊 Check Notion for today's summary
    echo 🎬 Check shorts_output/ for generated video
    echo 🔗 Check YouTube for uploaded video
    echo.
) else (
    echo ============================================================
    echo   ❌ Pipeline failed with error code %PIPELINE_EXIT_CODE%
    echo ============================================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo   - Missing .env file or API keys
    echo   - YouTube authentication not completed
    echo   - Network connection issues
    echo.
)

echo [3/4] Deactivating virtual environment...
deactivate
echo.

echo [4/4] Done!
pause
exit /b %PIPELINE_EXIT_CODE%

