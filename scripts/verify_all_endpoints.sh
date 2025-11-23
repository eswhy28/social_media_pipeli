#!/bin/bash
echo "=== COMPREHENSIVE ENDPOINT VERIFICATION ==="
echo ""

PASSED=0
TOTAL=0

test_endpoint() {
    NAME="$1"
    URL="$2"
    TOTAL=$((TOTAL + 1))
    
    RESULT=$(curl -s "$URL")
    if echo "$RESULT" | grep -q '"success": true'; then
        echo "✅ $NAME"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo "❌ $NAME"
        return 1
    fi
}

BASE="http://localhost:8000/api/v1/social-media"

echo "PRIMARY ENDPOINTS:"
test_endpoint "Intelligence Report" "$BASE/intelligence/report?limit=2"
test_endpoint "Intelligence (Media)" "$BASE/intelligence/report?has_media=true&limit=2"
test_endpoint "Intelligence (Engagement)" "$BASE/intelligence/report?min_engagement=500&limit=2"
echo ""

echo "DATA ENDPOINTS:"
test_endpoint "Data Scraped" "$BASE/data/scraped?limit=2"
test_endpoint "Geo Analysis" "$BASE/data/geo-analysis"
test_endpoint "Engagement Analysis" "$BASE/data/engagement-analysis"
test_endpoint "Statistics" "$BASE/data/stats"
echo ""

echo "AI ENDPOINTS:"
test_endpoint "AI Processing Stats" "$BASE/ai/processing-stats"
test_endpoint "Sentiment Results" "$BASE/ai/sentiment-results?limit=2"
test_endpoint "Location Results" "$BASE/ai/location-results?limit=2"
echo ""

echo "=== RESULTS: $PASSED/$TOTAL endpoints working ==="

if [ $PASSED -eq $TOTAL ]; then
    echo "🎉 ALL ENDPOINTS WORKING PERFECTLY!"
else
    echo "⚠️  Some endpoints may need attention"
fi
