#!/usr/bin/env python3
"""
Test all analytics endpoints to verify they're working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 TESTING ALL ANALYTICS ENDPOINTS")
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

# Test each endpoint
endpoints = [
    ("GET /api/v1/data/overview", f"{BASE_URL}/api/v1/data/overview", "Dashboard Analytics"),
    ("GET /api/v1/data/sentiment/live", f"{BASE_URL}/api/v1/data/sentiment/live", "Live Sentiment Score"),
    ("GET /api/v1/data/posts/recent?limit=5", f"{BASE_URL}/api/v1/data/posts/recent?limit=5", "Recent Tweets"),
    ("GET /api/v1/data/hashtags/trending", f"{BASE_URL}/api/v1/data/hashtags/trending", "Trending Hashtags"),
    ("GET /api/v1/data/stats", f"{BASE_URL}/api/v1/data/stats", "Overall Statistics"),
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
            
            # Show key data points
            if "data" in data:
                if "total_posts" in data["data"]:
                    print(f"     📊 Total Posts: {data['data']['total_posts']}")
                if "sentiment" in data["data"]:
                    sentiment = data["data"]["sentiment"]
                    if isinstance(sentiment, dict) and "positive" in sentiment:
                        print(f"     😊 Sentiment: +{sentiment.get('positive', 0)} / ={sentiment.get('neutral', 0)} / -{sentiment.get('negative', 0)}")
                if "sentiment_score" in data["data"]:
                    print(f"     📈 Sentiment Score: {data['data']['sentiment_score']}")
                if "posts" in data["data"]:
                    print(f"     📝 Posts Returned: {len(data['data']['posts'])}")
                if "hashtags" in data["data"]:
                    top_3 = data['data']['hashtags'][:3]
                    hashtag_list = ', '.join([f"#{h['tag']}({h['count']})" for h in top_3])
                    print(f"     🔥 Top Hashtags: {hashtag_list}")

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
    print("🎉 ALL ENDPOINTS ARE WORKING PERFECTLY!")
    print()
    print("📍 Access the interactive API documentation:")
    print(f"   {BASE_URL}/docs")
    print()
    print("🔐 Login credentials:")
    print("   Username: demo")
    print("   Password: demo123")
else:
    print("⚠️  Some endpoints need attention")

print()
print("=" * 80)

