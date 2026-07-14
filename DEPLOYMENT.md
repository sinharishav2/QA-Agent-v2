# Deployment Guide

## Local Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (optional if using Docker)
- Redis 7+ (optional if using Docker)

### Quick Start

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd qa-ai-platform
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Local Development

1. **Backend Setup (with uv - Recommended)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install uv for faster dependency installation
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies with uv (much faster than pip)
   uv pip install -e ..
   
   # Create database
   createdb qa_ai_platform
   
   # Start server
   python main.py
   ```

2. **Backend Setup (with pip - Alternative)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ..
   
   # Create database
   createdb qa_ai_platform
   
   # Start server
   python main.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Production Deployment

### Docker Image Build

```bash
docker build -t qa-ai-platform:1.0.0 .
docker tag qa-ai-platform:1.0.0 your-registry/qa-ai-platform:1.0.0
docker push your-registry/qa-ai-platform:1.0.0
```

### Kubernetes Deployment

1. **Create Namespace**
   ```bash
   kubectl create namespace qa-ai
   ```

2. **Create Secrets**
   ```bash
   kubectl create secret generic qa-ai-secrets \
     --from-literal=database-url=postgresql://... \
     --from-literal=redis-url=redis://... \
     --from-literal=openai-api-key=... \
     -n qa-ai
   ```

3. **Deploy Services**
   ```bash
   kubectl apply -f k8s/postgres-statefulset.yaml -n qa-ai
   kubectl apply -f k8s/redis-deployment.yaml -n qa-ai
   kubectl apply -f k8s/backend-deployment.yaml -n qa-ai
   kubectl apply -f k8s/frontend-deployment.yaml -n qa-ai
   kubectl apply -f k8s/ingress.yaml -n qa-ai
   ```

4. **Verify Deployment**
   ```bash
   kubectl get pods -n qa-ai
   kubectl get svc -n qa-ai
   ```

### Environment Configuration

#### Production Environment Variables

```env
# FastAPI
FASTAPI_ENV=production
FASTAPI_DEBUG=false
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@postgres-service:5432/qa_ai_platform
REDIS_URL=redis://redis-service:6379/0

# LLM
OPENAI_API_KEY=your_production_key
AZURE_OPENAI_API_KEY=your_azure_key
GOOGLE_API_KEY=your_google_key

# Storage
UPLOAD_DIR=/data/uploads
GENERATED_PROJECTS_DIR=/data/generated_projects
REPORTS_DIR=/data/reports
LOGS_DIR=/data/logs

# Security
SECRET_KEY=your_secure_random_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes automated CI/CD with:

1. **Testing Stage**
   - Backend unit tests
   - Frontend build verification
   - Code quality checks

2. **Build Stage**
   - Docker image creation
   - Image registry push

3. **Deploy Stage**
   - Kubernetes deployment
   - Health checks
   - Smoke tests

### Manual Deployment Steps

1. **Push to Main Branch**
   ```bash
   git push origin main
   ```

2. **GitHub Actions Triggers**
   - Runs tests
   - Builds Docker image
   - Pushes to registry
   - Deploys to production

## Database Migration

### PostgreSQL Setup

1. **Create Database**
   ```bash
   createdb qa_ai_platform
   ```

2. **Initialize Schema**
   ```bash
   python backend/models/database.py
   ```

3. **Verify Tables**
   ```bash
   psql qa_ai_platform -c "\dt"
   ```

## Backup & Recovery

### Database Backup

```bash
# Full backup
pg_dump qa_ai_platform > backup.sql

# Compressed backup
pg_dump qa_ai_platform | gzip > backup.sql.gz

# Restore
psql qa_ai_platform < backup.sql
```

### File Storage Backup

```bash
# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Backup generated projects
tar -czf projects-backup.tar.gz generated_projects/

# Backup reports
tar -czf reports-backup.tar.gz reports/
```

## Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

### Kubernetes Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Kubernetes Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend replicas
kubectl scale deployment backend --replicas=3 -n qa-ai

# Scale frontend replicas
kubectl scale deployment frontend --replicas=2 -n qa-ai
```

### Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: qa-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check database service
   kubectl get svc postgres-service -n qa-ai
   
   # Check logs
   kubectl logs -l app=backend -n qa-ai
   ```

2. **Redis Connection Error**
   ```bash
   # Check Redis service
   kubectl get svc redis-service -n qa-ai
   
   # Test connection
   redis-cli -h redis-service ping
   ```

3. **API Not Responding**
   ```bash
   # Check pod status
   kubectl get pods -n qa-ai
   
   # Check logs
   kubectl logs <pod-name> -n qa-ai
   
   # Describe pod
   kubectl describe pod <pod-name> -n qa-ai
   ```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_project_id ON projects(project_id);
CREATE INDEX idx_document_project ON uploaded_documents(project_id);
CREATE INDEX idx_requirement_project ON parsed_requirements(project_id);
CREATE INDEX idx_testcase_project ON manual_test_cases(project_id);

-- Analyze tables
ANALYZE;
```

### Redis Optimization

```bash
# Monitor Redis
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# Clear cache if needed
redis-cli FLUSHDB
```

## Security Hardening

1. **Network Policies**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: backend-policy
     namespace: qa-ai
   spec:
     podSelector:
       matchLabels:
         app: backend
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: frontend
   ```

2. **RBAC Configuration**
   ```bash
   kubectl create serviceaccount qa-ai-sa -n qa-ai
   kubectl create role qa-ai-role --verb=get,list,watch --resource=pods -n qa-ai
   kubectl create rolebinding qa-ai-binding --role=qa-ai-role --serviceaccount=qa-ai:qa-ai-sa -n qa-ai
   ```

3. **Secrets Management**
   - Use Kubernetes Secrets for sensitive data
   - Rotate secrets regularly
   - Use external secret managers (Vault, AWS Secrets Manager)

## Rollback Procedure

```bash
# Check rollout history
kubectl rollout history deployment/backend -n qa-ai

# Rollback to previous version
kubectl rollout undo deployment/backend -n qa-ai

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n qa-ai
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Monitor logs
   - Check health endpoints
   - Verify backups

2. **Weekly**
   - Review performance metrics
   - Check disk usage
   - Update dependencies

3. **Monthly**
   - Database optimization
   - Security patches
   - Capacity planning

## Support & Troubleshooting

For issues:
1. Check logs: `kubectl logs <pod-name> -n qa-ai`
2. Check events: `kubectl describe pod <pod-name> -n qa-ai`
3. Check metrics: `kubectl top pods -n qa-ai`
4. Review documentation
5. Open GitHub issue
