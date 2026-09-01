#!/usr/bin/env pwsh
# BizPilot AI - Local Development Runner
# Usage: .\run.ps1

Write-Host "BizPilot AI - Starting local development server..." -ForegroundColor Cyan

$venvPath = ".venv"

# Create venv if missing
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate venv
& "$venvPath\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest tests/ -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting." -ForegroundColor Red
    exit 1
}

# Start server
Write-Host "Starting server at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API docs at http://127.0.0.1:8000/docs" -ForegroundColor Green
python -m uvicorn app.main:app --reload
