# QA AI Automation Platform

An AI-powered multi-agent Quality Assurance system that automatically generates, validates, executes, and maintains automation test scripts from business requirement documents and manual test cases.

## Overview

The platform minimizes manual intervention by using specialized AI agents, each responsible for a specific stage of the automation lifecycle. It generates a complete automation framework including feature files, page objects, step definitions, test data, and comprehensive reports.

## Key Features

- **Document Ingestion**: Upload functional specifications, test cases, and expected outputs
- **Intelligent Parsing**: Extract requirements and test cases from documents
- **Test Design**: Generate positive, negative, boundary, and regression tests
- **Test Data Generation**: Create valid, invalid, boundary, and security test data
- **Automation Generation**: Generate BDD feature files, page objects, and step definitions
- **Framework Support**: Java Selenium and Python Selenium frameworks
- **Locator Intelligence**: Smart locator selection with priority-based strategies
- **Code Review**: Automated code quality checks
- **Execution**: Run tests with comprehensive reporting
- **Self-Healing**: Automatic repair of broken locators and timeouts
- **Analytics Dashboard**: Track automation coverage and metrics

## Architecture

### Multi-Agent System

The platform uses a coordinated network of specialized agents:

- **Document Ingestion Agent**: Validates and stores uploaded documents
- **Document Parser Agent**: Extracts structured data from documents
- **Requirement Extraction Agent**: Identifies business requirements
- **Test Case Extraction Agent**: Extracts manual test cases
- **Test Design Agent**: Generates comprehensive test scenarios
- **Test Data Agent**: Creates diverse test datasets
- **Automation Framework Agent**: Selects appropriate framework
- **BDD Generator Agent**: Creates feature files
- **Page Object Agent**: Generates reusable page classes
- **Step Definition Agent**: Creates step implementations
- **Locator Intelligence Agent**: Identifies optimal locators
- **Utility Generator Agent**: Creates utility classes
- **Orchestrator Agent**: Coordinates all agents

### Technology Stack

**Backend**
- FastAPI (REST API)
- Python 3.12+
- LangGraph (Agent orchestration)
- LangChain (LLM integration)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Redis (Caching)

**Frontend**
- React 18
- TypeScript
- Tailwind CSS
- Vite
- Axios

**Deployment**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Kubernetes (optional)

## Project Structure

```
qa-ai-platform/
├── backend/
│   ├── agents/              # AI agent implementations
│   ├── orchestrator/        # Orchestration logic
│   ├── parsers/            # Document parsing
│   ├── models/             # Database models & schemas
│   ├── api/                # FastAPI routes
│   ├── config.py           # Configuration
│   └── main.py             # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── App.jsx         # Main app
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml      # Local development setup
├── Dockerfile              # Backend container
├── pyproject.toml          # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 20+ (for frontend development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qa-ai-platform
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

1. **Backend Setup (with uv - Recommended)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install uv for faster dependency installation
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies with uv (much faster)
   uv pip install -e ..
   python main.py
   ```

2. **Backend Setup (with pip - Alternative)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ..
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb qa_ai_platform
   
   # Run migrations (if applicable)
   ```

## API Endpoints

### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{project_id}` - Get project details
- `GET /api/projects/{project_id}/status` - Get project status

### Documents
- `POST /api/projects/{project_id}/upload` - Upload document
- `GET /api/projects/{project_id}/documents` - List documents

### Automation
- `POST /api/projects/{project_id}/generate` - Generate automation
- `GET /api/projects/{project_id}/artifacts` - Download artifacts

### Health
- `GET /api/health` - Health check

## Configuration

### Environment Variables

```env
# FastAPI
FASTAPI_ENV=development
FASTAPI_DEBUG=true
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/qa_ai_platform
REDIS_URL=redis://localhost:6379/0

# LLM
OPENAI_API_KEY=your_key
AZURE_OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key

# Storage
UPLOAD_DIR=./uploads
GENERATED_PROJECTS_DIR=./generated_projects
REPORTS_DIR=./reports
LOGS_DIR=./logs
```

## Workflow

1. **Create Project**: Initialize a new QA automation project
2. **Upload Documents**: Upload functional specs, test cases, and expected outputs
3. **Parse Documents**: System extracts structured data
4. **Extract Requirements**: Identify business requirements
5. **Extract Test Cases**: Parse manual test cases
6. **Design Tests**: Generate comprehensive test scenarios
7. **Generate Test Data**: Create diverse test datasets
8. **Select Framework**: Choose automation framework
9. **Generate Artifacts**: Create feature files, page objects, step definitions
10. **Code Review**: Validate generated code
11. **Build**: Compile and validate framework
12. **Execute**: Run tests
13. **Report**: Generate execution reports
14. **Analyze**: Track metrics and coverage

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ --cov=backend
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Docker Build
```bash
docker build -t qa-ai-platform:latest .
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

### CI/CD Pipeline
The project includes GitHub Actions workflows for:
- Automated testing
- Code quality checks
- Docker image building
- Automated deployment

## Monitoring & Logging

- **Logs**: Centralized logging with Loguru
- **Monitoring**: Prometheus metrics (optional)
- **Dashboards**: Grafana integration (optional)

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Prompt Management Agent
- [ ] Validation Agent
- [ ] RAG Knowledge Base
- [ ] Human approval workflow
- [ ] Configuration Manager
- [ ] Playwright framework support
- [ ] Mobile automation support
- [ ] API testing support
- [ ] Performance testing integration
- [ ] Advanced analytics dashboard
