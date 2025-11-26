#!/bin/bash
# Post-Fix Verification Checklist

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           Post-Fix Verification Checklist                             ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check 1: Docker container running
echo "1. Checking Docker container..."
if docker ps --format '{{.Names}}' | grep -q "^postgres$"; then
    echo -e "   ${GREEN}✓${NC} PostgreSQL container is running"
else
    echo -e "   ${RED}✗${NC} PostgreSQL container not found"
    exit 1
fi

# Check 2: Database exists
echo "2. Checking database..."
DB_EXISTS=$(docker exec postgres psql -U sa -d mydb -tAc "SELECT 1 FROM pg_database WHERE datname='social_media_pipeline'" 2>/dev/null)
if [ "$DB_EXISTS" = "1" ]; then
    echo -e "   ${GREEN}✓${NC} Database 'social_media_pipeline' exists"
else
    echo -e "   ${RED}✗${NC} Database 'social_media_pipeline' not found"
    exit 1
fi

# Check 3: Alembic migrations status
echo "3. Checking Alembic migrations..."
if command -v alembic &> /dev/null; then
    CURRENT=$(alembic current 2>&1)
    if echo "$CURRENT" | grep -q "003"; then
        echo -e "   ${GREEN}✓${NC} Alembic at latest version (003)"
    elif echo "$CURRENT" | grep -q "head"; then
        echo -e "   ${GREEN}✓${NC} Alembic at head"
    else
        echo -e "   ${YELLOW}⚠${NC} Alembic may need to be upgraded"
        echo "   Run: alembic upgrade head"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Alembic not found in PATH"
fi

# Check 4: Tables exist
echo "4. Checking database tables..."
TABLE_COUNT=$(docker exec postgres psql -U sa -d social_media_pipeline -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null)
if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -ge 10 ]; then
    echo -e "   ${GREEN}✓${NC} Found $TABLE_COUNT tables (expected 14+)"
elif [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠${NC} Found only $TABLE_COUNT tables (expected 14)"
    echo "   You may need to run: alembic upgrade head"
else
    echo -e "   ${RED}✗${NC} No tables found"
    echo "   Run: python scripts/complete_setup.py"
    exit 1
fi

# Check 5: Data exists
echo "5. Checking for data..."
DATA_COUNT=$(docker exec postgres psql -U sa -d social_media_pipeline -tAc "SELECT COUNT(*) FROM apify_scraped_data" 2>/dev/null)
if [ -n "$DATA_COUNT" ] && [ "$DATA_COUNT" -gt 0 ]; then
    echo -e "   ${GREEN}✓${NC} Found $DATA_COUNT records in apify_scraped_data"
else
    echo -e "   ${YELLOW}⚠${NC} No data in database"
    echo "   Import data: python scripts/import_data.py"
fi

# Check 6: Virtual environment
echo "6. Checking virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "   ${GREEN}✓${NC} Virtual environment is activated"
else
    echo -e "   ${YELLOW}⚠${NC} Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
fi

# Check 7: Required packages
echo "7. Checking Python packages..."
if python -c "import fastapi, sqlalchemy, alembic" 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Core packages installed"
else
    echo -e "   ${RED}✗${NC} Some packages missing"
    echo "   Run: pip install -r requirements.txt"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                       Verification Complete                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. If any checks failed, run: python scripts/complete_setup.py"
echo "  2. Start the application: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  3. Test: curl http://localhost:8000/health"
echo ""

