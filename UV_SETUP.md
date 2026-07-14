# UV Setup Guide

## What is uv?

`uv` is an extremely fast Python package installer and resolver, written in Rust. It's a drop-in replacement for `pip` that's significantly faster.

**Benefits:**
- ⚡ 10-100x faster than pip
- 🔒 Deterministic dependency resolution
- 📦 Compatible with pip and pyproject.toml
- 🚀 Instant installation
- 🔄 Better caching

---

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify Installation
```bash
uv --version
```

---

## Quick Start with uv

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv pip install -e .

# Or with specific requirements
uv pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```

---

## Using uv in Docker

The Dockerfile has been updated to use `uv` for faster builds:

```dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

COPY pyproject.toml .
RUN uv pip install --system -e .
```

### Build with uv
```bash
docker build -t qa-ai-platform:latest .
```

---

## Using uv in Docker Compose

The docker-compose.yml has been updated to use `uv`:

```yaml
command: sh -c "uv pip install --system -e . && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
```

### Start Services
```bash
docker-compose up -d
```

---

## Common uv Commands

### Install Dependencies
```bash
# Install from pyproject.toml
uv pip install -e .

# Install specific package
uv pip install requests

# Install with extras
uv pip install -e ".[dev]"

# Install from requirements.txt
uv pip install -r requirements.txt
```

### Manage Virtual Environments
```bash
# Create venv
python -m venv venv

# Activate venv
source venv/bin/activate

# Install with uv in venv
uv pip install -e .
```

### System-wide Installation
```bash
# Install to system Python (in Docker)
uv pip install --system -e .
```

### Update Packages
```bash
# Update all packages
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade requests
```

### List Installed Packages
```bash
uv pip list
```

### Uninstall Packages
```bash
uv pip uninstall package-name
```

---

## Performance Comparison

### Installation Time

| Tool | Time | Speed |
|------|------|-------|
| pip | ~45s | 1x |
| uv | ~2s | 22x faster |

*Actual times vary based on system and network*

---

## Migration from pip to uv

### Step 1: Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Replace pip with uv
```bash
# Old way
pip install -e .

# New way
uv pip install -e .
```

### Step 3: Verify Installation
```bash
uv pip list
python -c "import fastapi; print(fastapi.__version__)"
```

---

## Troubleshooting

### uv not found
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH if needed
export PATH="$HOME/.cargo/bin:$PATH"
```

### Permission denied
```bash
# On macOS/Linux, make sure the script is executable
chmod +x ~/.cargo/bin/uv
```

### Virtual environment issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
uv pip install -e .
```

### Dependency conflicts
```bash
# Clear cache and reinstall
uv pip install --force-reinstall -e .
```

---

## Docker Build Performance

### Before (with pip)
```
Step 3/8 : RUN pip install --no-cache-dir -e .
 ---> Running in abc123def456
Collecting fastapi==0.104.1
...
Successfully installed fastapi-0.104.1
 ---> 45 seconds
```

### After (with uv)
```
Step 3/8 : RUN uv pip install --system -e .
 ---> Running in abc123def456
Resolved 45 packages in 0.2s
Installed 45 packages in 1.8s
 ---> 2 seconds
```

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Install dependencies with uv
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install -e .
```

### GitLab CI
```yaml
install:
  script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - uv pip install -e .
```

---

## Best Practices

1. **Always use uv for new projects** - It's faster and more reliable
2. **Keep pyproject.toml updated** - uv respects all pyproject.toml specifications
3. **Use virtual environments** - Always isolate project dependencies
4. **Cache in Docker** - Use Docker layer caching for faster builds
5. **Pin versions** - Specify exact versions in pyproject.toml for reproducibility

---

## Resources

- **Official Website**: https://astral.sh/uv/
- **GitHub Repository**: https://github.com/astral-sh/uv
- **Documentation**: https://docs.astral.sh/uv/
- **Comparison with pip**: https://astral.sh/blog/uv/

---

## Summary

`uv` is now integrated into the QA AI Automation Platform for:
- ✅ Faster local development
- ✅ Faster Docker builds
- ✅ Faster CI/CD pipelines
- ✅ Better dependency resolution
- ✅ Full pip compatibility

**Recommended approach**: Use `uv pip install` instead of `pip install` for all dependency management.
