# InsightFlow Setup Guide

## Quick Start with Docker

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser (optional):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application:**
   - API: http://localhost:8000/api/v1/
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

## Testing the API

### 1. Ingest Sample Data

```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d '[
    {
      "campaign_id": "camp_1",
      "campaign_name": "Summer Sale",
      "platform": "google_ads",
      "ad_group_id": "ag_1",
      "ad_group_name": "Banner Ads",
      "ad_id": "ad_1",
      "ad_name": "Banner 1",
      "date": "2024-01-15",
      "impressions": 1000,
      "clicks": 50,
      "cost": 25.50,
      "conversions": 5,
      "revenue": 150.00
    }
  ]'
```

### 2. Get ROI Analytics

```bash
curl http://localhost:8000/api/v1/analytics/roi?campaign_id=camp_1
```

### 3. Get Trends

```bash
curl http://localhost:8000/api/v1/analytics/trends?days=30
```

## Development Notes

- Authentication is currently disabled for easier development (see `api/views.py`)
- Enable authentication by changing `permission_classes = []` to `permission_classes = [IsAuthenticated]`
- Use JWT tokens from `/api/v1/auth/login` when authentication is enabled
