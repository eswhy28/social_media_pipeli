# Hugging Face Spaces Deployment Guide

## Quick Deployment Steps

### 1. Access Your Space
- Go to: https://huggingface.co/spaces/eswhy28/social_media_pipeline
- Click "Files and versions" tab

### 2. Upload Key Files
Upload these files to your HF Space (drag & drop or use Git):

#### Required Files:
- `app.py` - Entry point for HF Spaces
- `Dockerfile` - Container configuration 
- `requirements-hf.txt` - Dependencies
- `.env` - Environment variables with HUGGINGFACE_TOKEN
- `README.md` - Documentation

#### Application Code:
- `app/` folder (entire directory)
- `scripts/` folder
- Any other Python files needed

### 3. Environment Variables (Alternative to .env)
In your HF Space settings, you can also set:
```
HUGGINGFACE_TOKEN=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
SECRET_KEY=your-secret-key-change-in-production-hf-spaces-2024
DATABASE_URL=sqlite:///./data/social_media.db
```

### 4. Build Configuration
- Space Type: Docker
- Dockerfile: `Dockerfile` (default)
- Port: 7860 (HF Spaces standard)

## API Endpoints Available

Once deployed, your API will be accessible at:
`https://eswhy28-social-media-pipeline.hf.space`

### Main Endpoints:
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check
- `POST /api/v1/ai/analyze/sentiment` - Sentiment analysis
- `POST /api/v1/ai/analyze/locations` - Location extraction  
- `POST /api/v1/ai/analyze/comprehensive` - Complete analysis
- `GET /api/v1/ai/models/info` - Model information

### Example API Call:
```bash
curl -X POST "https://eswhy28-social-media-pipeline.hf.space/api/v1/ai/analyze/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this product! It works amazing in New York."}'
```

## Frontend Integration

Your frontend team can consume the API directly:
```javascript
const response = await fetch('https://eswhy28-social-media-pipeline.hf.space/api/v1/ai/analyze/comprehensive', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Your text to analyze here'
  })
});

const result = await response.json();
console.log(result);
```

## Troubleshooting

### If Build Fails:
1. Check build logs in HF Spaces
2. Ensure all files are uploaded
3. Verify .env file contains HUGGINGFACE_TOKEN
4. Check Dockerfile syntax

### If Models Don't Load:
1. Verify HUGGINGFACE_TOKEN is valid
2. Check model cache permissions
3. Monitor memory usage (models are large)

### Expected Build Time:
- Initial build: 10-15 minutes (downloading models)
- Subsequent builds: 3-5 minutes (cached models)

## Status Check
Once deployed, check these endpoints:
- `GET /health` - Should return 200 OK
- `GET /docs` - Should show interactive API docs  
- `GET /api/v1/ai/models/info` - Should show loaded models

Your API will be ready for frontend consumption!