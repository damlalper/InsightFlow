# 🧪 InsightFlow Test Rehberi

## Hızlı Test (Docker ile)

### 1. Servisleri Başlat

```bash
# Tüm servisleri başlat (PostgreSQL, ClickHouse, Redis, RabbitMQ, Django, Celery)
docker-compose up -d

# Servislerin durumunu kontrol et
docker-compose ps
```

### 2. Veritabanı Migrations

```bash
# Migrations çalıştır
docker-compose exec web python manage.py migrate

# Superuser oluştur (opsiyonel)
docker-compose exec web python manage.py createsuperuser
```

### 3. Servislerin Çalıştığını Kontrol Et

```bash
# Django API'yi kontrol et
curl http://localhost:8000/api/docs/

# ClickHouse'u kontrol et
curl http://localhost:8123/ping

# Redis'i kontrol et
docker-compose exec redis redis-cli ping
```

### 4. Test Verisi Gönder (JSON)

```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d '[
    {
      "campaign_id": "camp_test_1",
      "campaign_name": "Test Campaign",
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
    },
    {
      "campaign_id": "camp_test_1",
      "campaign_name": "Test Campaign",
      "platform": "google_ads",
      "date": "2024-01-16",
      "impressions": 1200,
      "clicks": 60,
      "cost": 30.00,
      "conversions": 6,
      "revenue": 180.00
    }
  ]'
```

**Beklenen Yanıt:**
```json
{
  "message": "Data ingestion started",
  "task_id": "...",
  "records_count": 2
}
```

### 5. Analytics Endpoint'lerini Test Et

```bash
# ROI Analytics
curl "http://localhost:8000/api/v1/analytics/roi?campaign_id=camp_test_1"

# Trends
curl "http://localhost:8000/api/v1/analytics/trends?days=30"

# Insights
curl "http://localhost:8000/api/v1/insights/summary"
```

### 6. CSV Dosyası ile Test

`test_data.csv` dosyası oluştur:

```csv
campaign_id,platform,date,impressions,clicks,cost,conversions,revenue,campaign_name
camp_csv_1,facebook_ads,2024-01-15,2000,100,50.00,10,300.00,Facebook Campaign
camp_csv_1,facebook_ads,2024-01-16,2200,110,55.00,11,330.00,Facebook Campaign
```

```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: text/csv" \
  --data-binary @test_data.csv
```

### 7. Celery Task'larını Kontrol Et

```bash
# Celery worker loglarını kontrol et
docker-compose logs celery

# Veya canlı logları izle
docker-compose logs -f celery
```

### 8. Veritabanını Kontrol Et

```bash
# PostgreSQL'e bağlan
docker-compose exec postgres psql -U postgres -d insightflow

# Campaign'leri kontrol et
SELECT * FROM campaigns;

# Metric'leri kontrol et
SELECT * FROM metrics LIMIT 10;

# Çıkış
\q
```

## Unit ve Integration Testleri

### Test Suite'i Çalıştır

```bash
# Tüm testleri çalıştır
docker-compose exec web pytest

# Coverage ile
docker-compose exec web pytest --cov=. --cov-report=html

# Sadece belirli bir test dosyası
docker-compose exec web pytest tests/test_domain.py

# Verbose output ile
docker-compose exec web pytest -v
```

### Lokal Test (Docker olmadan)

```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies yükle
pip install -r requirements.txt

# Servisleri başlat (sadece DB'ler)
docker-compose up -d postgres clickhouse redis rabbitmq

# Environment variables ayarla
export POSTGRES_HOST=localhost
export CLICKHOUSE_HOST=localhost
export REDIS_HOST=localhost
export CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Migrations
python manage.py migrate

# Testleri çalıştır
pytest
```

## API Dokümantasyonu

Tarayıcıda aç:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## Sorun Giderme

### Servisler başlamıyor

```bash
# Logları kontrol et
docker-compose logs

# Servisleri yeniden başlat
docker-compose down
docker-compose up -d

# Volume'ları temizle (dikkatli!)
docker-compose down -v
```

### ClickHouse bağlantı hatası

```bash
# ClickHouse'un çalıştığını kontrol et
docker-compose exec clickhouse clickhouse-client --query "SELECT 1"

# Tabloları kontrol et
docker-compose exec clickhouse clickhouse-client --query "SHOW TABLES"
```

### Celery task'ları çalışmıyor

```bash
# Celery worker'ı kontrol et
docker-compose logs celery

# Worker'ı yeniden başlat
docker-compose restart celery

# RabbitMQ'yu kontrol et
docker-compose exec rabbitmq rabbitmqctl status
```

### Test verisi göndermek için örnek script

`test_ingestion.sh` dosyası oluştur:

```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1"

echo "Testing data ingestion..."

# Test 1: JSON ingestion
curl -X POST "$API_URL/data/ingest" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "campaign_id": "camp_1",
      "campaign_name": "Summer Sale",
      "platform": "google_ads",
      "date": "2024-01-15",
      "impressions": 1000,
      "clicks": 50,
      "cost": 25.50,
      "conversions": 5,
      "revenue": 150.00
    }
  ]'

echo -e "\n\nTesting ROI analytics..."
curl "$API_URL/analytics/roi?campaign_id=camp_1"

echo -e "\n\nTesting trends..."
curl "$API_URL/analytics/trends?days=7"

echo -e "\n\nDone!"
```

## Hızlı Kontrol Listesi

- [ ] Docker Compose servisleri çalışıyor
- [ ] Migrations başarılı
- [ ] API endpoint'leri yanıt veriyor (`/api/docs/`)
- [ ] Test verisi gönderilebiliyor
- [ ] Analytics endpoint'leri çalışıyor
- [ ] Celery task'ları işleniyor (loglardan kontrol)
- [ ] Veritabanında veri var
- [ ] Test suite başarılı

## Sonraki Adımlar

1. Daha fazla test verisi gönder
2. Farklı platform'lar için veri test et
3. Anomaly detection'ı test et
4. Insight generation'ı kontrol et
5. Performance testleri yap (yük testi)
