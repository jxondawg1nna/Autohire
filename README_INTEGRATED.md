# Autohire - Complete Integrated Platform

**Autohire** is a comprehensive, AI-powered automated recruitment platform that revolutionizes job searching through intelligent automation, real-time processing, and seamless user experience.

## 🚀 Features

### Core Functionality
- **AI-Powered CV Analysis**: Advanced parsing and optimization using OpenAI/Anthropic APIs
- **Intelligent Job Matching**: Smart job discovery across multiple platforms
- **Automated Applications**: One-click application to hundreds of jobs
- **Real-time Communication**: WebSocket-powered live updates and notifications
- **Multi-channel Messaging**: Email, SMS, WhatsApp, and push notifications
- **Visual Automation**: Browser automation with anti-detection capabilities
- **Advanced Analytics**: Comprehensive performance tracking and insights

### Technical Architecture
- **Backend**: FastAPI with Python 3.11+
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Database**: PostgreSQL with advanced indexing
- **Cache**: Redis for session management and caching
- **Message Queue**: RabbitMQ for background processing
- **Storage**: MinIO S3-compatible object storage
- **Monitoring**: Prometheus, Grafana, and ELK stack
- **Containerization**: Docker with comprehensive orchestration

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 20GB free space
- **Network**: Stable internet connection

