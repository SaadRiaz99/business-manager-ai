@echo off
REM BizPilot AI - Local Development Runner (Windows)
REM Usage: run.bat

echo BizPilot AI - Starting local development server...

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt --quiet

echo Running tests...
python -m pytest tests/ -v --tb=short
if %ERRORLEVEL% neq 0 (
    echo Tests failed! Aborting.
    exit /b 1
)

echo Starting server at http://127.0.0.1:8000
echo API docs at http://127.0.0.1:8000/docs
python -m uvicorn app.main:app --reload
