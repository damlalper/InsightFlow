# InsightFlow – AI-Powered Marketing Analytics Backend
## Product Requirements Document (PRD) & System Architecture

---

## 1. Product Overview

InsightFlow is a scalable, AI-powered marketing analytics backend platform designed to collect, normalize, analyze, and serve marketing performance data from multiple sources.  
The system mimics the core backend architecture of enterprise marketing intelligence platforms (e.g., Improvado) and is built with scalability, performance, and clean architecture principles.

The product provides REST APIs for data ingestion, analytics computation, anomaly detection, and insight generation, optimized for high-load and future AI integration.

---

## 2. Goals & Objectives

### Primary Goals
- Build a production-ready backend SaaS platform
- Demonstrate strong Python backend engineering skills
- Implement scalable, high-performance analytics pipelines
- Apply clean code, SOLID, DDD, and async principles

### Success Metrics
- API response time < 200ms for analytics endpoints
- Ability to process large datasets asynchronously
- Clear separation of domain, application, and infrastructure layers
- Full Dockerized local environment with CI-ready structure

---

## 3. User Personas

### 3.1 Marketing Analyst
- Wants fast insights on campaign performance
- Needs ROI, trends, and anomaly detection
- Consumes data via dashboards or BI tools

### 3.2 Backend Engineer (Internal)
- Maintains ingestion pipelines
- Optimizes performance and scaling
- Extends analytics and AI capabilities

---

## 4. Functional Requirements

### 4.1 Data Ingestion
- Ingest marketing data via REST API
- Accept JSON and CSV payloads
- Support batch ingestion
- Validate and normalize incoming data
- Run ingestion asynchronously

### 4.2 Core Entities
- Campaign
- AdGroup
- Ad
- Metric (impressions, clicks, cost, conversions, revenue)
- Insight

### 4.3 Analytics Engine
- Calculate ROI, CPC, CPA, CTR
- Aggregate metrics by date, campaign, platform
- Support time-series analytics
- Store analytical data in ClickHouse

### 4.4 Anomaly Detection
- Detect abnormal spikes/drops using Z-score
- Flag anomalies per metric
- Store anomaly events

### 4.5 Insight Generation
- Generate summarized insights:
  - Best performing campaigns
  - Underperforming ads
  - Budget inefficiency signals
- Prepare AI-ready structured outputs

### 4.6 API Layer
- RESTful endpoints using Django Rest Framework
- JWT-based authentication
- Pagination and filtering
- OpenAPI / Swagger documentation

---

## 5. Non-Functional Requirements

- High performance and scalability
- Asynchronous task execution
- Clean, maintainable, well-documented code
- Linux-first development
- Full test coverage
- CI-ready architecture

---

## 6. Tech Stack

### Backend
- Python 3.11
- Django
- Django Rest Framework

### Async & Messaging
- Celery
- RabbitMQ
- asyncio

### Databases
- PostgreSQL (transactional)
- ClickHouse (analytics)
- Redis (cache & broker)

### Infrastructure
- Docker
- Docker Compose
- GitHub Actions (CI)

### Testing
- Pytest
- pytest-django

---

## 7. System Architecture
Client / BI Tool
|
v
API Gateway (DRF)
|
v
Application Layer (Services)
|
+--------------------+
| |
Async Tasks Analytics Engine
(Celery) (ClickHouse)
| |
v v
PostgreSQL ClickHouse
|
v
Redis (Cache)


---

### 7.2 Architectural Layers (DDD)

#### Domain Layer
- Pure business logic
- Entities: Campaign, Metric, Insight
- No framework dependencies

#### Application Layer
- Services orchestrating use cases
- AnalyticsService
- IngestionService
- InsightService

#### Infrastructure Layer
- Django ORM models
- Database clients
- External adapters
- Celery tasks

---

## 8. Data Flow

### 8.1 Ingestion Flow
1. Client sends batch data to `/api/v1/data/ingest`
2. API validates schema
3. Data sent to Celery queue
4. Worker normalizes and stores data
5. Metrics written to PostgreSQL and ClickHouse

### 8.2 Analytics Flow
1. Client requests analytics endpoint
2. Service queries ClickHouse
3. Aggregations computed
4. Cached in Redis
5. Response returned

---

## 9. API Endpoints

### Ingestion
POST /api/v1/data/ingest


### Analytics
GET /api/v1/analytics/roi
GET /api/v1/analytics/trends
GET /api/v1/analytics/anomalies


### Insights
GET /api/v1/insights/summary


---

## 10. Performance Strategy

- Use ClickHouse for heavy aggregations
- Cache frequent queries with Redis
- Async ingestion with Celery
- Database indexing
- Pagination and query optimization

---

## 11. Testing Strategy

- Unit tests for domain logic
- Integration tests for APIs
- Mock external services
- Minimum 80% coverage

---

## 12. CI Pipeline

### GitHub Actions Steps
1. Install dependencies
2. Run lint checks
3. Run Pytest
4. Build Docker image

---

## 13. Repository Structure


insightflow/
├── core/
│ ├── domain/
│ ├── services/
│ ├── repositories/
├── ingestion/
│ ├── tasks.py
│ ├── adapters/
├── analytics/
│ ├── roi.py
│ ├── anomalies.py
├── api/
├── tests/
├── docker/
├── .github/workflows/
├── docker-compose.yml
└── README.md


---

## 14. Future Improvements

- ML-based anomaly detection
- Real-time streaming ingestion
- Advanced AI insight summarization
- Dashboard frontend

---

## 15. Summary

InsightFlow demonstrates a real-world, production-grade backend SaaS architecture focused on marketing analytics, scalability, performance, and clean engineering practices.  
The project is designed to fully match enterprise-level expectations for Python backend roles in data-driven SaaS companies.

### 7.1 High-Level Architecture

