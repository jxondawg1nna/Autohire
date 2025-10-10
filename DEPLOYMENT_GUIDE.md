# 🚀 Enhanced Autohire Deployment Guide

## Complete AI-First Recruitment Platform

This guide covers the deployment of the enhanced Autohire platform with real browser automation, vector search, self-hosted LLM integration, and comprehensive monitoring.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Development Deployment](#development-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Observability](#monitoring--observability)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Troubleshooting](#troubleshooting)

## 🏗️ System Overview

The enhanced Autohire platform includes:

- **Real Browser Automation**: Playwright-powered job site scraping (LinkedIn, Indeed, Seek, Google Jobs)
- **Vector Search**: Meilisearch and Qdrant for semantic job matching
- **Self-Hosted LLM**: Local AI processing for privacy and control
- **Resume Parsing**: Advanced NLP with spaCy and PyPDF2
- **Comprehensive Monitoring**: Prometheus, Grafana, ELK stack
- **Container Orchestration**: Docker and Docker Compose
- **CI/CD Pipeline**: GitHub Actions with security scanning

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3003    │    │   Port: 8002    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │   Redis   │ │  Qdrant   │ │Meilisearch│
            │Port: 6379 │ │Port: 6333 │ │Port: 7700 │
            └───────────┘ └───────────┘ └───────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │Prometheus │ │  Grafana  │ │    ELK    │
            │Port: 9090 │ │Port: 3001 │ │   Stack   │
            └───────────┘ └───────────┘ └───────────┘
```

## 🔧 Prerequisites

### Required Software

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend development
- **Docker & Docker Compose** - Container orchestration
- **Git** - Version control

### Optional (for advanced features)

- **NVIDIA GPU** - For local LLM acceleration
- **8GB+ RAM** - For full ML model loading
- **SSD Storage** - For vector database performance

### Installation Commands

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Playwright browsers
playwright install --with-deps chromium

# Install frontend dependencies
cd frontend && npm install

# Install Docker (platform-specific)
# Windows: Download Docker Desktop
# macOS: brew install docker docker-compose
# Linux: curl -fsSL https://get.docker.com | sh
```

## ⚡ Quick Start

### 1. Validation Check

Run the deployment validation script:

```bash
python deploy_and_validate.py
```

This will check all prerequisites and validate the configuration.

### 2. Development Mode

Start individual services for development:

```bash
# Backend (Terminal 1)
cd backend
python enhanced_autohire_backend.py

# Frontend (Terminal 2)
cd frontend
npm run dev

# Optional: Start monitoring stack
docker-compose -f docker-compose.enhanced.yml up prometheus grafana
```

### 3. Full Production Mode

Deploy all services with Docker Compose:

```bash
# Build and start all services
docker-compose -f docker-compose.enhanced.yml up -d

# Check service status
docker-compose -f docker-compose.enhanced.yml ps

# View logs
docker-compose -f docker-compose.enhanced.yml logs -f autohire-backend
```

## 🛠️ Development Deployment

### Backend Development

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   playwright install chromium
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Backend**
   ```bash
   python enhanced_autohire_backend.py
   ```

4. **API Documentation**
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc

### Frontend Development

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   ```bash
   # Create .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8002
   ```

3. **Start Frontend**
   ```bash
   npm run dev
   # Access at http://localhost:3000
   ```

### Database Setup

1. **PostgreSQL (Development)**
   ```bash
   # Using Docker
   docker run -d \
     --name autohire-postgres \
     -e POSTGRES_DB=autohire \
     -e POSTGRES_USER=autohire_user \
     -e POSTGRES_PASSWORD=autohire_password \
     -p 5432:5432 \
     postgres:15
   ```

2. **Run Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

## 🚀 Production Deployment

### Using Docker Compose (Recommended)

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd autohire
   ```

2. **Environment Configuration**
   ```bash
   cp .env.production .env
   # Edit production settings
   ```

3. **Deploy Stack**
   ```bash
   # Pull latest images
   docker-compose -f docker-compose.enhanced.yml pull

   # Start all services
   docker-compose -f docker-compose.enhanced.yml up -d

   # Wait for services to be ready
   sleep 30

   # Check health
   curl http://localhost:8002/health
   ```

4. **Service Endpoints**
   - **Application**: http://localhost:3003
   - **API**: http://localhost:8002
   - **Grafana**: http://localhost:3001 (admin/admin)
   - **Prometheus**: http://localhost:9090
   - **Kibana**: http://localhost:5601

### Manual Production Setup

1. **Application Server**
   ```bash
   # Install production dependencies
   pip install -r backend/requirements.txt

   # Use production WSGI server
   gunicorn -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8002 \
     --workers 4 \
     enhanced_autohire_backend:app
   ```

2. **Database Configuration**
   ```bash
   # Production PostgreSQL
   createdb autohire_production
   psql autohire_production < backend/sql/init.sql
   ```

3. **Reverse Proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:3003;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api/ {
           proxy_pass http://localhost:8002;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📊 Monitoring & Observability

### Prometheus Metrics

The backend exposes comprehensive metrics:

- **Application Metrics**: Request count, duration, errors
- **Business Metrics**: Jobs scraped, applications submitted
- **System Metrics**: Memory usage, CPU utilization
- **Custom Metrics**: Browser automation success rate

Access: http://localhost:9090

### Grafana Dashboards

Pre-configured dashboards include:

1. **Application Overview**: Request metrics, error rates
2. **Job Scraping Performance**: Site-specific success rates
3. **System Resources**: CPU, memory, disk usage
4. **User Activity**: Authentication, job searches

Access: http://localhost:3001 (admin/admin)

### ELK Stack Logging

- **Elasticsearch**: Log storage and indexing
- **Logstash**: Log processing and filtering
- **Kibana**: Log visualization and analysis

Access: http://localhost:5601

### Health Checks

```bash
# Application health
curl http://localhost:8002/health

# Database health
curl http://localhost:8002/health/database

# External services
curl http://localhost:8002/health/dependencies
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Testing**: Backend and frontend test suites
2. **Security Scanning**: Vulnerability detection
3. **Building**: Docker image creation
4. **Deployment**: Automated staging/production deployment

### Pipeline Configuration

1. **Repository Secrets**
   ```bash
   # Required secrets in GitHub repository
   STAGING_HOST=your-staging-server.com
   STAGING_USER=deploy
   STAGING_SSH_KEY=<private-key>
   PRODUCTION_HOST=your-production-server.com
   PRODUCTION_USER=deploy
   PRODUCTION_SSH_KEY=<private-key>
   SLACK_WEBHOOK=<webhook-url>
   ```

2. **Trigger Deployment**
   ```bash
   # Staging deployment (develop branch)
   git push origin develop

   # Production deployment (main branch)
   git push origin main
   ```

### Manual Deployment

```bash
# Build and push images
docker build -t autohire-backend:latest backend/
docker build -t autohire-frontend:latest frontend/

# Deploy to server
docker-compose -f docker-compose.enhanced.yml up -d
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check which ports are in use
   netstat -tulpn | grep :8002

   # Kill conflicting processes
   sudo kill -9 <PID>
   ```

2. **Docker Issues**
   ```bash
   # Reset Docker state
   docker-compose -f docker-compose.enhanced.yml down
   docker system prune -f
   docker-compose -f docker-compose.enhanced.yml up -d
   ```

3. **Database Connection Issues**
   ```bash
   # Check PostgreSQL logs
   docker logs autohire-postgres

   # Test connection
   psql -h localhost -U autohire_user -d autohire
   ```

4. **Browser Automation Issues**
   ```bash
   # Reinstall Playwright browsers
   playwright install --force chromium

   # Check browser permissions
   xvfb-run -a playwright install chromium  # Linux
   ```

### Performance Optimization

1. **Backend Optimization**
   ```bash
   # Increase worker processes
   gunicorn --workers 8 --worker-class uvicorn.workers.UvicornWorker

   # Enable Redis caching
   redis-cli config set maxmemory 2gb
   ```

2. **Database Optimization**
   ```sql
   -- Create indexes for performance
   CREATE INDEX idx_jobs_created_at ON jobs(created_at);
   CREATE INDEX idx_applications_user_id ON applications(user_id);
   ```

3. **Vector Search Optimization**
   ```python
   # Qdrant optimization
   qdrant_client.recreate_collection(
       collection_name="jobs",
       vectors_config=VectorParams(
           size=384,
           distance=Distance.COSINE,
           hnsw_config=HnswConfigDiff(
               ef_construct=200,
               full_scan_threshold=10000
           )
       )
   )
   ```

### Logs and Debugging

```bash
# Application logs
docker logs -f autohire-backend

# Database logs
docker logs -f postgres

# All services logs
docker-compose -f docker-compose.enhanced.yml logs -f

# Specific service logs
docker-compose -f docker-compose.enhanced.yml logs -f grafana
```

### Backup and Recovery

```bash
# Database backup
pg_dump -h localhost -U autohire_user autohire > backup.sql

# Volume backup
docker run --rm -v autohire_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore database
psql -h localhost -U autohire_user autohire < backup.sql
```

## 🎯 Next Steps

After successful deployment:

1. **Configure Job Sites**: Add specific job board credentials
2. **Set Up Monitoring Alerts**: Configure Grafana alerts
3. **Performance Tuning**: Optimize based on usage patterns
4. **Security Hardening**: Implement additional security measures
5. **Scaling**: Add load balancing and horizontal scaling

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Run the validation script: `python deploy_and_validate.py`
4. Create an issue in the repository

---

**🎉 Congratulations! You now have a production-ready AI-first recruitment platform with comprehensive monitoring and automation capabilities.**