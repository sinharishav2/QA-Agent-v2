# Getting Started with QA AI Automation Platform

## Overview

Welcome to the QA AI Automation Platform! This guide will help you get up and running with the system in minutes.

## What is This Project?

The QA AI Automation Platform is an AI-powered multi-agent system that automatically generates, validates, executes, and maintains automation test scripts from business requirement documents and manual test cases.

**Key Capabilities:**
- Intelligent document parsing and requirement extraction
- Automatic test case generation with multiple test types
- Comprehensive test data generation
- BDD feature file generation
- Page object and step definition generation
- Automated code review
- Test execution and reporting
- Self-healing capabilities

## System Requirements

### Minimum Requirements
- Docker & Docker Compose
- 4GB RAM
- 10GB disk space
- Internet connection (for LLM APIs)

### Recommended Requirements
- 8GB+ RAM
- 20GB+ disk space
- SSD storage
- Modern browser (Chrome, Firefox, Safari, Edge)

## Quick Start (5 minutes)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd qa-ai-platform
```

### Step 2: Configure Environment
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys:
```env
OPENAI_API_KEY=your_key_here
AZURE_OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Detailed Setup

### Option 1: Docker Compose (Recommended)

#### Prerequisites
- Docker Desktop installed
- 4GB RAM available

#### Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd qa-ai-platform

# 2. Copy environment file
cp backend/.env.example backend/.env

# 3. Edit environment variables
nano backend/.env  # or use your preferred editor

# 4. Start all services
docker-compose up -d

# 5. Verify services are running
docker-compose ps

# 6. Check logs
docker-compose logs -f backend

# 7. Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

#### Stopping Services
```bash
docker-compose down
```

#### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Option 2: Local Development

#### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

#### Backend Setup (with uv - Recommended)
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv (faster)
uv pip install -e ..

# Create database
createdb qa_ai_platform

# Run server
python main.py
```

The backend will start on http://localhost:8000

#### Backend Setup (with pip - Alternative)
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies with pip
pip install -e ..

# Create database
createdb qa_ai_platform

# Run server
python main.py
```

#### Frontend Setup
```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on http://localhost:3000

## First Steps

### 1. Create a Project
1. Open http://localhost:3000
2. Click "New Project"
3. Enter project name and description
4. Click "Create"

### 2. Upload Documents
1. Navigate to your project
2. Upload three documents:
   - **Functional Specification** (DOCX)
   - **Test Cases** (DOCX or XLSX)
   - **Expected Output** (XLSX)

### 3. Generate Automation
1. Click "Generate Automation"
2. Wait for the process to complete
3. View generated artifacts

### 4. Review Results
1. Check generated feature files
2. Review page objects
3. Examine step definitions
4. View test data

## API Usage Examples

### Create a Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My QA Project",
    "description": "Test automation project"
  }'
```

### Upload a Document
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/upload \
  -F "file=@path/to/document.docx" \
  -F "document_type=functional_specification"
```

### Generate Automation
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/generate \
  -H "Content-Type: application/json"
```

### Get Project Status
```bash
curl http://localhost:8000/api/projects/{project_id}/status
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Project Structure Overview

```
qa-ai-platform/
├── backend/                 # FastAPI backend
│   ├── agents/             # 17 AI agents
│   ├── orchestrator/       # Workflow orchestration
│   ├── models/             # Database models
│   ├── api/                # API endpoints
│   └── main.py             # Application entry
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yml      # Docker setup
├── Dockerfile              # Backend container
├── pyproject.toml          # Python dependencies
├── README.md               # Main documentation
├── ARCHITECTURE.md         # System design
├── DEPLOYMENT.md           # Deployment guide
└── PROJECT_SUMMARY.md      # Project overview
```

## Configuration

### Environment Variables

**Database**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/qa_ai_platform
REDIS_URL=redis://localhost:6379/0
```

**LLM APIs**
```env
OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_API_KEY=your_azure_key
GOOGLE_API_KEY=your_google_key
```

