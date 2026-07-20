# QA AI Automation Platform - UV Commands
# Usage: .\Makefile.ps1 -Command "command_name"

param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "QA AI Automation Platform - UV Commands" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\Makefile.ps1 -Command 'command_name'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup & Installation:" -ForegroundColor Green
    Write-Host "  setup              - Complete setup with UV" -ForegroundColor White
    Write-Host "  install-uv         - Install UV package manager" -ForegroundColor White
    Write-Host "  install-backend    - Install backend dependencies with UV" -ForegroundColor White
    Write-Host "  install-frontend   - Install frontend dependencies" -ForegroundColor White
    Write-Host ""
    Write-Host "Running Application:" -ForegroundColor Green
    Write-Host "  backend            - Start backend with UV" -ForegroundColor White
    Write-Host "  frontend           - Start frontend" -ForegroundColor White
    Write-Host "  dev                - Start both backend and frontend" -ForegroundColor White
    Write-Host ""
    Write-Host "Development:" -ForegroundColor Green
    Write-Host "  sync               - Sync dependencies with UV" -ForegroundColor White
    Write-Host "  list               - List installed packages" -ForegroundColor White
    Write-Host "  update             - Update all packages" -ForegroundColor White
    Write-Host "  clean              - Clean virtual environment" -ForegroundColor White
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Green
    Write-Host "  test               - Run tests" -ForegroundColor White
    Write-Host "  lint               - Run linting checks" -ForegroundColor White
    Write-Host "  format             - Format code with black" -ForegroundColor White
    Write-Host ""
    Write-Host "Utilities:" -ForegroundColor Green
    Write-Host "  health             - Check application health" -ForegroundColor White
    Write-Host "  logs               - Show backend logs" -ForegroundColor White
    Write-Host "  help               - Show this help message" -ForegroundColor White
    Write-Host ""
}

function Install-UV {
    Write-Host "Installing UV..." -ForegroundColor Yellow
    pip install uv
    Write-Host "✓ UV installed successfully" -ForegroundColor Green
}

function Setup-All {
    Write-Host "Setting up QA AI Automation Platform with UV..." -ForegroundColor Cyan
    
    # Setup backend
    Write-Host ""
    Write-Host "Setting up backend..." -ForegroundColor Yellow
    cd backend
    uv venv
    & .\.venv\Scripts\Activate.ps1
    uv sync
    cd ..
    Write-Host "✓ Backend setup complete" -ForegroundColor Green
    
    # Setup frontend
    Write-Host ""
    Write-Host "Setting up frontend..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
    Write-Host "✓ Frontend setup complete" -ForegroundColor Green
    
    # Create directories
    Write-Host ""
    Write-Host "Creating required directories..." -ForegroundColor Yellow
    cd backend
    @("uploads", "generated_projects", "reports", "logs") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ | Out-Null
            Write-Host "  ✓ Created $_ directory" -ForegroundColor Green
        }
    }
    cd ..
    
    Write-Host ""
    Write-Host "✓ Setup complete!" -ForegroundColor Green
}

function Install-Backend {
    Write-Host "Installing backend dependencies with UV..." -ForegroundColor Yellow
    cd backend
    uv venv
    & .\.venv\Scripts\Activate.ps1
    uv sync
    cd ..
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
}

function Install-Frontend {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
}

function Start-Backend {
    Write-Host "Starting backend with UV..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    Write-Host "Backend running on http://localhost:8000" -ForegroundColor Green
    python main.py
}

function Start-Frontend {
    Write-Host "Starting frontend..." -ForegroundColor Yellow
    cd frontend
    Write-Host "Frontend running on http://localhost:5173" -ForegroundColor Green
    npm run dev
}

function Start-Dev {
    Write-Host "Starting development environment..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Open two PowerShell windows and run:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Window 1 (Backend):" -ForegroundColor Green
    Write-Host "  cd backend" -ForegroundColor Gray
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "  python main.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Window 2 (Frontend):" -ForegroundColor Green
    Write-Host "  cd frontend" -ForegroundColor Gray
    Write-Host "  npm run dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Then open: http://localhost:5173" -ForegroundColor Cyan
}

function Sync-Dependencies {
    Write-Host "Syncing dependencies with UV..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv sync
    cd ..
    Write-Host "✓ Dependencies synced" -ForegroundColor Green
}

function List-Packages {
    Write-Host "Installed packages:" -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv pip list
    cd ..
}

function Update-Packages {
    Write-Host "Updating packages with UV..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv pip install --upgrade -r requirements.txt
    cd ..
    Write-Host "✓ Packages updated" -ForegroundColor Green
}

function Clean-Environment {
    Write-Host "Cleaning virtual environment..." -ForegroundColor Yellow
    cd backend
    if (Test-Path ".venv") {
        Remove-Item -Recurse -Force ".venv"
        Write-Host "✓ Virtual environment removed" -ForegroundColor Green
    }
    cd ..
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv run pytest
    cd ..
}

function Run-Lint {
    Write-Host "Running linting checks..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv run flake8 .
    cd ..
}

function Format-Code {
    Write-Host "Formatting code with black..." -ForegroundColor Yellow
    cd backend
    & .\.venv\Scripts\Activate.ps1
    uv run black .
    cd ..
    Write-Host "✓ Code formatted" -ForegroundColor Green
}

function Check-Health {
    Write-Host "Checking application health..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend is healthy" -ForegroundColor Green
            Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "✗ Backend is not responding" -ForegroundColor Red
        Write-Host "Make sure backend is running on http://localhost:8000" -ForegroundColor Yellow
    }
}

function Show-Logs {
    Write-Host "Backend logs:" -ForegroundColor Yellow
    cd backend
    if (Test-Path "logs") {
        Get-ChildItem logs | ForEach-Object {
            Write-Host ""
            Write-Host "File: $($_.Name)" -ForegroundColor Cyan
            Get-Content $_.FullName -Tail 20
        }
    } else {
        Write-Host "No logs directory found" -ForegroundColor Yellow
    }
    cd ..
}

# Execute command
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-All }
    "install-uv" { Install-UV }
    "install-backend" { Install-Backend }
    "install-frontend" { Install-Frontend }
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "dev" { Start-Dev }
    "sync" { Sync-Dependencies }
    "list" { List-Packages }
    "update" { Update-Packages }
    "clean" { Clean-Environment }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "health" { Check-Health }
    "logs" { Show-Logs }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
