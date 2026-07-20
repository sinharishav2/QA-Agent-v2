# Quick Start Guide - QA AI Automation Platform

Get up and running in 5 minutes!

## Prerequisites

✅ Python 3.12+
✅ Node.js 16+
✅ Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Step 1: Configure Gemini API Key (2 minutes)

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Open `backend/.env`
3. Replace this line:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```
   With your actual key:
   ```
   GOOGLE_API_KEY=sk-abc123xyz789...
   ```
4. Save the file

## Step 2: Start Backend (1 minute)

Open PowerShell and run:

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\backend

# Activate virtual environment
venv\Scripts\Activate.ps1

# Start backend
python main.py
```

You should see:
```
INFO     | __main__:<module>:75 - QA AI Automation Platform starting up...
INFO     | __main__:<module>:76 - Environment: development
```

✅ Backend is running on: **http://localhost:8000**

## Step 3: Start Frontend (1 minute)

Open a new PowerShell and run:

```powershell
cd c:\Users\Rishav\Desktop\QA-Agent-V2\frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

✅ Frontend is running on: **http://localhost:5173**

## Step 4: Test the Application (1 minute)

1. Open browser: **http://localhost:5173**
2. You'll see the chat interface with:
   - Left sidebar: Conversation history
   - Middle: Chat area
   - Right panel: Project options

## Step 5: Upload Sample Documents

1. Click "New Conversation" in left sidebar
2. Enter project name: "E-Commerce Testing"
3. Click "Create"
4. Upload these 3 files from `data/` folder:
   - `feature_specification.txt` → Select "functional_specification"
   - `test_cases.txt` → Select "test_cases"
   - `expected_output.txt` → Select "expected_output"

## Step 6: Generate Automation Code

1. Click "Generate" button
2. Wait for Gemini to process (30-60 seconds)
3. You'll see generated code summary
4. Download from right panel

## What Gets Generated

✅ **Test Scripts** - Python/Selenium automation code
✅ **Page Objects** - Reusable page object models
✅ **Feature Files** - BDD Gherkin scenarios
✅ **Step Definitions** - Test step implementations
✅ **Test Data** - Test data generators
✅ **Configuration** - Setup and config files

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check if port 8000 is free: `netstat -ano \| findstr :8000` |
| Frontend won't load | Check if port 5173 is free, run `npm install` again |
| Gemini API error | Verify API key in `.env`, check quota at [Google AI Studio](https://makersuite.google.com/app/apikey) |
| Can't upload files | Ensure `backend/uploads/` directory exists |
| Generated code is empty | Check backend logs: `backend/logs/` |

## File Locations

```
QA-Agent-V2/
├── backend/
│   ├── main.py (Start here)
│   ├── .env (Add Gemini API key here)
│   ├── api/
│   ├── agents/
│   ├── models/
│   └── utils/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── data/
    ├── feature_specification.txt (Sample input)
    ├── test_cases.txt (Sample input)
    ├── expected_output.txt (Sample input)
    └── README.md (Sample data guide)
```

## API Endpoints

```bash
# Create project
POST http://localhost:8000/api/projects?project_name=MyProject

# Upload document
POST http://localhost:8000/api/projects/{project_id}/upload
  -F "file=@feature_spec.txt"
  -F "document_type=functional_specification"

# Generate automation
POST http://localhost:8000/api/projects/{project_id}/generate

# Get project status
GET http://localhost:8000/api/projects/{project_id}/status

# Health check
GET http://localhost:8000/api/health
```

## Next Steps

1. ✅ Configure Gemini API key
2. ✅ Start backend and frontend
3. ✅ Upload sample documents
4. ✅ Generate automation code
5. ✅ Download and review generated code
6. ✅ Customize for your application
7. ✅ Run tests against your app
8. ✅ Integrate with CI/CD

## Performance Tips

- First generation takes 30-60 seconds (Gemini processing)
- Subsequent generations are faster
- Keep documents under 5MB
- Use clear, structured document formats

## Support

- Check logs: `backend/logs/`
- Review sample data: `data/README.md`
- Check Gemini setup: `GEMINI_SETUP.md`
- Full documentation: `README.md`

---

**You're all set! Start with Step 1 above.** 🚀

Questions? Check the documentation files in the project root.
