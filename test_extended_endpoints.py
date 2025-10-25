#!/usr/bin/env python3
"""
Test extended API endpoints to verify all implementations
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 TESTING EXTENDED API ENDPOINTS")
print("=" * 80)
print()

# Step 1: Login
print("Step 1: Authenticating...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    data={"username": "demo", "password": "demo123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Authenticated successfully")
print()

# Test extended endpoints
endpoints = [
    ("GET /api/v1/data/overview", f"{BASE_URL}/api/v1/data/overview", "Dashboard Overview"),
    ("GET /api/v1/data/sentiment/live", f"{BASE_URL}/api/v1/data/sentiment/live", "Live Sentiment"),
    ("GET /api/v1/data/sentiment/series", f"{BASE_URL}/api/v1/data/sentiment/series?granularity=day", "Sentiment Time Series"),
    ("GET /api/v1/data/posts/recent", f"{BASE_URL}/api/v1/data/posts/recent?limit=5", "Recent Posts"),
    ("GET /api/v1/data/posts/top", f"{BASE_URL}/api/v1/data/posts/top?limit=5", "Top Posts"),
    ("GET /api/v1/data/posts/search", f"{BASE_URL}/api/v1/data/posts/search?q=Nigeria&limit=5", "Search Posts"),
    ("GET /api/v1/data/hashtags/trending", f"{BASE_URL}/api/v1/data/hashtags/trending", "Trending Hashtags"),
    ("GET /api/v1/data/hashtags/Nigeria", f"{BASE_URL}/api/v1/data/hashtags/Nigeria", "Hashtag Detail"),
    ("GET /api/v1/data/influencers", f"{BASE_URL}/api/v1/data/influencers?limit=5", "Influencers"),
    ("GET /api/v1/data/geographic/states", f"{BASE_URL}/api/v1/data/geographic/states", "Geographic Data"),
    ("GET /api/v1/data/anomalies", f"{BASE_URL}/api/v1/data/anomalies?limit=5", "Anomalies"),
    ("GET /api/v1/data/connectors", f"{BASE_URL}/api/v1/data/connectors", "Data Connectors"),
    ("GET /api/v1/data/stats", f"{BASE_URL}/api/v1/data/stats", "Overall Stats"),
]

results = []

for endpoint_name, url, description in endpoints:
    print(f"Testing: {description}")
    print(f"  Endpoint: {endpoint_name}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {response.status_code} OK")
            
            # Show sample data
            if "data" in data:
                data_keys = list(data["data"].keys()) if isinstance(data["data"], dict) else "array"
                print(f"     📦 Response keys: {data_keys}")
            
            results.append((endpoint_name, "✅ PASS", None))
        else:
            print(f"  ❌ Status: {response.status_code}")
            print(f"     Error: {response.text[:100]}")
            results.append((endpoint_name, "❌ FAIL", response.status_code))
    
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        results.append((endpoint_name, "❌ ERROR", str(e)))
    
    print()

# Summary
print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print()

passed = sum(1 for _, status, _ in results if "PASS" in status)
total = len(results)

for endpoint, status, error in results:
    print(f"{status} {endpoint}")
    if error:
        print(f"   Error: {error}")

print()
print(f"✅ {passed}/{total} endpoints working correctly")
print()

if passed == total:
    print("🎉 ALL EXTENDED ENDPOINTS ARE WORKING!")
    print()
    print("📚 Frontend developers can now integrate with:")
    print("   • Dashboard analytics")
    print("   • Sentiment analysis")
    print("   • Post search and filtering")
    print("   • Hashtag tracking")
    print("   • Influencer metrics")
    print("   • Geographic insights")
    print("   • Anomaly detection")
    print()
    print("📖 See FRONTEND_API_GUIDE.md for integration examples")
else:
    print(f"⚠️  {total - passed} endpoints need attention")

print()
print("=" * 80)

