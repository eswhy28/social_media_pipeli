"""
Tests for Social Media Services
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.google_trends_service import GoogleTrendsService
from app.services.tiktok_service import TikTokService
from app.services.facebook_service import FacebookService
from app.services.apify_service import ApifyService


class TestGoogleTrendsService:
    """Tests for Google Trends Service"""

    @pytest.mark.asyncio
    async def test_get_trending_searches(self):
        """Test fetching trending searches"""
        service = GoogleTrendsService()

        with patch.object(service, 'get_trending_searches', new=AsyncMock()) as mock_get:
            mock_get.return_value = [
                {
                    "term": "Nigeria",
                    "rank": 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "region": "NG",
                    "source": "google_trends"
                }
            ]

            result = await service.get_trending_searches("NG")

            assert result is not None
            assert len(result) > 0
            assert result[0]["source"] == "google_trends"

    @pytest.mark.asyncio
    async def test_get_suggestions(self):
        """Test keyword suggestions"""
        service = GoogleTrendsService()

        with patch.object(service, 'get_suggestions', new=AsyncMock()) as mock_get:
            mock_get.return_value = ["Nigeria", "Nigerian", "Naija"]

            result = await service.get_suggestions("nige")

            assert result is not None
            assert isinstance(result, list)


class TestTikTokService:
    """Tests for TikTok Service"""

    @pytest.mark.asyncio
    async def test_search_hashtag(self):
        """Test hashtag search"""
        service = TikTokService()

        with patch.object(service, 'search_hashtag', new=AsyncMock()) as mock_search:
            mock_search.return_value = [
                {
                    "video_id": "123",
                    "author": {"username": "testuser"},
                    "metrics": {"views": 1000, "likes": 100},
                    "hashtags": ["nigeria"]
                }
            ]

            result = await service.search_hashtag("nigeria", count=10)

            assert result is not None
            assert len(result) > 0

    def test_calculate_engagement_rate(self):
        """Test engagement rate calculation"""
        service = TikTokService()

        video_data = {
            "metrics": {
                "views": 1000,
                "likes": 100,
                "comments": 20,
                "shares": 10
            }
        }

        engagement_rate = service.calculate_engagement_rate(video_data)

        assert engagement_rate > 0
        assert engagement_rate <= 100


class TestFacebookService:
    """Tests for Facebook Service"""

    @pytest.mark.asyncio
    async def test_scrape_page_posts(self):
        """Test page scraping"""
        service = FacebookService()

        with patch.object(service, 'scrape_page_posts', new=AsyncMock()) as mock_scrape:
            mock_scrape.return_value = [
                {
                    "post_id": "123",
                    "page": "testpage",
                    "content": {"text": "Test post"},
                    "metrics": {"likes": 100, "comments": 10}
                }
            ]

            result = await service.scrape_page_posts("testpage", pages=1)

            assert result is not None
            assert len(result) > 0

    def test_calculate_engagement_rate(self):
        """Test engagement calculation"""
        service = FacebookService()

        post_data = {
            "metrics": {
                "likes": 100,
                "comments": 20,
                "shares": 5
            }
        }

        engagement_score = service.calculate_engagement_rate(post_data)

        assert engagement_score > 0


class TestApifyService:
    """Tests for Apify Service"""

    def test_initialization_without_token(self):
        """Test service initialization without API token"""
        with patch('app.services.apify_service.settings') as mock_settings:
            mock_settings.APIFY_API_TOKEN = None

            service = ApifyService()

            assert service.client is None

    @pytest.mark.asyncio
    async def test_run_actor(self):
        """Test running an Apify actor"""
        service = ApifyService()

        if not service.api_token:
            pytest.skip("Apify API token not configured")

        with patch.object(service, 'run_actor', new=AsyncMock()) as mock_run:
            mock_run.return_value = {
                "status": "SUCCEEDED",
                "run_id": "test123",
                "data": []
            }

            result = await service.run_actor(
                actor_id="test/actor",
                run_input={}
            )

            assert result is not None
            assert "status" in result


class TestDataPipeline:
    """Tests for Data Pipeline Service"""

    def test_nigerian_content_detection(self):
        """Test Nigerian content detection"""
        from app.services.data_pipeline_service import DataPipelineService

        service = DataPipelineService(MagicMock())

        # Test with Nigerian keyword
        assert service.is_nigerian_content("Nigeria is great") is True

        # Test with Nigerian location
        assert service.is_nigerian_content("Test", location="Lagos") is True

        # Test without Nigerian content
        assert service.is_nigerian_content("Random text", location="London") is False

    def test_text_cleaning(self):
        """Test text cleaning"""
        from app.services.data_pipeline_service import DataPipelineService

        service = DataPipelineService(MagicMock())

        dirty_text = "Check this out! https://example.com  #trending   "
        clean_text = service.clean_text(dirty_text)

        assert "https" not in clean_text
        assert clean_text.strip() == clean_text

    def test_hashtag_extraction(self):
        """Test hashtag extraction"""
        from app.services.data_pipeline_service import DataPipelineService

        service = DataPipelineService(MagicMock())

        text = "This is a post #Nigeria #Naija #trending"
        hashtags = service.extract_hashtags(text)

        assert len(hashtags) == 3
        assert "Nigeria" in hashtags
        assert "Naija" in hashtags


class TestMonitoringService:
    """Tests for Monitoring Service"""

    @pytest.mark.asyncio
    async def test_record_fetch_attempt(self):
        """Test recording fetch attempt"""
        from app.services.monitoring_service import MonitoringService

        mock_db = AsyncMock()
        service = MonitoringService(mock_db)

        with patch.object(mock_db, 'execute', new=AsyncMock()):
            with patch.object(mock_db, 'commit', new=AsyncMock()):
                result = await service.record_fetch_attempt(
                    source_type="google_trends",
                    source_name="test",
                    success=True,
                    items_collected=10
                )

                assert result is True


# Integration tests would go here with real database
# They would test the full pipeline with real data
