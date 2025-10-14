import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    # Use a test database URL
    test_db_url = settings.DATABASE_URL.replace("social_monitor", "social_monitor_test").replace("+asyncpg", "")

    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)

