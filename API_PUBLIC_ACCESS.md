# Public API Access Guide

This guide shows developers how to access and use the Social Media AI Pipeline API from anywhere.

## Base URL

Once deployed to Vercel, your API will be available at:
```
https://your-project.vercel.app
```

Replace `your-project.vercel.app` with your actual Vercel deployment URL.

## Authentication

Currently, the API is configured with `DISABLE_AUTH=true` for easy testing and public access.

**No authentication required** - Anyone can use the API endpoints.

## Quick Start

### 1. Test the API

```bash
# Health check
curl https://your-project.vercel.app/health

# API info
curl https://your-project.vercel.app/api
```

### 2. View Documentation

Visit the interactive API documentation:
```
https://your-project.vercel.app/docs
```

## API Endpoints

### AI Analysis

#### Sentiment Analysis
Analyze the sentiment of any text.

```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/sentiment" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "I absolutely love this product! Best purchase ever!"
     }'
```

**Response:**
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

#### Location Extraction
Extract geographical locations from text.

```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/locations" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "I visited Paris, London, and Tokyo last summer."
     }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "locations": [
      {
        "text": "Paris",
        "label": "GPE",
        "confidence": 0.99
      },
      {
        "text": "London",
        "label": "GPE",
        "confidence": 0.98
      },
      {
        "text": "Tokyo",
        "label": "GPE",
        "confidence": 0.97
      }
    ]
  }
}
```

#### Comprehensive Analysis
Get complete analysis including sentiment, locations, keywords, and entities.

```bash
curl -X POST "https://your-project.vercel.app/api/v1/ai/analyze/comprehensive" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Amazing experience in New York! The restaurant was incredible and the staff were so friendly."
     }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Amazing experience in New York!...",
    "sentiment": {
      "label": "positive",
      "score": 0.92,
      "confidence": 0.95
    },
    "locations": [
      {
        "text": "New York",
        "label": "GPE",
        "confidence": 0.98
      }
    ],
    "keywords": ["amazing", "experience", "incredible", "friendly"],
    "entities": [...],
    "analysis_timestamp": "2024-10-26T00:00:00Z"
  }
}
```

## Frontend Integration

### JavaScript/TypeScript

#### React Example
```javascript
import { useState } from 'react';

const API_BASE_URL = 'https://your-project.vercel.app';

export default function SentimentAnalyzer() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/ai/analyze/comprehensive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error analyzing text:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text to analyze..."
      />
      <button onClick={analyzeSentiment} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      {result && (
        <div>
          <h3>Sentiment: {result.data.sentiment.label}</h3>
          <p>Confidence: {(result.data.sentiment.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}
```

#### Next.js API Route
```javascript
// pages/api/analyze.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { text } = req.body;

  try {
    const response = await fetch('https://your-project.vercel.app/api/v1/ai/analyze/comprehensive', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Analysis failed' });
  }
}
```

### Python

```python
import requests

API_BASE_URL = 'https://your-project.vercel.app'

def analyze_text(text):
    """Analyze text sentiment and extract insights"""
    response = requests.post(
        f'{API_BASE_URL}/api/v1/ai/analyze/comprehensive',
        json={'text': text}
    )
    return response.json()

def extract_locations(text):
    """Extract geographical locations from text"""
    response = requests.post(
        f'{API_BASE_URL}/api/v1/ai/analyze/locations',
        json={'text': text}
    )
    return response.json()

# Usage
result = analyze_text("I love visiting Paris in the spring!")
print(f"Sentiment: {result['data']['sentiment']['label']}")
print(f"Locations: {result['data']['locations']}")
```

### Vue.js

