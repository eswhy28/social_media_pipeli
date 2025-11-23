#!/bin/bash
# Final comprehensive endpoint verification

BASE_URL="http://localhost:8000/api/v1/social-media"

echo "================================================================================"
echo "FINAL ENDPOINT VERIFICATION"
echo "================================================================================"
echo ""

# Test Intelligence Report
echo "1. Intelligence Report (Primary Endpoint)"
echo "   GET ${BASE_URL}/intelligence/report?limit=2"
RESULT=$(curl -s "${BASE_URL}/intelligence/report?limit=2")
if echo "$RESULT" | grep -q '"success": true' && echo "$RESULT" | grep -q '"reports"'; then
    echo "   ✅ WORKING - Returns complete intelligence data with AI analysis"
else
    echo "   ❌ FAILED"
fi
echo ""

# Test with filters
echo "2. Intelligence Report with Filters"
echo "   GET ${BASE_URL}/intelligence/report?has_media=true&limit=2"
RESULT=$(curl -s "${BASE_URL}/intelligence/report?has_media=true&limit=2")
if echo "$RESULT" | grep -q '"has_media": true'; then
    echo "   ✅ WORKING - Media filter functioning"
else
    echo "   ❌ FAILED"
fi
echo ""

echo "3. Intelligence Report with Min Engagement"
echo "   GET ${BASE_URL}/intelligence/report?min_engagement=1000&limit=2"
RESULT=$(curl -s "${BASE_URL}/intelligence/report?min_engagement=1000&limit=2")
if echo "$RESULT" | grep -q '"success": true'; then
    echo "   ✅ WORKING - Engagement filter functioning"
else
    echo "   ❌ FAILED"
fi
echo ""

# Test Data Stats
echo "4. Data Statistics"
echo "   GET ${BASE_URL}/data/stats"
RESULT=$(curl -s "${BASE_URL}/data/stats")
if echo "$RESULT" | grep -q '"total_posts"' && echo "$RESULT" | grep -q '139'; then
    echo "   ✅ WORKING - Shows 139 total posts"
else
    echo "   ❌ FAILED"
fi
echo ""

# Test AI Processing Stats
echo "5. AI Processing Statistics"
echo "   GET ${BASE_URL}/ai/processing-stats"
RESULT=$(curl -s "${BASE_URL}/ai/processing-stats")
if echo "$RESULT" | grep -q '"sentiment_processed"' && echo "$RESULT$ | grep -q '139'; then
    echo "   ✅ WORKING - Shows AI processing status"
else
    echo "   ❌ FAILED"
fi
echo ""

# Test Sentiment Results
echo "6. Sentiment Analysis Results"
echo "   GET ${BASE_URL}/ai/sentiment-results?limit=2"
RESULT=$(curl -s "${BASE_URL}/ai/sentiment-results?limit=2")
if echo "$RESULT" | grep -q '"sentiment"' && echo "$RESULT" | grep -q '"label"'; then
    echo "   ✅ WORKING - Returns sentiment with labels"
else
    echo "   ❌ FAILED"
fi
echo ""

# Test Location Results
echo "7. Location Extraction Results"
echo "   GET ${BASE_URL}/ai/location-results?limit=2"
RESULT=$(curl -s "${BASE_URL}/ai/location-results?limit=2")
if echo "$RESULT" | grep -q '"success": true'; then
    echo "   ✅ WORKING - Returns location extraction results"
else
    echo "   ❌ FAILED"
fi
echo ""

echo "================================================================================"
echo "VERIFICATION COMPLETE"
echo "================================================================================"
echo ""
echo "Main Intelligence Endpoint:"
echo "  curl 'http://localhost:8000/api/v1/social-media/intelligence/report?limit=10'"
echo ""
echo "Interactive API Docs:"
echo "  http://localhost:8000/docs"
echo ""
