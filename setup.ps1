# Quick setup script for Clinote Backend (Windows PowerShell)

Write-Host "🚀 Setting up Clinote Backend..." -ForegroundColor Green

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Copy environment file
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env with your configuration" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
python -c "from app.database import init_db; init_db()"

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env with your database URL and Gemini API key"
Write-Host "2. Run: .\venv\Scripts\Activate.ps1"
Write-Host "3. Run: uvicorn app.main:app --reload"
Write-Host ""
Write-Host "API will be available at: http://localhost:8000"
Write-Host "API docs at: http://localhost:8000/docs"
