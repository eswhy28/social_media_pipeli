# API Testing Guide - Social Media AI Pipeline

**API Base URL:** `http://35.239.75.255:8000`

This guide will help you test all the API endpoints for the Social Media AI Pipeline.

---

## Table of Contents
- [Getting Started](#getting-started)
- [Testing Methods](#testing-methods)
- [API Endpoints](#api-endpoints)
- [Sample Test Cases](#sample-test-cases)
- [Expected Results](#expected-results)
- [Reporting Issues](#reporting-issues)

---

## Getting Started

### What You Need
- A tool to test APIs (choose one):
  - **Postman** (Recommended - Download from [postman.com](https://postman.com))
  - **Thunder Client** (VS Code Extension)
  - **cURL** (Command line)
  - **Browser** (for GET requests only)

### Base URL
All API requests should use this base URL:
```
http://35.239.75.255:8000
```

---

## Testing Methods

### Method 1: Using Postman (Recommended)

1. **Download Postman**: [postman.com/downloads](https://postman.com/downloads)
2. **Create a new request**
3. **Set the request type** (GET, POST, etc.)
4. **Enter the full URL** (e.g., `http://35.239.75.255:8000/health`)
5. **For POST requests**:
   - Go to "Body" tab
   - Select "raw"
   - Choose "JSON" from dropdown
   - Paste the JSON data
6. **Click Send**

### Method 2: Using cURL (Command Line)

Open terminal/command prompt and run the cURL commands provided below.

### Method 3: Using Browser

Only for GET requests - paste the URL directly in your browser.

---

## API Endpoints

### 1. Health Check ✅
**Purpose:** Check if the API is running

**Method:** GET
**URL:** `http://35.239.75.255:8000/health`

**Postman:**
- Method: GET
- URL: `http://35.239.75.255:8000/health`

**cURL:**
```bash
curl http://35.239.75.255:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "2.0.0",
  "database": "SQLite",
  "cache": "Redis"
}
```

---

### 2. API Documentation 📚
**Purpose:** View interactive API documentation

**Method:** Browser
**URL:** `http://35.239.75.255:8000/docs`

**Instructions:**
- Open your browser
- Go to: `http://35.239.75.255:8000/docs`
- You'll see interactive documentation where you can test all endpoints

---

### 3. Sentiment Analysis 😊😐😢
**Purpose:** Analyze if text is positive, negative, or neutral

**Method:** POST
**URL:** `http://35.239.75.255:8000/api/v1/ai/analyze/sentiment`

**Postman:**
- Method: POST
- URL: `http://35.239.75.255:8000/api/v1/ai/analyze/sentiment`
- Body (JSON):
```json
{
  "text": "Super Eagles beat South Africa 2-1! Osimhen scores brace ⚽ #SuperEagles"
}
```

**cURL:**
```bash
curl -X POST "http://35.239.75.255:8000/api/v1/ai/analyze/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Super Eagles beat South Africa 2-1! Osimhen scores brace ⚽ #SuperEagles"}'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "score": 0.95,
    "confidence": 0.98,
    "model": "roberta"
  }
}
```

**Test Cases to Try:**
1. Positive text: "Super Eagles beat South Africa 2-1! Osimhen scores brace ⚽ #SuperEagles"
2. Negative text: "Naira crashes to ₦1,700 per dollar at black market. This is terrible! #NigerianEconomy"
3. Neutral text: "JAMB announces dates for 2026 UTME registration #Nigeria #JAMB"

---

### 4. Location Extraction 🌍
**Purpose:** Extract geographical locations from text

**Method:** POST
**URL:** `http://35.239.75.255:8000/api/v1/ai/analyze/locations`

**Postman:**
- Method: POST
- URL: `http://35.239.75.255:8000/api/v1/ai/analyze/locations`
- Body (JSON):
```json
{
  "text": "Our offices are in Lagos, Abuja, Port Harcourt, and Kano. We also operate in Ghana and Kenya."
}
```

**cURL:**
```bash
curl -X POST "http://35.239.75.255:8000/api/v1/ai/analyze/locations" \
  -H "Content-Type: application/json" \
  -d '{"text": "Our offices are in Lagos, Abuja, Port Harcourt, and Kano. We also operate in Ghana and Kenya."}'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "locations": [
      {
        "text": "Lagos",
        "label": "GPE",
        "confidence": 0.99
      },
      {
        "text": "Abuja",
        "label": "GPE",
        "confidence": 0.98
      },
      {
        "text": "Port Harcourt",
        "label": "GPE",
        "confidence": 0.97
      },
      {
        "text": "Kano",
        "label": "GPE",
        "confidence": 0.96
      }
    ]
  }
}
```

**Test Cases to Try:**
1. "Meeting in Lagos and Abuja tomorrow to discuss economic policies"
2. "Our company has offices in Lagos, Abuja, Port Harcourt, and Kano"
3. "Traveling from Ibadan to Enugu via Benin City"

---

### 5. Comprehensive Analysis 🔍
**Purpose:** Get complete analysis (sentiment + locations + keywords + entities)

**Method:** POST
**URL:** `http://35.239.75.255:8000/api/v1/ai/analyze/comprehensive`

**Postman:**
- Method: POST
- URL: `http://35.239.75.255:8000/api/v1/ai/analyze/comprehensive`
- Body (JSON):
```json
{
  "text": "President Tinubu announced new economic policies in Lagos yesterday. Nigerian citizens react positively to infrastructure investments across Africa."
}
```

**cURL:**
```bash
curl -X POST "http://35.239.75.255:8000/api/v1/ai/analyze/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{"text": "President Tinubu announced new economic policies in Lagos yesterday. Nigerian citizens react positively to infrastructure investments across Africa."}'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "text": "President Tinubu announced...",
    "sentiment": {
      "label": "positive",
      "score": 0.85,
      "confidence": 0.92
    },
    "locations": [
      {
        "text": "Lagos",
        "label": "GPE",
        "confidence": 0.99
      },
      {
        "text": "Africa",
        "label": "LOC",
        "confidence": 0.95
      }
    ],
    "keywords": ["economic", "policies", "infrastructure", "investments"],
    "entities": [...],
    "analysis_timestamp": "2025-10-26T00:00:00Z"
  }
}
```

---

### 6. Get Social Media Posts 📱
**Purpose:** Retrieve stored social media posts

**Method:** GET
**URL:** `http://35.239.75.255:8000/api/v1/data/posts?skip=0&limit=10`

**Postman:**
- Method: GET
- URL: `http://35.239.75.255:8000/api/v1/data/posts?skip=0&limit=10`

**cURL:**
```bash
curl "http://35.239.75.255:8000/api/v1/data/posts?skip=0&limit=10"
```

**Browser:**
Open: `http://35.239.75.255:8000/api/v1/data/posts?skip=0&limit=10`

---

### 7. Create Social Media Post 📝
**Purpose:** Add a new social media post

**Method:** POST
**URL:** `http://35.239.75.255:8000/api/v1/data/posts`

**Postman:**
- Method: POST
- URL: `http://35.239.75.255:8000/api/v1/data/posts`
- Body (JSON):
```json
{
  "platform": "twitter",
  "content": "Testing the API from Lagos! #Nigeria #Tech",
  "author": "test_user",
  "post_url": "https://twitter.com/test_user/status/123456"
}
```

**cURL:**
```bash
curl -X POST "http://35.239.75.255:8000/api/v1/data/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "content": "Testing the API from Lagos! #Nigeria #Tech",
    "author": "test_user",
    "post_url": "https://twitter.com/test_user/status/123456"
  }'
```

---

### 8. Get Analytics 📊
**Purpose:** Get analytics and statistics

**Method:** GET
**URL:** `http://35.239.75.255:8000/api/v1/data/analytics`

**Postman:**
- Method: GET
- URL: `http://35.239.75.255:8000/api/v1/data/analytics`

**cURL:**
```bash
curl "http://35.239.75.255:8000/api/v1/data/analytics"
```

**Browser:**
Open: `http://35.239.75.255:8000/api/v1/data/analytics`

---

### 9. AI Models Information ℹ️
**Purpose:** Check loaded AI models and their status

**Method:** GET
**URL:** `http://35.239.75.255:8000/api/v1/ai/models/info`

**Postman:**
- Method: GET
- URL: `http://35.239.75.255:8000/api/v1/ai/models/info`

**cURL:**
```bash
curl "http://35.239.75.255:8000/api/v1/ai/models/info"
```

**Browser:**
Open: `http://35.239.75.255:8000/api/v1/ai/models/info`

---

## Sample Test Cases

### Test Case 1: Sports - Positive Sentiment
```json
{
  "text": "Victor Osimhen wins African Footballer of the Year award 🏆 Amazing achievement for Nigeria! #Nigeria #Osimhen"
}
```
**Expected:** Sentiment = positive, High confidence, Location = Nigeria

---

### Test Case 2: Economy - Negative Sentiment
```json
{
  "text": "Fuel price increases to ₦650 per liter in major cities. This is really bad for businesses! #FuelPrice #Nigeria"
}
```
**Expected:** Sentiment = negative, High confidence, Location = Nigeria

---

### Test Case 3: Entertainment - Positive with Locations
```json
{
  "text": "Burna Boy's concert in Lagos was incredible! Performing at O2 Arena London next month 🎵 #BurnaBoy #Afrobeats"
}
```
**Expected:** Positive sentiment, Locations = Lagos & London

---

### Test Case 4: Politics - Multiple Locations
```json
{
  "text": "President Tinubu announces new cabinet reshuffle. Ministers from Lagos, Kano, Rivers, and Ogun states appointed #Nigeria #Tinubu"
}
```
**Expected:** Multiple locations (Lagos, Kano, Rivers, Ogun, Nigeria), Political keywords

---

### Test Case 5: Technology - Neutral to Positive
```json
{
  "text": "Flutterwave raises $250M in Series D funding round. Nigerian fintech continues to attract global investors #Nigeria #Fintech"
}
```
**Expected:** Positive sentiment, Location = Nigeria, Tech keywords

---

### Test Case 6: Social Issues - Mixed Sentiment
```json
{
  "text": "Lagos traffic: Residents spend average 4 hours daily in gridlock. Government promises solutions soon #Lagos #Traffic"
}
```
**Expected:** Negative/Neutral sentiment, Location = Lagos

---

### Test Case 7: Health - Positive News
```json
{
  "text": "Nigeria records zero polio cases for 4th consecutive year 🎉 Great achievement for healthcare! #Nigeria #Health"
}
```
**Expected:** Positive sentiment, Location = Nigeria, Health keywords

---

### Test Case 8: Empty Text (Error Test)
```json
{
  "text": ""
}
```
**Expected:** Error response - validation error

---

## Expected Results

### Success Response Format
```json
{
  "success": true,
  "data": {
    // Response data here
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

---

## Reporting Issues

When reporting issues, please include:

1. **Endpoint tested:** (e.g., `/api/v1/ai/analyze/sentiment`)
2. **Request method:** (GET, POST, etc.)
3. **Request body:** (if POST request)
4. **Expected result:** What you expected to happen
5. **Actual result:** What actually happened
6. **Error message:** Any error messages received
7. **Screenshot:** If possible

**Report to:** [Your Contact Information]

---

## Quick Reference - All Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/v1/ai/analyze/sentiment` | POST | Sentiment analysis |
| `/api/v1/ai/analyze/locations` | POST | Location extraction |
| `/api/v1/ai/analyze/comprehensive` | POST | Complete analysis |
| `/api/v1/data/posts` | GET | Get posts |
| `/api/v1/data/posts` | POST | Create post |
| `/api/v1/data/analytics` | GET | Get analytics |
| `/api/v1/ai/models/info` | GET | AI models info |

---

## Need Help?

- **Interactive Docs:** http://35.239.75.255:8000/docs
- **Health Check:** http://35.239.75.255:8000/health

---

**Happy Testing! 🚀**