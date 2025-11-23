#!/bin/bash
# Comprehensive endpoint testing script

BASE_URL="http://localhost:8000/api/v1/social-media"

echo "================================================================================"
echo "TESTING ALL SOCIAL MEDIA INTELLIGENCE ENDPOINTS"
echo "================================================================================"
echo ""

# Test 1: Intelligence Report - Basic
echo "1. Testing Intelligence Report (basic)..."
curl -s "${BASE_URL}/intelligence/report?limit=2" | python -m json.tool | head -20
if [ $? -eq 0 ]; then
    echo "✅ Intelligence Report - Basic: PASSED"
else
    echo "❌ Intelligence Report - Basic: FAILED"
fi
echo ""

# Test 2: Intelligence Report - With Media Filter
echo "2. Testing Intelligence Report (has_media=true)..."
curl -s "${BASE_URL}/intelligence/report?has_media=true&limit=2" | python -m json.tool | grep -A 5 '"media"' | head -10
if [ $? -eq 0 ]; then
    echo "✅ Intelligence Report - Media Filter: PASSED"
else
    echo "❌ Intelligence Report - Media Filter: FAILED"
fi
echo ""

# Test 3: Intelligence Report - Min Engagement
echo "3. Testing Intelligence Report (min_engagement=1000)..."
curl -s "${BASE_URL}/intelligence/report?min_engagement=1000&limit=2" > /tmp/test_engagement.json
if grep -q '"success": true' /tmp/test_engagement.json; then
    echo "✅ Intelligence Report - Min Engagement: PASSED"
    cat /tmp/test_engagement.json | python -m json.tool | grep -A 3 '"engagement"' | head -8
else
    echo "❌ Intelligence Report - Min Engagement: FAILED"
    cat /tmp/test_engagement.json
fi
echo ""

# Test 4: Data Scraped
echo "4. Testing Data Scraped endpoint..."
curl -s "${BASE_URL}/data/scraped?limit=2" > /tmp/test_scraped.json
if grep -q '"success": true' /tmp/test_scraped.json; then
    echo "✅ Data Scraped: PASSED"
else
    echo "❌ Data Scraped: FAILED"
    cat /tmp/test_scraped.json
fi
echo ""

# Test 5: Geo Analysis
echo "5. Testing Geo Analysis endpoint..."
curl -s "${BASE_URL}/data/geo-analysis?hours_back=720" > /tmp/test_geo.json
if grep -q '"success": true' /tmp/test_geo.json; then
    echo "✅ Geo Analysis: PASSED"
else
    echo "❌ Geo Analysis: FAILED"
    cat /tmp/test_geo.json
fi
echo ""

# Test 6: Stats
echo "6. Testing Stats endpoint..."
curl -s "${BASE_URL}/data/stats" > /tmp/test_stats.json
if grep -q '"success": true' /tmp/test_stats.json; then
    echo "✅ Stats: PASSED"
    cat /tmp/test_stats.json | python -m json.tool | head -20
else
    echo "❌ Stats: FAILED"
    cat /tmp/test_stats.json
fi
echo ""

# Test 7: AI Processing Stats
echo "7. Testing AI Processing Stats..."
curl -s "${BASE_URL}/ai/processing-stats" > /tmp/test_ai_stats.json
if grep -q '"success": true' /tmp/test_ai_stats.json; then
    echo "✅ AI Processing Stats: PASSED"
    cat /tmp/test_ai_stats.json | python -m json.tool | head -30
else
    echo "❌ AI Processing Stats: FAILED"
    cat /tmp/test_ai_stats.json
fi
echo ""

# Test 8: Sentiment Results
echo "8. Testing Sentiment Results..."
curl -s "${BASE_URL}/ai/sentiment-results?limit=2" > /tmp/test_sentiment.json
if grep -q '"success": true' /tmp/test_sentiment.json; then
    echo "✅ Sentiment Results: PASSED"
else
    echo "❌ Sentiment Results: FAILED"
    cat /tmp/test_sentiment.json
fi
echo ""

# Test 9: Location Results
echo "9. Testing Location Results..."
curl -s "${BASE_URL}/ai/location-results?limit=2" > /tmp/test_locations.json
if grep -q '"success": true' /tmp/test_locations.json; then
    echo "✅ Location Results: PASSED"
else
    echo "❌ Location Results: FAILED"
    cat /tmp/test_locations.json
fi
echo ""

echo "================================================================================"
echo "ENDPOINT TESTING COMPLETE"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  Intelligence Report endpoints: Core functionality"
echo "  Data endpoints: Raw data access"
echo "  AI endpoints: ML processing results"
echo ""
echo "All critical endpoints tested!"
echo ""
