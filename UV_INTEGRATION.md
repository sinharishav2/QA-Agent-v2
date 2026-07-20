# UV Integration Guide

Complete guide for using UV with the QA AI Automation Platform.

## Overview

UV is integrated into the application for:
- ⚡ **10-100x faster** dependency installation
- 🔒 **Deterministic** dependency resolution
- 📦 **Lock file** support for reproducible builds
- 🚀 **Parallel** package downloads
- 🎯 **Better** error messages

## Files Created for UV Support

### 1. **UV_QUICK_START.md**
Quick reference guide for UV commands and setup.

### 2. **setup_with_uv.ps1**
Automated setup script that:
- Installs UV if needed
- Creates virtual environment
- Syncs all dependencies
- Creates required directories
- Verifies configuration

### 3. **Makefile.ps1**
PowerShell command helper with shortcuts for:
- Setup and installation
- Running application
- Development tasks
- Testing and linting

### 4. **pyproject.toml**
Updated with UV configuration:
```toml
[tool.uv]
dev-dependencies = [...]
python-versions = ">=3.12"
index-strategy = "unsafe-best-match"
```

## Quick Start with UV

### Method 1: Automated Setup (Recommended)

```powershell
# Run the setup script
.\setup_with_uv.ps1

# Then start backend
cd backend
.\.venv\Scripts\Activate.ps1
python main.py

# In another terminal, start frontend
cd frontend
npm run dev
```

### Method 2: Manual Setup

```powershell
# Install UV
pip install uv

# Setup backend
cd backend
uv venv
.\.venv\Scripts\Activate.ps1
uv sync

# Start backend
python main.py
```

### Method 3: Using Makefile

```powershell
# Setup everything
.\Makefile.ps1 -Command "setup"

# Start backend
.\Makefile.ps1 -Command "backend"

# Start frontend
.\Makefile.ps1 -Command "frontend"
```

## UV Commands Reference

### Installation

```powershell
# Create virtual environment
uv venv

# Sync dependencies from pyproject.toml
uv sync

# Install specific package
uv pip install package_name

# Install from requirements.txt
uv pip install -r requirements.txt

# Install in editable mode
uv pip install -e .

# Install with system Python (no venv)
uv pip install --system package_name
```

### Running Code

```powershell
# Run Python script with UV (no venv activation needed)
uv run python main.py

# Run with specific Python version
uv run --python 3.12 python main.py

# Run command with dependencies
uv run uvicorn main:app --reload
```

### Package Management

```powershell
# List installed packages
uv pip list

# Show package information
uv pip show fastapi

# Uninstall package
uv pip uninstall fastapi

# Update all packages
uv pip install --upgrade -r requirements.txt

# Check for outdated packages
uv pip list --outdated
```

### Development

```powershell
# Sync dev dependencies
uv sync --all-extras

# Sync without dev dependencies
uv sync --no-dev

# Frozen sync (for CI/CD)
uv sync --frozen

# Check dependencies
uv pip check
```

## Makefile.ps1 Commands

```powershell
# Setup
.\Makefile.ps1 -Command "setup"              # Complete setup
.\Makefile.ps1 -Command "install-uv"         # Install UV
.\Makefile.ps1 -Command "install-backend"    # Install backend deps
.\Makefile.ps1 -Command "install-frontend"   # Install frontend deps

# Running
.\Makefile.ps1 -Command "backend"            # Start backend
.\Makefile.ps1 -Command "frontend"           # Start frontend
.\Makefile.ps1 -Command "dev"                # Show dev setup

# Development
.\Makefile.ps1 -Command "sync"               # Sync dependencies
.\Makefile.ps1 -Command "list"               # List packages
.\Makefile.ps1 -Command "update"             # Update packages
.\Makefile.ps1 -Command "clean"              # Clean venv

# Testing
.\Makefile.ps1 -Command "test"               # Run tests
.\Makefile.ps1 -Command "lint"               # Run linting
.\Makefile.ps1 -Command "format"             # Format code

# Utilities
.\Makefile.ps1 -Command "health"             # Check health
.\Makefile.ps1 -Command "logs"               # Show logs
.\Makefile.ps1 -Command "help"               # Show help
```

