#!/bin/bash

# Social Media Pipeline - Test Script
# Runs the test suite with coverage reporting

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}  SOCIAL MEDIA PIPELINE - TEST SUITE${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run ./setup.sh first${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Installing pytest...${NC}"
    pip install pytest pytest-asyncio pytest-cov > /dev/null 2>&1
fi

# Run tests
echo -e "${YELLOW}▶ Running test suite...${NC}"
echo ""

# Run pytest with coverage
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html

TEST_RESULT=$?

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}================================================================================================${NC}"
    echo -e "${GREEN}  ✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}================================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 Coverage Report:${NC}"
    echo "   - Terminal: See above"
    echo "   - HTML Report: ${BLUE}htmlcov/index.html${NC}"
    echo ""
    echo "   View HTML report: ${BLUE}open htmlcov/index.html${NC}"
    echo ""
else
    echo -e "${RED}================================================================================================${NC}"
    echo -e "${RED}  ❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}================================================================================================${NC}"
    echo ""
    echo "Please review the errors above and fix the issues."
    echo ""
    exit 1
fi
#!/bin/bash

# Social Media Pipeline - Start Script
# Starts all services (API, Celery Workers, Celery Beat)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}  SOCIAL MEDIA PIPELINE - STARTING SERVICES${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run ./setup.sh first${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running
echo -e "${YELLOW}▶ Checking Redis...${NC}"
if ! redis-cli ping &> /dev/null; then
    echo -e "${YELLOW}⚠️  Redis not running. Attempting to start...${NC}"
    if command -v systemctl &> /dev/null; then
        sudo systemctl start redis 2>/dev/null || redis-server --daemonize yes
    else
        redis-server --daemonize yes
    fi
    sleep 2
fi

if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running. Start it manually: redis-server${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Kill any existing processes
echo -e "${YELLOW}▶ Stopping any existing processes...${NC}"
pkill -f "celery.*app.celery_app" 2>/dev/null || true
pkill -f "uvicorn.*app.main" 2>/dev/null || true
sleep 2

# Start Celery Worker
echo -e "${YELLOW}▶ Starting Celery Worker...${NC}"
celery -A app.celery_app worker --loglevel=info --logfile=logs/celery_worker.log --detach
echo -e "${GREEN}✅ Celery Worker started${NC}"

# Start Celery Beat (Task Scheduler)
echo -e "${YELLOW}▶ Starting Celery Beat...${NC}"
celery -A app.celery_app beat --loglevel=info --logfile=logs/celery_beat.log --detach
echo -e "${GREEN}✅ Celery Beat started${NC}"

# Start FastAPI application
echo -e "${YELLOW}▶ Starting FastAPI application...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info > logs/api.log 2>&1 &
API_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if the API is running
if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✅ FastAPI application started (PID: $API_PID)${NC}"
else
    echo -e "${RED}❌ Failed to start FastAPI application${NC}"
    echo "Check logs/api.log for details"
    exit 1
fi

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}  ✅ ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo -e "${YELLOW}📡 Service Status:${NC}"
echo "   - API Server:      ${GREEN}Running${NC} on http://localhost:8000"
echo "   - Celery Worker:   ${GREEN}Running${NC}"
echo "   - Celery Beat:     ${GREEN}Running${NC}"
echo "   - Redis:           ${GREEN}Running${NC}"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "   - Swagger UI:  ${BLUE}http://localhost:8000/docs${NC}"
echo "   - ReDoc:       ${BLUE}http://localhost:8000/redoc${NC}"
echo "   - Health:      ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}📊 Monitoring:${NC}"
echo "   - API Logs:        ${BLUE}tail -f logs/api.log${NC}"
echo "   - Celery Logs:     ${BLUE}tail -f logs/celery_worker.log${NC}"
echo "   - Stop Services:   ${BLUE}./stop.sh${NC}"
echo ""
echo -e "${YELLOW}🔑 Demo Credentials:${NC}"
echo "   Username: ${GREEN}demo${NC}"
echo "   Password: ${GREEN}demo123${NC}"
echo ""
echo -e "${GREEN}Application is ready! Visit http://localhost:8000/docs to get started 🚀${NC}"
echo ""

# Try to open browser (optional)
if command -v xdg-open &> /dev/null; then
    sleep 2
    xdg-open http://localhost:8000/docs 2>/dev/null &
elif command -v open &> /dev/null; then
    sleep 2
    open http://localhost:8000/docs 2>/dev/null &
fi

