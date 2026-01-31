#!/usr/bin/env python
"""
Test script for InsightFlow API.
"""
import requests
import json
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

def test_data_ingestion():
    """Test data ingestion endpoint."""
    print("🧪 Testing Data Ingestion...")
    
    data = [
        {
            "campaign_id": "camp_test_1",
            "campaign_name": "Summer Sale Campaign",
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
            "campaign_name": "Summer Sale Campaign",
            "platform": "google_ads",
            "date": "2024-01-16",
            "impressions": 1200,
            "clicks": 60,
            "cost": 30.00,
            "conversions": 6,
            "revenue": 180.00
        },
        {
            "campaign_id": "camp_test_2",
            "campaign_name": "Winter Campaign",
            "platform": "facebook_ads",
            "date": "2024-01-15",
            "impressions": 2000,
            "clicks": 100,
            "cost": 50.00,
            "conversions": 10,
            "revenue": 300.00
        }
    ]
    
    response = requests.post(
        f"{API_BASE}/data/ingest",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 202:
        print("✅ Data ingestion successful!")
        task_id = response.json().get('task_id')
        print(f"Task ID: {task_id}")
        return True
    else:
        print(f"❌ Data ingestion failed: {response.text}")
        return False

def test_roi_analytics():
    """Test ROI analytics endpoint."""
    print("\n🧪 Testing ROI Analytics...")
    
    # Wait a bit for data to be processed
    time.sleep(2)
    
    response = requests.get(f"{API_BASE}/analytics/roi?campaign_id=camp_test_1")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ ROI analytics successful!")
        return True
    else:
        print(f"❌ ROI analytics failed: {response.text}")
        return False

def test_trends():
    """Test trends endpoint."""
    print("\n🧪 Testing Trends...")
    
    response = requests.get(f"{API_BASE}/analytics/trends?days=30")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} data points")
        if data:
            print(f"Sample: {json.dumps(data[0], indent=2)}")
        print("✅ Trends analytics successful!")
        return True
    else:
        print(f"❌ Trends analytics failed: {response.text}")
        return False

def test_insights():
    """Test insights endpoint."""
    print("\n🧪 Testing Insights...")
    
    response = requests.get(f"{API_BASE}/insights/summary")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} insights")
        if data:
            print(f"Sample: {json.dumps(data[0], indent=2)}")
        print("✅ Insights successful!")
        return True
    else:
        print(f"❌ Insights failed: {response.text}")
        return False

def test_anomalies():
    """Test anomalies endpoint."""
    print("\n🧪 Testing Anomalies...")
    
    response = requests.get(
        f"{API_BASE}/analytics/anomalies",
        params={
            "metric_type": "cost",
            "entity_id": "camp_test_1",
            "entity_type": "campaign",
            "lookback_days": 30
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} anomalies")
        if data:
            print(f"Sample: {json.dumps(data[0], indent=2)}")
        print("✅ Anomalies detection successful!")
        return True
    else:
        print(f"❌ Anomalies detection failed: {response.text}")
        return False

def check_api_health():
    """Check if API is running."""
    print("🔍 Checking API health...")
    
    try:
        response = requests.get("http://localhost:8000/api/docs/", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
            return True
        else:
            print(f"⚠️ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Start with: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("InsightFlow API Test Suite")
    print("=" * 50)
    
    # Check API health
    if not check_api_health():
        print("\n⚠️ Please start the API first:")
        print("   docker-compose up -d")
        print("   docker-compose exec web python manage.py migrate")
        return
    
    results = []
    
    # Run tests
    results.append(("Data Ingestion", test_data_ingestion()))
    results.append(("ROI Analytics", test_roi_analytics()))
    results.append(("Trends", test_trends()))
    results.append(("Insights", test_insights()))
    results.append(("Anomalies", test_anomalies()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
