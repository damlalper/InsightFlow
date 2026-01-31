# InsightFlow - AI-Powered Marketing Analytics Backend

> **Production-ready SaaS platform** built with Django, demonstrating enterprise-level Python backend engineering skills for marketing intelligence platforms like Improvado.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-Latest-yellow.svg)](https://clickhouse.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 🎯 Built for Enterprise Marketing Analytics

InsightFlow is a **scalable, high-performance backend SaaS platform** designed to collect, normalize, analyze, and serve marketing performance data from multiple sources. This project demonstrates production-ready Python backend engineering with focus on:

- ✅ **Scalability & Performance** - Async processing, high-load support, BigData analytics
- ✅ **Clean Architecture** - DDD, SOLID principles, Repository pattern
- ✅ **Enterprise Practices** - CI/CD, comprehensive testing, clean code
- ✅ **Production-Ready** - Docker, monitoring, error handling, logging

## 🚀 Key Features

### Core Capabilities
- **Async Data Ingestion** - Celery-based batch processing for JSON & CSV
- **Analytics Engine** - ROI, CPC, CPA, CTR calculations with ClickHouse
- **Anomaly Detection** - Z-score based detection for metric anomalies
- **Insight Generation** - Automated insights for campaigns, ads, budget optimization
- **RESTful API** - Django Rest Framework with JWT auth and OpenAPI docs

### Technical Highlights
- **High-Load/BigData** - ClickHouse for analytics, optimized aggregations
- **Async Processing** - Celery + RabbitMQ for background tasks
- **Performance** - Redis caching, database indexing, query optimization
- **Scalability** - Microservices-ready architecture, horizontal scaling support

## 💻 Tech Stack

### Backend
- **Python 3.11** - Modern Python with type hints
- **Django 4.2** - Web framework
- **Django Rest Framework** - REST API
- **Celery** - Async task processing
- **RabbitMQ** - Message broker

### Databases
- **PostgreSQL** - Transactional data (Campaigns, Metrics, Insights)
- **ClickHouse** - Analytics/BigData (high-performance aggregations)
- **Redis** - Caching & Celery broker

### Infrastructure
- **Docker & Docker Compose** - Containerized development & deployment
- **GitHub Actions** - CI/CD pipeline
- **Pytest** - Testing framework (80%+ coverage target)

### Architecture Principles
- **Domain-Driven Design (DDD)** - Clean separation of concerns
- **SOLID Principles** - Maintainable, extensible code
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic orchestration

## 🏗️ Architecture

```
insightflow/
├── core/
│   ├── domain/          # Pure business logic (no framework deps)
│   ├── services/        # Application layer (use cases)
│   ├── repositories/     # Repository pattern implementations
│   └── infrastructure/  # ClickHouse, external adapters
├── ingestion/           # Async data ingestion (Celery)
├── analytics/           # Analytics calculations (ROI, anomalies)
├── api/                 # REST API endpoints
└── tests/               # Comprehensive test suite
```

## ⚡ Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+ (for local development)

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 3. Access API
- **API Docs**: http://localhost:8000/api/docs/
- **API**: http://localhost:8000/api/v1/
- **RabbitMQ Management**: http://localhost:15672/ (guest/guest)

### 4. Test Data Ingestion
```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d '[{
    "campaign_id": "camp_1",
    "campaign_name": "Test Campaign",
    "platform": "google_ads",
    "date": "2024-01-15",
    "impressions": 1000,
    "clicks": 50,
    "cost": 25.50,
    "conversions": 5,
    "revenue": 150.00
  }]'
```

## 📚 API Endpoints

### Data Ingestion
- `POST /api/v1/data/ingest` - Ingest marketing data (JSON/CSV)

### Analytics
- `GET /api/v1/analytics/roi` - Calculate ROI, CPC, CPA, CTR
- `GET /api/v1/analytics/trends` - Time series trends
- `GET /api/v1/analytics/anomalies` - Anomaly detection

### Insights
- `GET /api/v1/insights/summary` - Generated marketing insights

**Full API Documentation**: http://localhost:8000/api/docs/

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Integration tests
pytest tests/test_integration.py -v
```

**Test Coverage**: 80%+ target (domain & analytics: 100%)

## 📊 Performance

- **API Response Time**: < 200ms for analytics endpoints
- **Async Processing**: Celery for large dataset ingestion
- **High-Performance Analytics**: ClickHouse for aggregations
- **Caching**: Redis for frequent queries
- **Database Optimization**: Indexing, query optimization

## 🛠️ Development

### Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up -d postgres clickhouse redis rabbitmq

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Start Celery worker
celery -A insightflow worker --loglevel=info
```

### Code Quality
- **Linting**: black, flake8, isort
- **Type Checking**: mypy
- **Testing**: pytest with 80%+ coverage
- **CI/CD**: GitHub Actions

## 📖 Documentation

- **[Setup Guide](docs/QUICK_START.md)** - Quick start instructions
- **[Test Guide](docs/TEST_GUIDE.md)** - Comprehensive testing guide
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Feature overview
- **[Job Requirements](docs/JOB_REQUIREMENTS_CHECKLIST.md)** - Requirements checklist
- **[PRD](docs/prd.md)** - Product Requirements Document

## 🎓 Skills Demonstrated

This project showcases expertise in:

- ✅ **Python/Django Backend Development** - Production-ready SaaS architecture
- ✅ **High-Load/BigData Systems** - ClickHouse, async processing, scalability
- ✅ **REST API Design** - DRF, OpenAPI, JWT authentication
- ✅ **Clean Architecture** - DDD, SOLID, Repository pattern, Service layer
- ✅ **Async Processing** - Celery, RabbitMQ, background tasks
- ✅ **Database Design** - PostgreSQL, ClickHouse, Redis, optimization
- ✅ **Testing** - Unit, integration tests, 80%+ coverage
- ✅ **DevOps** - Docker, CI/CD, containerization
- ✅ **Code Quality** - Type hints, linting, documentation

## 🏢 Enterprise Features

- **Scalable Architecture** - Ready for horizontal scaling
- **High Performance** - Optimized for < 200ms response times
- **Production-Ready** - Error handling, logging, monitoring
- **Clean Code** - SOLID, DDD, maintainable, well-documented
- **CI/CD Pipeline** - Automated testing and deployment
- **Comprehensive Testing** - Unit, integration, coverage reports

## 📝 Project Structure

```
insightflow/
├── core/                    # Domain, services, repositories
│   ├── domain/              # Pure business logic
│   ├── services/            # Application services
│   ├── repositories/        # Data access layer
│   └── infrastructure/      # External adapters
├── ingestion/               # Data ingestion (Celery)
├── analytics/               # Analytics engine
├── api/                     # REST API
├── tests/                   # Test suite
├── docs/                    # Documentation
├── docker-compose.yml       # Services configuration
└── requirements.txt         # Dependencies
```

## 🔄 CI/CD

GitHub Actions workflow includes:
- Linting (black, flake8, isort)
- Test execution with coverage
- Code quality checks
- Docker image building

## 📄 License

See [LICENSE](LICENSE) file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔮 Future Enhancements

- ML-based anomaly detection
- Real-time streaming ingestion
- Advanced AI insight summarization
- Dashboard frontend
- Multi-tenant support

---

**Built with ❤️ for enterprise marketing analytics**

For detailed documentation, see the [docs](docs/) folder.
