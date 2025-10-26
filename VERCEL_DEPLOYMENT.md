# Vercel Deployment Guide - Social Media AI Pipeline

Complete guide for deploying the Social Media AI Pipeline to Vercel with publicly accessible APIs.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Deploy](#quick-deploy)
- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [API Endpoints](#api-endpoints)
- [Testing Your Deployment](#testing-your-deployment)
- [Troubleshooting](#troubleshooting)
- [Cost Considerations](#cost-considerations)

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Repository must be pushed to GitHub
3. **Hugging Face Token**: Get your token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## Quick Deploy

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   Add these in the Vercel dashboard under "Settings" → "Environment Variables":

   **Required Variables:**
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `your-generated-secret-key-here`
   - `HUGGINGFACE_TOKEN` = `hf_your_token_here`
   - `DATABASE_URL` = `sqlite+aiosqlite:///./social_media.db`
   - `DISABLE_AUTH` = `true`
   - `API_V1_PREFIX` = `/api/v1`

   **Important:** Make sure to add these variables to the "Production" environment

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (3-5 minutes)
   - Your API will be live!

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add ENVIRONMENT production
   vercel env add SECRET_KEY your-secret-key
   vercel env add HUGGINGFACE_TOKEN hf_your_token
   vercel env add DATABASE_URL sqlite+aiosqlite:///./data/social_media.db
   vercel env add DISABLE_AUTH true
   ```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `SECRET_KEY` | JWT secret key (generate with `openssl rand -hex 32`) | `a3f5...` |
| `HUGGINGFACE_TOKEN` | Hugging Face API token | `hf_xxx...` |
| `DATABASE_URL` | Database connection URL | `sqlite+aiosqlite:///./data/social_media.db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISABLE_AUTH` | Disable authentication for testing | `true` |
| `REDIS_HOST` | Redis host (for caching) | `localhost` |
| `REDIS_PASSWORD` | Redis password | None |
| `LOG_LEVEL` | Logging level | `INFO` |

### Generating a Secret Key

```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

## Database Configuration

### SQLite (Default - Simple Setup)

The default configuration uses SQLite, which works well for testing and small deployments:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/social_media.db
```

**Pros:**
- Zero configuration
- No external dependencies
- Perfect for testing

**Cons:**
- Data resets on each deployment
- Not suitable for production with persistent data

### PostgreSQL (Production Recommended)

For production with persistent data, use a PostgreSQL database:

1. **Create a PostgreSQL database** (options):
   - [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (easiest)
   - [Supabase](https://supabase.com) (generous free tier)
   - [Neon](https://neon.tech) (serverless PostgreSQL)

2. **Update DATABASE_URL**:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
   ```

3. **Install PostgreSQL adapter**:
   Add to `requirements.txt`:
   ```
   asyncpg>=0.27.0
   ```

## API Endpoints

Once deployed, your API will be available at: `https://your-project.vercel.app`

### Core Endpoints

#### 1. Health Check
```bash
curl https://your-project.vercel.app/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "2.0.0",
  "platform": "Vercel"
}
```

#### 2. API Documentation
```
https://your-project.vercel.app/docs
```
Interactive Swagger UI documentation

#### 3. Sentiment Analysis
```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this product! It works great!"}'
```

#### 4. Location Extraction
```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/locations" \
     -H "Content-Type: application/json" \
     -d '{"text": "Meeting in New York and Los Angeles next week."}'
```

#### 5. Comprehensive Analysis
```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/comprehensive" \
     -H "Content-Type: application/json" \
     -d '{"text": "Amazing experience in Paris! The food was incredible."}'
```

### Public API Access

The API is configured with CORS enabled for all origins (`*`), meaning:
- ✅ Anyone can access the API
- ✅ Works from any website/frontend
- ✅ No authentication required (for testing)
- ✅ Perfect for demos and prototypes

### Frontend Integration Example

```javascript
// React/Next.js Example
const analyzeText = async (text) => {
  const response = await fetch('https://your-project.vercel.app/api/v1/ai/analyze/comprehensive', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text })
  });

  const data = await response.json();
  return data;
};

// Usage
const result = await analyzeText("I love this product!");
console.log(result);
```

## Testing Your Deployment

### 1. Basic Health Check
```bash
curl https://your-project.vercel.app/health
```

### 2. API Information
```bash
curl https://your-project.vercel.app/api
```

### 3. Test AI Analysis
```bash
# Test sentiment analysis
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text": "This is amazing!"}'

# Test comprehensive analysis
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/comprehensive" \
     -H "Content-Type: application/json" \
     -d '{"text": "Great experience in Tokyo and Seoul!"}'
```

### 4. Check API Documentation
Open in browser:
```
https://your-project.vercel.app/docs
```

## Troubleshooting

### Build Failures

**Issue**: Python version mismatch
```bash
# Add runtime.txt to specify Python version
echo "python-3.11" > runtime.txt
```

**Issue**: Missing dependencies
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt
```

### Timeout Errors

**Issue**: Function timeout (default 10s)
- Solution: Configured in `vercel.json` with `maxDuration: 60`
- Hobby plan: max 60s
- Pro plan: max 300s

### Memory Issues

**Issue**: Out of memory errors
- Solution: Configured in `vercel.json` with `memory: 3008` (max)
- Consider using smaller AI models or optimizing model loading

### Database Connection Issues

**Issue**: SQLite database resets
- Solution: Use PostgreSQL for persistent storage (see Database Configuration)

**Issue**: Database locked errors
- Solution: SQLite has limited concurrency, use PostgreSQL for production

### CORS Issues

**Issue**: CORS errors from frontend
- Check: `api/index.py` has CORS middleware configured
- Verify: `allow_origins=["*"]` is set

## Cost Considerations

### Vercel Pricing

**Hobby Plan (Free)**
- ✅ Perfect for this project
- 100 GB bandwidth/month
- 100 hours serverless function execution/month
- 6,000 serverless function invocations/day
- 60 second max function duration

**Pro Plan ($20/month)**
- 1 TB bandwidth/month
- 1,000 hours execution/month
- 300 second max function duration
- Better for production workloads

### External Services (Free Tiers)

**Database Options:**
- **Vercel Postgres**: Free tier available
- **Supabase**: 500 MB database, 1 GB file storage
- **Neon**: 3 GB storage, 1 compute unit

**Redis (Optional):**
- **Upstash**: 10,000 commands/day free
- **Redis Labs**: 30 MB free

**AI Models:**
- **Hugging Face**: Free inference API (rate limited)
- Models cached on first request

## Production Checklist

Before going to production:

- [ ] Generate strong `SECRET_KEY`
- [ ] Set `DISABLE_AUTH=false` and implement authentication
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure Redis for caching
- [ ] Set up monitoring (Vercel Analytics)
- [ ] Configure custom domain
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Review and adjust CORS origins
- [ ] Implement rate limiting per user
- [ ] Set up database backups
- [ ] Configure environment-specific variables
- [ ] Test all endpoints thoroughly
- [ ] Document API for users

## Monitoring and Logs

### View Deployment Logs

1. **Via Dashboard**:
   - Go to your project in Vercel dashboard
   - Click on "Deployments"
   - Click on a deployment
   - View "Build Logs" and "Function Logs"

2. **Via CLI**:
   ```bash
   vercel logs your-project-name
   ```

### Monitor Performance

- **Vercel Analytics**: Built-in analytics for free
- **Custom Metrics**: Use services like Sentry, DataDog, etc.

## Continuous Deployment

Vercel automatically deploys when you push to your GitHub repository:

```bash
# Make changes
git add .
git commit -m "Update API endpoints"
git push origin main

# Vercel automatically deploys
# Watch progress at https://vercel.com/dashboard
```

## Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **API Documentation**: `https://your-project.vercel.app/docs`
- **Vercel Support**: [vercel.com/support](https://vercel.com/support)

## Next Steps

1. **Deploy and Test**: Follow the Quick Deploy steps
2. **Share Your API**: Give your Vercel URL to frontend developers
3. **Monitor Usage**: Check Vercel dashboard for usage metrics
4. **Iterate**: Update code and push to trigger auto-deployment
5. **Scale**: Upgrade to Pro plan when needed

---

Your API is now accessible worldwide! 🚀

**Example API URL**: `https://social-media-ai.vercel.app`

Share this URL with anyone who needs to access your API endpoints.