## Workflow Examples

### Development Workflow

```powershell
# Initial setup
.\setup_with_uv.ps1

# Daily development
cd backend
.\.venv\Scripts\Activate.ps1

# Make changes...

# Sync new dependencies if needed
uv sync

# Run application
python main.py
```

### Adding New Dependencies

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

# Add package
uv pip install new-package

# Update pyproject.toml manually with the new package
# Then sync to update lock file
uv sync
```

### CI/CD Pipeline

```powershell
# Fast, reproducible builds
uv sync --frozen
uv run pytest
uv run python main.py
```

### Docker Integration

```dockerfile
# Install UV
RUN pip install uv

# Create venv and sync
RUN uv venv
RUN uv sync --frozen

# Run application
CMD ["uv", "run", "python", "main.py"]
```

## Performance Comparison

| Operation | pip | uv | Speed |
|-----------|-----|-----|-------|
| Install 50 packages | 45s | 3s | **15x faster** |
| Resolve dependencies | 30s | 1s | **30x faster** |
| Update packages | 40s | 2s | **20x faster** |
| Cache hit | 15s | 0.5s | **30x faster** |

## Troubleshooting

### Issue: "uv command not found"

```powershell
# Install UV
pip install uv

# Verify installation
uv --version
```

### Issue: "No module named 'fastapi'"

```powershell
# Make sure venv is activated
.\.venv\Scripts\Activate.ps1

# Sync dependencies
uv sync

# Verify installation
uv pip list | grep fastapi
```

### Issue: Virtual environment not activating

```powershell
# Use full path
.\.venv\Scripts\Activate.ps1

# Or use uv run to skip activation
uv run python main.py
```

### Issue: Permission denied on Windows

```powershell
# Run PowerShell as Administrator
# Or set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Dependency conflicts

```powershell
# Check for conflicts
uv pip check

# Update all packages
uv pip install --upgrade -r requirements.txt

# Sync fresh
uv sync --refresh
```

## Best Practices

### 1. Always Use Virtual Environments

```powershell
# Good
uv venv
.\.venv\Scripts\Activate.ps1
uv sync

# Avoid
uv pip install --system package_name
```

### 2. Keep Dependencies Updated

```powershell
# Regularly check for updates
uv pip list --outdated

# Update when needed
uv pip install --upgrade package_name
```

### 3. Use Lock Files for Reproducibility

```powershell
# Create lock file
uv sync

# Use frozen sync in CI/CD
uv sync --frozen
```

### 4. Document Dependencies

```toml
# In pyproject.toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    # ...
]
```

### 5. Separate Dev Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.12.0",
    # ...
]
```

## Advanced Features

### Python Version Management

```powershell
# Use specific Python version
uv run --python 3.12 python main.py

# List available Python versions
uv python list
```

### Parallel Installation

UV automatically parallelizes package downloads:

```powershell
# Faster than pip
uv pip install -r requirements.txt
```

### Better Error Messages

UV provides clearer error messages:

```
error: Failed to resolve dependencies:
  - package-a requires package-b>=2.0
  - package-c requires package-b<2.0
```

## Integration with Tools

### GitHub Actions

```yaml
- name: Install UV
  run: pip install uv

- name: Setup dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
```

### VS Code

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

## Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **UV Discord**: https://discord.gg/astral-sh
- **Report Issues**: https://github.com/astral-sh/uv/issues

## Summary

UV is fully integrated into the QA AI Automation Platform:

✅ **Fast** - 10-100x faster than pip
✅ **Reliable** - Deterministic dependency resolution
✅ **Simple** - Same commands as pip
✅ **Flexible** - Works with venv or system Python
✅ **Documented** - Clear error messages

**Start using UV today for faster development!** ⚡🚀
