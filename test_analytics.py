#!/usr/bin/env python3
"""
Test analytics endpoint with authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🔐 TESTING ANALYTICS API")
print("=" * 80)
print()

# Step 1: Login to get token
print("Step 1: Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    data={"username": "demo", "password": "demo123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    print()
    print("💡 The demo user may not exist. Let me check the health endpoint first...")
    
    health = requests.get(f"{BASE_URL}/health")
    print(f"   Health check: {health.status_code} - {health.json()}")
    exit(1)

token_data = login_response.json()
access_token = token_data.get("access_token")
print(f"✅ Login successful! Token: {access_token[:30]}...")
print()

# Step 2: Test analytics endpoint
print("Step 2: Fetching analytics overview...")
headers = {"Authorization": f"Bearer {access_token}"}

analytics_response = requests.get(
    f"{BASE_URL}/api/v1/data/overview",
    headers=headers
)

print(f"Status Code: {analytics_response.status_code}")
print()

if analytics_response.status_code == 200:
    data = analytics_response.json()
    print("✅ Analytics data retrieved successfully!")
    print()
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Failed to get analytics: {analytics_response.status_code}")
    print(f"Response: {analytics_response.text}")

print()
print("=" * 80)