### Software Dependencies
- **Docker Desktop** 4.0+ ([Download](https://www.docker.com/products/docker-desktop))
- **Python** 3.8+ ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

## 🎯 Quick Start

### Option 1: One-Click Startup (Recommended)

#### Windows
```bash
# Clone the repository
git clone <repository-url>
cd autohire

# Run the startup script
start-autohire.bat
```

#### Linux/macOS
```bash
# Clone the repository
git clone <repository-url>
cd autohire

# Make script executable and run
chmod +x start-autohire.sh
./start-autohire.sh
```

### Option 2: Manual Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd autohire
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env  # or use your preferred editor
   ```

3. **Start Services**
   ```bash
   # Using Docker Compose
   docker-compose up -d
   
   # Or using the Python manager
   python scripts/start-autohire.py start --monitor
   ```

## 🌐 Service URLs

Once started, access these services:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:3000 | Primary user interface |
| **Integrated Dashboard** | http://localhost:3000/dashboard/integrated | Advanced integrated dashboard |
| **API Documentation** | http://localhost:8000/docs | Interactive API documentation |
| **API Health Check** | http://localhost:8000/health | System health status |
| **MinIO Console** | http://localhost:9001 | Object storage management |
| **RabbitMQ Management** | http://localhost:15672 | Message queue monitoring |
| **Grafana Dashboard** | http://localhost:3001 | Performance monitoring |
| **Kibana Logs** | http://localhost:5601 | Log analysis |

### Default Credentials
- **MinIO**: `autohire` / `autohire_password`
- **RabbitMQ**: `autohire` / `autohire_password`
- **Grafana**: `admin` / `admin` (change on first login)

## 🛠️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Core Settings
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Communication
TWILIO_ACCOUNT_SID=your-twilio-sid
SENDGRID_API_KEY=your-sendgrid-key

# Automation
SCRAPING_ENABLED=True
MAX_DAILY_APPLICATIONS=50
AUTOHIRE_SPONGECAKE_ENABLED=True
```

### Service Configuration

#### Database
- **PostgreSQL 15** with optimized configuration
- Automatic table creation and seeding
- Connection pooling and performance tuning

#### Redis
- Session management and caching
- Real-time data storage
- Celery broker for background tasks

#### Message Queue
- RabbitMQ for reliable message delivery
- Background job processing
- Email and notification queuing

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Infrastructure │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Docker)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • API Gateway   │    │ • PostgreSQL    │
│ • Real-time UI  │    │ • WebSocket     │    │ • Redis         │
│ • Components    │    │ • Services      │    │ • RabbitMQ      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

#### Backend Services
- **main_integrated.py**: Enhanced main application with all integrations
- **background_tasks.py**: Task management and scheduling
- **websocket_manager.py**: Real-time communication handling
- **API Routes**: Comprehensive REST API with 12+ endpoint groups

#### Frontend Components
- **Integrated Dashboard**: Complete management interface
- **Real-time Updates**: Live notifications and status
- **WebSocket Integration**: Bidirectional communication
- **Component Library**: Reusable UI components

#### Infrastructure
- **Docker Compose**: Multi-service orchestration
- **Production Stack**: Monitoring, logging, and alerting
- **Auto-scaling**: Resource management and optimization

## 🔧 Development

### Local Development Setup

1. **Backend Development**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python main_integrated.py
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

### Adding New Features

1. **Backend Service**
   ```python
   # Add to backend/app/services/
   class NewService:
       async def initialize(self):
           # Service initialization
           pass
   ```

2. **Frontend Component**
   ```typescript
   // Add to frontend/src/components/
   const NewComponent: React.FC = () => {
       return <div>New Feature</div>;
   };
   ```

3. **API Endpoint**
   ```python
   # Add to backend/app/api/v1/
   @router.get("/new-endpoint")
   async def new_endpoint():
       return {"message": "New feature"}
   ```

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **System Health**: `/health` endpoint with comprehensive metrics
- **Real-time Status**: WebSocket-powered live updates
- **Performance Metrics**: Memory, CPU, and disk usage
- **Service Status**: Individual service health monitoring

### Production Monitoring
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visual dashboards and reporting
- **ELK Stack**: Centralized logging and analysis
- **Custom Metrics**: Application-specific monitoring

### Key Metrics
- Application response times
- Job processing rates
- User engagement analytics
- System resource utilization
- Error rates and debugging

## 🚀 Deployment

### Development Deployment
```bash
# Start all services
./start-autohire.sh

# Monitor logs
docker-compose logs -f
```

### Production Deployment
```bash
# Use production configuration
docker-compose -f docker-compose.production.yml up -d

# Scale services
docker-compose up --scale backend=3 --scale celery-worker=2
```

### Cloud Deployment
- **AWS**: ECS/EKS with RDS and ElastiCache
- **Google Cloud**: GKE with Cloud SQL and Memorystore
- **Azure**: AKS with Azure Database and Redis Cache

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
python scripts/test-integration.py
```

### Test Coverage
- Unit tests for all services
- Integration tests for API endpoints
- End-to-end tests for user workflows
- Performance and load testing

## 🛡️ Security

### Built-in Security Features
- JWT authentication with refresh tokens
- Rate limiting and DDoS protection
- Input validation and sanitization
- CORS configuration
- SQL injection prevention
- XSS protection

### Production Security
- HTTPS enforcement with SSL certificates
- Database encryption at rest
- Secure secret management
- Network isolation and firewalls
- Regular security audits

## 📈 Performance

### Optimization Features
- Redis caching for frequently accessed data
- Database query optimization with indexes
- Background task processing with Celery
- CDN integration for static assets
- Lazy loading and code splitting

### Scalability
- Horizontal scaling with Docker containers
- Load balancing with Nginx
- Database connection pooling
- Asynchronous processing
- Microservices architecture

## 🆘 Troubleshooting

### Common Issues

1. **Services Not Starting**
   ```bash
   # Check Docker status
   docker ps
   
   # View logs
   docker-compose logs [service-name]
   
   # Restart services
   ./start-autohire.sh
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker-compose logs postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

### Getting Help
- Check the logs in the `logs/` directory
- Review the health check endpoint: http://localhost:8000/health
- Use the system status dashboard for real-time diagnostics
- Check Docker container status: `docker ps`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all new frontend code
- Add comprehensive tests
- Update documentation
- Follow semantic versioning

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI and Anthropic for AI capabilities
- The FastAPI and Next.js communities
- Docker and the containerization ecosystem
- All contributors and supporters

---

**Autohire** - Revolutionizing job search through intelligent automation.

For more information, visit our [documentation](http://localhost:8000/docs) or contact support.