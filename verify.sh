#!/bin/bash

# System Verification Script - Checks if everything is properly installed

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}  SOCIAL MEDIA PIPELINE - SYSTEM VERIFICATION${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

ISSUES=0

# Check Python
echo -e "${YELLOW}🐍 Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "   ${GREEN}✅ Python $VERSION installed${NC}"
else
    echo -e "   ${RED}❌ Python not found${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check Virtual Environment
echo -e "${YELLOW}📦 Checking Virtual Environment...${NC}"
if [ -d "venv" ]; then
    echo -e "   ${GREEN}✅ Virtual environment exists${NC}"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "   ${GREEN}✅ Virtual environment activated${NC}"
    fi
else
    echo -e "   ${RED}❌ Virtual environment not found${NC}"
    echo -e "   ${YELLOW}Run: ./setup.sh${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check Dependencies
echo -e "${YELLOW}📚 Checking Dependencies...${NC}"
DEPS=("fastapi" "uvicorn" "sqlalchemy" "celery" "redis" "tweepy" "textblob" "pytest")
for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "   ${GREEN}✅ $dep${NC}"
    else
        echo -e "   ${RED}❌ $dep not installed${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check Redis
echo -e "${YELLOW}💾 Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null 2>&1; then
        VERSION=$(redis-cli --version | awk '{print $2}')
        echo -e "   ${GREEN}✅ Redis $VERSION running${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Redis installed but not running${NC}"
        echo -e "   ${YELLOW}Start with: redis-server --daemonize yes${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "   ${RED}❌ Redis not found${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check Database
echo -e "${YELLOW}🗄️  Checking Database...${NC}"
if [ -f "social_media.db" ]; then
    SIZE=$(du -h social_media.db | cut -f1)
    echo -e "   ${GREEN}✅ Database file exists (${SIZE})${NC}"

    # Count tables
    if python3 -c "
import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"'))
        count = result.scalar()
        print(f'   ${GREEN}✅ {count} tables created${NC}')
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; then
        :
    else
        echo -e "   ${RED}❌ Database connection failed${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "   ${YELLOW}⚠️  Database not initialized${NC}"
    echo -e "   ${YELLOW}Run: ./setup.sh${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check Configuration
echo -e "${YELLOW}⚙️  Checking Configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✅ .env file exists${NC}"

    if grep -q "TWITTER_BEARER_TOKEN=.\+" .env 2>/dev/null; then
        echo -e "   ${GREEN}✅ Twitter token configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Twitter token not set (optional)${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  .env file missing${NC}"
    echo -e "   ${YELLOW}Run: cp .env.example .env${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check Scripts
echo -e "${YELLOW}📜 Checking Scripts...${NC}"
for script in setup.sh start.sh stop.sh test.sh; do
    if [ -x "$script" ]; then
        echo -e "   ${GREEN}✅ $script (executable)${NC}"
    elif [ -f "$script" ]; then
        echo -e "   ${YELLOW}⚠️  $script exists but not executable${NC}"
        echo -e "   ${YELLOW}Run: chmod +x $script${NC}"
    else
        echo -e "   ${RED}❌ $script missing${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

# Summary
echo ""
echo -e "${BLUE}================================================================================================${NC}"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}  ✅ SYSTEM VERIFICATION PASSED - ALL CHECKS OK!${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
    echo -e "${GREEN}🚀 Ready to start!${NC}"
    echo ""
    echo "   Start application: ${BLUE}./start.sh${NC}"
    echo "   Run tests:         ${BLUE}./test.sh${NC}"
    echo "   API docs:          ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
else
    echo -e "${YELLOW}  ⚠️  FOUND $ISSUES ISSUE(S) - REVIEW ABOVE${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 To fix issues, run:${NC}"
    echo "   ${BLUE}./setup.sh${NC}"
    echo ""
fi

