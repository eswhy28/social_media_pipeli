#!/bin/bash

# Social Media Pipeline - Stop Script
# Gracefully stops all services

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}  SOCIAL MEDIA PIPELINE - STOPPING SERVICES${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Stop Celery workers
echo -e "${YELLOW}▶ Stopping Celery workers...${NC}"
pkill -f "celery.*app.celery_app.*worker" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Celery workers stopped${NC}"
else
    echo -e "${YELLOW}ℹ️  No Celery workers were running${NC}"
fi

# Stop Celery Beat
echo -e "${YELLOW}▶ Stopping Celery Beat...${NC}"
pkill -f "celery.*app.celery_app.*beat" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Celery Beat stopped${NC}"
else
    echo -e "${YELLOW}ℹ️  Celery Beat was not running${NC}"
fi

# Stop FastAPI/Uvicorn
echo -e "${YELLOW}▶ Stopping FastAPI application...${NC}"
pkill -f "uvicorn.*app.main" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ FastAPI application stopped${NC}"
else
    echo -e "${YELLOW}ℹ️  FastAPI application was not running${NC}"
fi

# Wait for processes to terminate
sleep 2

# Verify all stopped
REMAINING=$(pgrep -f "celery.*app.celery_app|uvicorn.*app.main" 2>/dev/null)
if [ -z "$REMAINING" ]; then
    echo ""
    echo -e "${GREEN}✅ All services stopped successfully${NC}"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Some processes are still running. Force killing...${NC}"
    pkill -9 -f "celery.*app.celery_app|uvicorn.*app.main" 2>/dev/null
    sleep 1
    echo -e "${GREEN}✅ All services stopped${NC}"
    echo ""
fi

echo -e "${BLUE}To start services again, run: ${GREEN}./start.sh${NC}"
echo ""

