# QA AI Automation Platform - Setup Script with UV
# This script sets up the entire application using UV for fast dependency management

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QA AI Automation Platform - UV Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if UV is installed
Write-Host "[1/6] Checking UV installation..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version
    Write-Host "✓ UV is installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ UV is not installed. Installing..." -ForegroundColor Red
    pip install uv
    Write-Host "✓ UV installed successfully" -ForegroundColor Green
}

Write-Host ""

# Step 2: Setup Backend
Write-Host "[2/6] Setting up backend..." -ForegroundColor Yellow
cd backend

# Create virtual environment with UV
Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
uv venv

# Activate virtual environment
Write-Host "  Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Sync dependencies
Write-Host "  Installing dependencies with UV..." -ForegroundColor Cyan
uv sync

Write-Host "✓ Backend setup complete" -ForegroundColor Green
Write-Host ""

# Step 3: Verify backend dependencies
Write-Host "[3/6] Verifying backend dependencies..." -ForegroundColor Yellow
uv pip list | Select-Object -First 10
Write-Host "✓ Dependencies verified" -ForegroundColor Green
Write-Host ""

# Step 4: Setup Frontend
Write-Host "[4/6] Setting up frontend..." -ForegroundColor Yellow
cd ../frontend

# Install frontend dependencies
Write-Host "  Installing npm dependencies..." -ForegroundColor Cyan
npm install

Write-Host "✓ Frontend setup complete" -ForegroundColor Green
Write-Host ""

# Step 5: Create required directories
Write-Host "[5/6] Creating required directories..." -ForegroundColor Yellow
cd ../backend

if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    Write-Host "  ✓ Created uploads directory" -ForegroundColor Green
}

if (-not (Test-Path "generated_projects")) {
    New-Item -ItemType Directory -Path "generated_projects" | Out-Null
    Write-Host "  ✓ Created generated_projects directory" -ForegroundColor Green
}

if (-not (Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
    Write-Host "  ✓ Created reports directory" -ForegroundColor Green
}

if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "  ✓ Created logs directory" -ForegroundColor Green
}

Write-Host ""

# Step 6: Configuration check
Write-Host "[6/6] Checking configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    if ($envContent -match "GOOGLE_API_KEY=your_google_api_key") {
        Write-Host "  ⚠ GOOGLE_API_KEY not configured" -ForegroundColor Yellow
        Write-Host "  Please update backend/.env with your Gemini API key" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ GOOGLE_API_KEY is configured" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ .env file not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! ✓" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure Gemini API Key:" -ForegroundColor White
Write-Host "   Edit backend/.env and add your API key:" -ForegroundColor Gray
Write-Host "   GOOGLE_API_KEY=your_actual_api_key_here" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Start Backend (in backend directory):" -ForegroundColor White
Write-Host "   uv run python main.py" -ForegroundColor Gray
Write-Host "   Or if venv is activated:" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Start Frontend (in frontend directory):" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Open in Browser:" -ForegroundColor White
Write-Host "   http://localhost:5173" -ForegroundColor Gray
Write-Host ""

Write-Host "5. Upload Sample Documents:" -ForegroundColor White
Write-Host "   From the data/ folder:" -ForegroundColor Gray
Write-Host "   - feature_specification.txt" -ForegroundColor Gray
Write-Host "   - test_cases.txt" -ForegroundColor Gray
Write-Host "   - expected_output.txt" -ForegroundColor Gray
Write-Host ""

Write-Host "6. Generate Automation Code:" -ForegroundColor White
Write-Host "   Click 'Generate' and download results" -ForegroundColor Gray
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - UV Quick Start: UV_QUICK_START.md" -ForegroundColor Gray
Write-Host "  - Quick Start: QUICK_START.md" -ForegroundColor Gray
Write-Host "  - Sample Data: data/README.md" -ForegroundColor Gray
Write-Host "  - Gemini Setup: GEMINI_SETUP.md" -ForegroundColor Gray
Write-Host ""

Write-Host "Happy Testing! 🚀" -ForegroundColor Green
