# API Usage Examples

## Authentication

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register?username=john&email=john@example.com&password=SecurePass123"
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "SecurePass123"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "user_123",
      "username": "john",
      "email": "john@example.com",
      "role": "user"
    }
  }
}
```

## Data Endpoints

### Get Dashboard Overview
```bash
curl -X GET "http://localhost:8000/api/v1/data/overview?range=Last%207%20Days" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Live Sentiment
```bash
curl -X GET "http://localhost:8000/api/v1/data/sentiment/live" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Sentiment Time Series
```bash
curl -X GET "http://localhost:8000/api/v1/data/sentiment/series?range=Last%2030%20Days&granularity=day" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Trending Hashtags
```bash
curl -X GET "http://localhost:8000/api/v1/data/hashtags/trending?limit=20&min_mentions=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Hashtag Details
```bash
curl -X GET "http://localhost:8000/api/v1/data/hashtags/Nigeria" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Keyword Trends
```bash
curl -X GET "http://localhost:8000/api/v1/data/keywords/trends?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Influencers
```bash
curl -X GET "http://localhost:8000/api/v1/data/influencers?limit=20&min_followers=100000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Geographic Data
```bash
curl -X GET "http://localhost:8000/api/v1/data/geographic/states?range=Last%207%20Days" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Top Posts
```bash
curl -X GET "http://localhost:8000/api/v1/data/posts/top?limit=20&min_engagement=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Posts
```bash
curl -X POST "http://localhost:8000/api/v1/data/posts/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "election",
    "range": "Last 7 Days",
    "limit": 50,
    "offset": 0,
    "sentiment": "positive"
  }'
```

### Get Anomalies
```bash
curl -X GET "http://localhost:8000/api/v1/data/anomalies?severity=high&status=new" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## AI Endpoints

### Generate Summary
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate/summary" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "section": "overview",
    "subject": "#Nigeria",
    "template": "hashtag",
    "range": "Last 30 Days",
    "context": {
      "mentions": 15000,
      "sentiment": {"pos": 35, "neg": 40, "neu": 25},
      "top_keywords": ["politics", "economy"]
    }
  }'
```

### Generate Insights
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate/insights" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "section": "sentiment",
    "subject": "#Nigeria",
    "template": "hashtag",
    "range": "Last 30 Days",
    "context": {
      "mentions": 15000,
      "sentiment": {"pos": 35, "neg": 40, "neu": 25}
    }
  }'
```

## Report Endpoints

### Generate Report
```bash
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "hashtag",
    "subject": "#Nigeria",
    "range": "Last 30 Days",
    "sections": {
      "overview": true,
      "timeline": true,
      "sentiment": true,
      "narratives": true,
      "geo": true,
      "influencers": true,
      "topPosts": true,
      "claims": false,
      "appendix": true
    }
  }'
```

### Check Report Status
```bash
curl -X GET "http://localhost:8000/api/v1/reports/REPORT_ID/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Download Report
```bash
curl -X GET "http://localhost:8000/api/v1/reports/REPORT_ID/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output report.pdf
```

### List Reports
```bash
curl -X GET "http://localhost:8000/api/v1/reports?limit=50&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Admin Endpoints

### Get Alert Rules
```bash
curl -X GET "http://localhost:8000/api/v1/admin/alert-rules" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Alert Rule
```bash
curl -X POST "http://localhost:8000/api/v1/admin/alert-rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sentiment Drop Alert",
    "description": "Alert when sentiment drops by 15%",
    "enabled": true,
    "conditions": {
      "metric": "sentiment",
      "threshold": -15,
      "time_window": "24h",
      "comparison": "day_over_day"
    },
    "actions": ["email", "webhook"]
  }'
```

### Get Data Connectors (Admin only)
```bash
curl -X GET "http://localhost:8000/api/v1/admin/connectors" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Python Examples

### Using requests library
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "john", "password": "SecurePass123"}
)
token = response.json()["data"]["token"]

# Set headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Get overview data
overview = requests.get(
    f"{BASE_URL}/data/overview",
    params={"range": "Last 7 Days"},
    headers=headers
)
print(overview.json())

# Generate report
report_response = requests.post(
    f"{BASE_URL}/reports/generate",
    json={
        "template": "hashtag",
        "subject": "#Nigeria",
        "range": "Last 30 Days",
        "sections": {"overview": True, "sentiment": True}
    },
    headers=headers
)
report_id = report_response.json()["data"]["report_id"]

# Check report status
status = requests.get(
    f"{BASE_URL}/reports/{report_id}/status",
    headers=headers
)
print(status.json())
```

### Using httpx (async)
```python
import httpx
import asyncio

async def main():
    BASE_URL = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "john", "password": "SecurePass123"}
        )
        token = response.json()["data"]["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get trending hashtags
        hashtags = await client.get(
            f"{BASE_URL}/data/hashtags/trending",
            params={"limit": 10},
            headers=headers
        )
        print(hashtags.json())

asyncio.run(main())
```
# Alembic Configuration File

[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = postgresql://user:password@localhost:5432/social_monitor

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

