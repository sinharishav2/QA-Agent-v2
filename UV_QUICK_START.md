# Quick Start with UV Package Manager

Fast Python dependency management with `uv`!

## What is UV?

`uv` is an extremely fast Python package installer and resolver, written in Rust. It's 10-100x faster than pip!

## Prerequisites

✅ Python 3.12+
✅ Node.js 16+
✅ Gemini API Key
✅ `uv` installed (see installation below)

## Install UV

### Option 1: Using pip (Recommended)

```powershell
pip install uv
```

### Option 2: Using Windows Package Manager

```powershell
winget install astral-sh.uv
```

### Option 3: Using Chocolatey

```powershell
choco install uv
```

### Verify Installation

```powershell
uv --version
```

You should see: `uv 0.x.x`

---

## Step 1: Configure Gemini API Key (1 minute)

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Open `backend/.env`
3. Add your key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
4. Save the file

---

## Step 2: Setup Backend with UV (1 minute)

### Option A: Using UV Sync (Recommended)

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Create virtual environment with uv
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Sync dependencies using uv
uv sync
```

### Option B: Using UV Pip Install

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Create virtual environment with uv
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies with uv
uv pip install -e .
```

### Option C: Direct Installation (No venv)

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Install directly with uv
uv pip install --system -e .
```

---

## Step 3: Start Backend with UV (1 minute)

### Option A: Using UV Run (Recommended)

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Run directly with uv (no need to activate venv)
uv run python main.py
```

### Option B: Using Activated Virtual Environment

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Activate venv
.venv\Scripts\activate

# Run application
python main.py
```

### Option C: Using UV Pip with System Python

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Install and run
uv pip install --system -e . && python main.py
```

---

## Step 4: Start Frontend (1 minute)

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

---

## Step 5: Test the Application

1. Open browser: **http://localhost:5173**
2. Upload sample documents from `data/` folder
3. Generate automation code
4. Download results

---

## UV Commands Cheat Sheet

```powershell
# Create virtual environment
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Sync dependencies from pyproject.toml
uv sync

# Install specific package
uv pip install fastapi

# Install from requirements.txt
uv pip install -r requirements.txt

# Install in editable mode
uv pip install -e .

# Install with system Python (no venv)
uv pip install --system package_name

# Run Python with uv (no venv activation needed)
uv run python script.py

# Run command with uv
uv run uvicorn main:app --reload

# List installed packages
uv pip list

# Show package info
uv pip show fastapi

# Uninstall package
uv pip uninstall fastapi

# Update all packages
uv pip install --upgrade -r requirements.txt
```

---

## Performance Comparison

| Task | pip | uv |
|------|-----|-----|
| Install 50 packages | ~45 seconds | ~3 seconds |
| Resolve dependencies | ~30 seconds | ~1 second |
| Update packages | ~40 seconds | ~2 seconds |

**UV is 10-100x faster!** ⚡

---

## Recommended Setup

### For Development

```powershell
# One-time setup
cd backend
uv venv
.venv\Scripts\activate
uv sync

# Every time you want to run
cd backend
.venv\Scripts\activate
python main.py
```

### For Quick Testing

```powershell
# No venv needed
cd backend
uv run python main.py
```

### For CI/CD

```powershell
# Fast, reproducible builds
cd backend
uv sync --frozen
uv run python main.py
```

---

## Troubleshooting

### Issue: "uv command not found"

**Solution:** Install uv first:
```powershell
pip install uv
```

### Issue: "No module named 'fastapi'"

**Solution:** Make sure dependencies are installed:
```powershell
uv sync
```

### Issue: Virtual environment not activating

**Solution:** Use full path:
```powershell
.\.venv\Scripts\activate
```

### Issue: Permission denied on Windows

**Solution:** Run PowerShell as Administrator or use:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## UV with Docker

If using Docker, UV is already integrated in the Dockerfile:

```dockerfile
# Install uv
RUN pip install uv

# Use uv to install dependencies
RUN uv pip install --system -e .

# Run application
CMD ["python", "main.py"]
```

---

## UV with GitHub Actions

```yaml
- name: Install uv
  run: pip install uv

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

---

## Benefits of Using UV

✅ **10-100x faster** than pip
✅ **Deterministic** dependency resolution
✅ **Parallel** package downloads
✅ **Caching** for faster installs
✅ **Lock file** support (uv.lock)
✅ **No venv needed** with `uv run`
✅ **Better error messages**
✅ **Python version management**

---

## Next Steps

1. ✅ Install `uv`
2. ✅ Configure Gemini API key
3. ✅ Setup backend with `uv sync`
4. ✅ Start backend with `uv run python main.py`
5. ✅ Start frontend with `npm run dev`
6. ✅ Upload sample documents
7. ✅ Generate automation code

---

## Full Setup Script

Save this as `setup.ps1` and run it:

```powershell
# Install uv if not already installed
pip install uv

# Setup backend
cd backend
uv venv
.venv\Scripts\activate
uv sync

# Setup frontend
cd ../frontend
npm install

# Done!
echo "Setup complete! Run:"
echo "Backend: cd backend && .venv\Scripts\activate && python main.py"
echo "Frontend: cd frontend && npm run dev"
```

---

## Support

- UV Documentation: https://docs.astral.sh/uv/
- UV GitHub: https://github.com/astral-sh/uv
- Report issues: https://github.com/astral-sh/uv/issues

---

**Happy fast Python development with UV!** ⚡🚀