```vue
<template>
  <div>
    <textarea v-model="text" placeholder="Enter text..."></textarea>
    <button @click="analyze" :disabled="loading">
      {{ loading ? 'Analyzing...' : 'Analyze' }}
    </button>
    <div v-if="result">
      <h3>Sentiment: {{ result.data.sentiment.label }}</h3>
      <p>Score: {{ result.data.sentiment.score }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      text: '',
      result: null,
      loading: false,
      apiUrl: 'https://your-project.vercel.app'
    }
  },
  methods: {
    async analyze() {
      this.loading = true;
      try {
        const response = await fetch(`${this.apiUrl}/api/v1/ai/analyze/comprehensive`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: this.text })
        });
        this.result = await response.json();
      } catch (error) {
        console.error('Analysis error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

## Mobile Apps

### React Native

```javascript
import { useState } from 'react';
import { View, TextInput, Button, Text } from 'react-native';

const API_BASE_URL = 'https://your-project.vercel.app';

export default function SentimentScreen() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const analyzeSentiment = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/ai/analyze/sentiment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <View>
      <TextInput
        value={text}
        onChangeText={setText}
        placeholder="Enter text..."
      />
      <Button title="Analyze" onPress={analyzeSentiment} />
      {result && (
        <Text>Sentiment: {result.data.sentiment}</Text>
      )}
    </View>
  );
}
```

### Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://your-project.vercel.app';

  Future<Map<String, dynamic>> analyzeSentiment(String text) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/ai/analyze/sentiment'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to analyze sentiment');
    }
  }
}
```

## Rate Limits

Current rate limits:
- **100 requests per minute** per IP address
- No authentication required
- Free tier limits apply

For higher limits, contact the API administrator.

## CORS Configuration

The API is configured with CORS enabled for all origins:
- ✅ Can be accessed from any website
- ✅ Can be accessed from mobile apps
- ✅ Can be accessed from localhost
- ✅ No CORS errors

## Error Handling

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

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `MODEL_ERROR` | 500 | AI model error |

### Error Handling Example

```javascript
const analyzeText = async (text) => {
  try {
    const response = await fetch('https://your-project.vercel.app/api/v1/ai/analyze/sentiment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error.message);
    // Handle error appropriately
  }
};
```

## Best Practices

1. **Cache Results**: Cache API responses to reduce redundant calls
2. **Batch Requests**: Group multiple analyses when possible
3. **Handle Errors**: Always implement proper error handling
4. **Validate Input**: Validate text input before sending to API
5. **Monitor Usage**: Keep track of your API usage
6. **Use HTTPS**: Always use the HTTPS endpoint

## Example Projects

### Simple Web App

```html
<!DOCTYPE html>
<html>
<head>
    <title>Sentiment Analyzer</title>
</head>
<body>
    <h1>Social Media Sentiment Analyzer</h1>
    <textarea id="text" rows="5" cols="50" placeholder="Enter text..."></textarea>
    <br>
    <button onclick="analyze()">Analyze</button>
    <div id="result"></div>

    <script>
        const API_URL = 'https://your-project.vercel.app';

        async function analyze() {
            const text = document.getElementById('text').value;

            try {
                const response = await fetch(`${API_URL}/api/v1/ai/analyze/comprehensive`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text })
                });

                const data = await response.json();

                document.getElementById('result').innerHTML = `
                    <h2>Results:</h2>
                    <p><strong>Sentiment:</strong> ${data.data.sentiment.label}</p>
                    <p><strong>Confidence:</strong> ${(data.data.sentiment.confidence * 100).toFixed(2)}%</p>
                    <p><strong>Locations:</strong> ${data.data.locations.map(l => l.text).join(', ') || 'None'}</p>
                `;
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('result').innerHTML = '<p style="color: red;">Error analyzing text</p>';
            }
        }
    </script>
</body>
</html>
```

## Support

- **API Documentation**: `https://your-project.vercel.app/docs`
- **Health Status**: `https://your-project.vercel.app/health`
- **GitHub Issues**: Report bugs and request features

## Updates and Changes

The API is continuously improved. Check the changelog for updates:
- Monitor the GitHub repository for changes
- Subscribe to notifications
- Review deployment updates in Vercel

---

**Happy Coding!** 🚀

Start using the API today and build amazing applications with AI-powered sentiment analysis and location extraction.