**Application**
```env
FASTAPI_ENV=development
FASTAPI_DEBUG=true
LOG_LEVEL=INFO
```

**Storage**
```env
UPLOAD_DIR=./uploads
GENERATED_PROJECTS_DIR=./generated_projects
REPORTS_DIR=./reports
LOGS_DIR=./logs
```

## Common Tasks

### Viewing Logs
```bash
# Docker Compose
docker-compose logs -f backend

# Local development
# Logs appear in terminal where you ran `python main.py`
```

### Accessing Database
```bash
# Docker Compose
docker-compose exec postgres psql -U qa_user -d qa_ai_platform

# Local
psql qa_ai_platform
```

### Resetting Database
```bash
# Docker Compose
docker-compose down -v
docker-compose up -d

# Local
dropdb qa_ai_platform
createdb qa_ai_platform
```

### Clearing Cache
```bash
# Docker Compose
docker-compose exec redis redis-cli FLUSHDB

# Local
redis-cli FLUSHDB
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # Database
lsof -i :6379  # Redis

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql postgresql://qa_user:qa_password@localhost:5432/qa_ai_platform

# View logs
docker-compose logs postgres
```

### Redis Connection Error
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping

# View logs
docker-compose logs redis
```

### Frontend Not Loading
```bash
# Check if frontend is running
curl http://localhost:3000

# View logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### API Not Responding
```bash
# Check health
curl http://localhost:8000/api/health

# View logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Setup and features
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Explore the System**
   - Create a test project
   - Upload sample documents
   - Generate automation
   - Review generated artifacts

3. **Configure LLM**
   - Add OpenAI API key
   - Test LLM integration
   - Customize prompts

4. **Customize for Your Needs**
   - Modify agent prompts
   - Adjust test generation rules
   - Configure framework preferences

5. **Deploy to Production**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
   - Set up Kubernetes
   - Configure CI/CD pipeline

## Support

### Getting Help
1. Check [README.md](README.md) for common questions
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check logs for error messages
4. Open an issue on GitHub

### Reporting Issues
When reporting issues, include:
- Error message
- Steps to reproduce
- Logs from `docker-compose logs`
- Environment details

## Key Features

### Document Processing
- Intelligent DOCX/XLSX parsing
- Requirement extraction
- Test case extraction
- Automatic feature identification

### Test Generation
- Positive test cases
- Negative test cases
- Boundary value tests
- Smoke/sanity/regression tests

### Test Data
- Valid data generation
- Invalid data generation
- Boundary data
- Security test payloads

### Code Generation
- BDD feature files
- Page objects
- Step definitions
- Utility classes

### Quality Assurance
- Automated code review
- SOLID principles validation
- Code smell detection
- Duplicate detection

### Execution & Reporting
- Test execution
- HTML reports
- JSON reports
- Metrics tracking

### Self-Healing
- Broken locator detection
- Automatic locator updates
- Timeout adjustment
- Retry logic

## Performance Tips

1. **Database**
   - Use SSD for better performance
   - Regularly vacuum PostgreSQL
   - Monitor connection pool

2. **Caching**
   - Redis caches frequently accessed data
   - Clear cache if needed: `redis-cli FLUSHDB`

3. **Parallel Execution**
   - Configure parallel test execution
   - Adjust based on system resources

4. **Logging**
   - Set appropriate log level
   - Archive old logs regularly

## Security Considerations

1. **API Keys**
   - Store in `.env` file (not in code)
   - Rotate keys regularly
   - Use different keys per environment

2. **Database**
   - Use strong passwords
   - Enable SSL in production
   - Regular backups

3. **Frontend**
   - Use HTTPS in production
   - Enable CORS properly
   - Validate all inputs

## Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/
- **Kubernetes**: https://kubernetes.io/docs/

## Feedback & Contributions

We welcome feedback and contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

---

**Ready to get started?** Follow the Quick Start section above and you'll be up and running in minutes!

For detailed information, see:
- [README.md](README.md) - Full documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
