# 🚀 Hızlı Başlangıç - Test Etme

## 1️⃣ Servisleri Başlat

PowerShell'de:

```powershell
# Docker Compose ile tüm servisleri başlat
docker-compose up -d

# Durumu kontrol et
docker-compose ps
```

## 2️⃣ Veritabanı Hazırla

```powershell
# Migrations çalıştır
docker-compose exec web python manage.py migrate

# (Opsiyonel) Admin kullanıcısı oluştur
docker-compose exec web python manage.py createsuperuser
```

## 3️⃣ API'yi Test Et

### Tarayıcıda:
- **API Dokümantasyonu**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### PowerShell ile Test:

```powershell
# Test verisi gönder
$body = @'
[
  {
    "campaign_id": "camp_test_1",
    "campaign_name": "Test Campaign",
    "platform": "google_ads",
    "date": "2024-01-15",
    "impressions": 1000,
    "clicks": 50,
    "cost": 25.50,
    "conversions": 5,
    "revenue": 150.00
  }
]
'@

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/data/ingest" `
  -Method Post -Body $body -ContentType "application/json"
```

### Python Script ile Test:

```powershell
# Test script'ini çalıştır
python test_ingestion.py
```

## 4️⃣ Analytics Test Et

```powershell
# ROI Analytics
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/roi?campaign_id=camp_test_1"

# Trends
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/trends?days=30"

# Insights
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/insights/summary"
```

## 5️⃣ Test Suite Çalıştır

```powershell
# Tüm testleri çalıştır
docker-compose exec web pytest

# Coverage ile
docker-compose exec web pytest --cov=. --cov-report=term
```

## 6️⃣ Logları Kontrol Et

```powershell
# Django logları
docker-compose logs web

# Celery logları
docker-compose logs celery

# Tüm servisler
docker-compose logs
```

## ⚠️ Sorun Giderme

### Servisler başlamıyor:
```powershell
docker-compose down
docker-compose up -d
```

### Port zaten kullanılıyor:
`docker-compose.yml` dosyasında portları değiştir veya kullanan servisi durdur.

### ClickHouse bağlantı hatası:
```powershell
docker-compose restart clickhouse
```

## ✅ Başarı Kontrolü

- [ ] http://localhost:8000/api/docs/ açılıyor
- [ ] Test verisi gönderilebiliyor
- [ ] Analytics endpoint'leri çalışıyor
- [ ] Test suite başarılı

Detaylı test rehberi için `TEST_GUIDE.md` dosyasına bakın!
