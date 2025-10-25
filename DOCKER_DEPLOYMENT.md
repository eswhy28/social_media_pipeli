# Social Media Pipeline - Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Starting the Application

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Generate sample data (first time only):**
   ```bash
   docker-compose exec api python generate_1000_tweets.py
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Main API: http://localhost:8000

4. **Default Credentials:**
   - Username: `demo`
   - Password: `demo123`

### Services Running

The application consists of 4 services:

1. **API** (Port 8000) - Main FastAPI application
2. **Redis** (Port 6379) - Caching and message broker
3. **Worker** - Celery worker for background tasks
4. **Beat** - Celery beat for scheduled tasks

### Useful Commands

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove volumes:**
```bash
docker-compose down -v
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

**Check service status:**
```bash
docker-compose ps
```

**Execute commands inside container:**
```bash
docker-compose exec api bash
```

## 🔧 Configuration

### Environment Variables

Copy `.env.docker` to `.env` and update:

```bash
cp .env.docker .env
```

Key variables to configure:
- `SECRET_KEY` - Change to a secure random string
- `CORS_ORIGINS` - Update with your frontend domain
- `ENVIRONMENT` - Set to `production` for deployment

### Port Configuration

To change the default port (8000), modify `docker-compose.yml`:

```yaml
api:
  ports:
    - "YOUR_PORT:8000"  # Change YOUR_PORT to desired port
```

## 📊 API Endpoints

All endpoints are documented at: http://localhost:8000/docs

### Authentication
- `POST /api/v1/auth/token` - Get JWT token

### Data Endpoints
- `GET /api/v1/data/overview` - Dashboard overview
- `GET /api/v1/data/sentiment/live` - Real-time sentiment
- `GET /api/v1/data/sentiment/series` - Sentiment time series
- `GET /api/v1/data/posts/recent` - Recent posts
- `GET /api/v1/data/posts/top` - Top posts by engagement
- `GET /api/v1/data/posts/search` - Search posts
- `GET /api/v1/data/hashtags/trending` - Trending hashtags
- `GET /api/v1/data/hashtags/{tag}` - Hashtag details
- `GET /api/v1/data/influencers` - Top influencers
- `GET /api/v1/data/geographic/states` - Geographic data
- `GET /api/v1/data/anomalies` - Detected anomalies
- `GET /api/v1/data/connectors` - Data source status
- `GET /api/v1/data/stats` - Overall statistics

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{id}/status` - Check report status

### AI
- `POST /api/v1/ai/generate/summary` - Generate AI summary
- `POST /api/v1/ai/generate/insights` - Generate insights

## 🔐 Security

### Production Checklist

1. **Change SECRET_KEY:**
   ```bash
   # Generate a secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update CORS_ORIGINS:**
   ```env
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

3. **Use HTTPS:**
   - Deploy behind a reverse proxy (nginx/traefik)
   - Enable SSL/TLS certificates

4. **Environment:**
   ```env
   ENVIRONMENT=production
   DEBUG=False
   ```

## 🌐 Frontend Integration

### API Base URL
```javascript
const API_BASE_URL = "http://localhost:8000";
```

### Authentication Flow

```javascript
// 1. Login and get token
const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'demo',
    password: 'demo123'
  })
});

const { access_token } = await response.json();

// 2. Use token for authenticated requests
const data = await fetch(`${API_BASE_URL}/api/v1/data/overview`, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### Example API Calls

**Get Dashboard Overview:**
```javascript
const overview = await fetch(
  `${API_BASE_URL}/api/v1/data/overview?range=Last 7 Days`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());
```

**Search Posts:**
```javascript
const posts = await fetch(
  `${API_BASE_URL}/api/v1/data/posts/search?q=Nigeria&limit=20`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());
```

**Get Trending Hashtags:**
```javascript
const hashtags = await fetch(
  `${API_BASE_URL}/api/v1/data/hashtags/trending?limit=10`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());
```

## 📈 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "database": "SQLite",
  "cache": "Redis"
}
```

### Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

## 🐛 Troubleshooting

### API not responding
```bash
# Check if container is running
docker-compose ps

# View logs
docker-compose logs api

# Restart service
docker-compose restart api
```

### Database issues
```bash
# Reinitialize database
docker-compose exec api python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

# Generate sample data
docker-compose exec api python generate_1000_tweets.py
```

### Redis connection issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Port already in use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

## 📦 Data Persistence

Data is persisted in Docker volumes:
- `redis_data` - Redis cache
- `./data` - SQLite database
- `./logs` - Application logs

To backup data:
```bash
# Backup database
cp social_media.db social_media.db.backup

# Or use docker cp
docker cp social_media_api:/app/social_media.db ./backup/
```

## 🔄 Updates and Maintenance

### Update application code:
```bash
git pull
docker-compose up -d --build
```

### Clear cache:
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### View application logs:
```bash
docker-compose exec api tail -f logs/*.log
```

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify all services are healthy: `docker-compose ps`
3. Check API documentation: http://localhost:8000/docs

## 📝 License

Social Media Pipeline POC - Demo Application

