"""
Google Trends Service for Nigerian Social Media Analysis
Fetches trending topics, search interest, and related queries for Nigeria
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

logger = logging.getLogger(__name__)


class GoogleTrendsService:
    """
    Service for fetching and processing Google Trends data
    Focused on Nigerian market analysis
    """

    def __init__(self):
        """Initialize Google Trends service"""
        self.timeout = settings.GOOGLE_TRENDS_TIMEOUT
        self.max_retries = settings.GOOGLE_TRENDS_RETRIES

        # Nigeria geo code (ISO 3166-2)
        self.nigeria_geo = "NG"

        # Nigerian states for regional analysis
        self.nigerian_states = [
            "NG-AB", "NG-AD", "NG-AK", "NG-AN", "NG-BA", "NG-BE", "NG-BO",
            "NG-BY", "NG-CR", "NG-DE", "NG-EB", "NG-ED", "NG-EK", "NG-EN",
            "NG-FC", "NG-GO", "NG-IM", "NG-JI", "NG-KD", "NG-KE", "NG-KN",
            "NG-KO", "NG-KT", "NG-KW", "NG-LA", "NG-NA", "NG-NI", "NG-OG",
            "NG-ON", "NG-OS", "NG-OY", "NG-PL", "NG-RI", "NG-SO", "NG-TA",
            "NG-YO", "NG-ZA"
        ]

        logger.info("Google Trends Service initialized for Nigeria")

    def _get_pytrends_client(self) -> TrendReq:
        """
        Create a new pytrends client instance

        Returns:
            TrendReq: Configured pytrends client
        """
        return TrendReq(
            hl='en-NG',  # English (Nigeria)
            tz=60,  # WAT (West Africa Time, UTC+1)
            timeout=(self.timeout, self.timeout),
            retries=self.max_retries,
            backoff_factor=0.5
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ResponseError)
    )
    async def get_trending_searches(self, region: str = "NG") -> List[Dict[str, Any]]:
        """
        Get current trending searches in Nigeria

        Args:
            region: ISO country code (default: NG for Nigeria)

        Returns:
            List of trending search terms with metadata
        """
        try:
            logger.info(f"Fetching trending searches for {region}")

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            pytrends = self._get_pytrends_client()

            # Get trending searches
            trending_df = await loop.run_in_executor(
                None,
                pytrends.trending_searches,
                region
            )

            # Transform to list of dictionaries
            trending_data = []
            for idx, term in enumerate(trending_df[0].tolist()):
                trending_data.append({
                    "term": term,
                    "rank": idx + 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "region": region,
                    "source": "google_trends"
                })

            logger.info(f"Retrieved {len(trending_data)} trending searches")
            return trending_data

        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ResponseError)
    )
    async def get_interest_over_time(
        self,
        keywords: List[str],
        timeframe: str = "today 3-m",
        geo: str = "NG"
    ) -> Dict[str, Any]:
        """
        Get interest over time for specific keywords in Nigeria

        Args:
            keywords: List of keywords to track (max 5)
            timeframe: Time period (e.g., 'today 3-m', 'today 12-m', 'now 7-d')
            geo: Geographic region (default: NG)

        Returns:
            Dictionary with time series data and metadata
        """
        try:
            logger.info(f"Fetching interest over time for: {keywords}")

            # Limit to 5 keywords (API restriction)
            if len(keywords) > 5:
                keywords = keywords[:5]
                logger.warning("Limited to 5 keywords due to API restrictions")

            loop = asyncio.get_event_loop()
            pytrends = self._get_pytrends_client()

            # Build payload
            await loop.run_in_executor(
                None,
                lambda: pytrends.build_payload(
                    keywords,
                    cat=0,
                    timeframe=timeframe,
                    geo=geo,
                    gprop=''
                )
            )

            # Get interest over time
            interest_df = await loop.run_in_executor(
                None,
                pytrends.interest_over_time
            )

            if interest_df.empty:
                return {"keywords": keywords, "data": [], "timeframe": timeframe}

            # Remove 'isPartial' column if exists
            if 'isPartial' in interest_df.columns:
                interest_df = interest_df.drop(columns=['isPartial'])

            # Transform to dictionary format
            data = []
            for date, row in interest_df.iterrows():
                data_point = {
                    "date": date.isoformat(),
                    "values": {kw: int(row[kw]) for kw in keywords if kw in row}
                }
                data.append(data_point)

            result = {
                "keywords": keywords,
                "data": data,
                "timeframe": timeframe,
                "geo": geo,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Retrieved {len(data)} data points")
            return result

        except Exception as e:
            logger.error(f"Error fetching interest over time: {e}")
            return {"keywords": keywords, "data": [], "error": str(e)}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ResponseError)
    )
    async def get_related_queries(
        self,
        keyword: str,
        geo: str = "NG"
    ) -> Dict[str, Any]:
        """
        Get related queries for a keyword in Nigeria

        Args:
            keyword: Main keyword to analyze
            geo: Geographic region (default: NG)

        Returns:
            Dictionary with top and rising related queries
        """
        try:
            logger.info(f"Fetching related queries for: {keyword}")

            loop = asyncio.get_event_loop()
            pytrends = self._get_pytrends_client()

            # Build payload
            await loop.run_in_executor(
                None,
                lambda: pytrends.build_payload(
                    [keyword],
                    cat=0,
                    timeframe='today 3-m',
                    geo=geo,
                    gprop=''
                )
            )

            # Get related queries
            related_dict = await loop.run_in_executor(
                None,
                pytrends.related_queries
            )

            # Transform the data
            result = {
                "keyword": keyword,
                "geo": geo,
                "top_queries": [],
                "rising_queries": [],
                "timestamp": datetime.utcnow().isoformat()
            }

            if keyword in related_dict:
                # Process top queries
                if related_dict[keyword]['top'] is not None:
                    top_df = related_dict[keyword]['top']
                    result['top_queries'] = [
                        {"query": row['query'], "value": int(row['value'])}
                        for _, row in top_df.iterrows()
                    ]

                # Process rising queries
                if related_dict[keyword]['rising'] is not None:
                    rising_df = related_dict[keyword]['rising']
                    result['rising_queries'] = [
                        {
                            "query": row['query'],
                            "value": row['value'] if pd.notna(row['value']) else "Breakout"
                        }
                        for _, row in rising_df.iterrows()
                    ]

            logger.info(f"Retrieved {len(result['top_queries'])} top and "
                       f"{len(result['rising_queries'])} rising queries")
            return result

        except Exception as e:
            logger.error(f"Error fetching related queries: {e}")
            return {"keyword": keyword, "top_queries": [], "rising_queries": [], "error": str(e)}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ResponseError)
    )
    async def get_regional_interest(
        self,
        keyword: str,
        resolution: str = "REGION"
    ) -> Dict[str, Any]:
        """
        Get regional interest breakdown within Nigeria

        Args:
            keyword: Keyword to analyze
            resolution: 'REGION' for states, 'CITY' for cities

        Returns:
            Dictionary with regional interest data
        """
        try:
            logger.info(f"Fetching regional interest for: {keyword}")

            loop = asyncio.get_event_loop()
            pytrends = self._get_pytrends_client()

            # Build payload
            await loop.run_in_executor(
                None,
                lambda: pytrends.build_payload(
                    [keyword],
                    cat=0,
                    timeframe='today 3-m',
                    geo='NG',
                    gprop=''
                )
            )

            # Get regional interest
            regional_df = await loop.run_in_executor(
                None,
                lambda: pytrends.interest_by_region(
                    resolution=resolution,
                    inc_low_vol=True,
                    inc_geo_code=True
                )
            )

            # Transform to list of dictionaries
            regional_data = []
            if not regional_df.empty:
                for location, row in regional_df.iterrows():
                    regional_data.append({
                        "location": location,
                        "interest": int(row[keyword]) if keyword in row else 0
                    })

                # Sort by interest
                regional_data.sort(key=lambda x: x['interest'], reverse=True)

            result = {
                "keyword": keyword,
                "resolution": resolution,
                "regions": regional_data,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Retrieved interest data for {len(regional_data)} regions")
            return result

        except Exception as e:
            logger.error(f"Error fetching regional interest: {e}")
            return {"keyword": keyword, "regions": [], "error": str(e)}

    async def get_suggestions(self, keyword: str) -> List[str]:
        """
        Get keyword suggestions based on partial input

        Args:
            keyword: Partial keyword

        Returns:
            List of suggested keywords
        """
        try:
            logger.info(f"Fetching suggestions for: {keyword}")

            loop = asyncio.get_event_loop()
            pytrends = self._get_pytrends_client()

            suggestions = await loop.run_in_executor(
                None,
                pytrends.suggestions,
                keyword
            )

            # Extract just the titles
            suggestion_list = [s['title'] for s in suggestions]

            logger.info(f"Retrieved {len(suggestion_list)} suggestions")
            return suggestion_list

        except Exception as e:
            logger.error(f"Error fetching suggestions: {e}")
            return []

    def transform_to_social_media_format(
        self,
        trends_data: List[Dict[str, Any]],
        data_type: str = "trending"
    ) -> List[Dict[str, Any]]:
        """
        Transform Google Trends data to match social media pipeline format

        Args:
            trends_data: Raw trends data
            data_type: Type of data (trending, interest, regional)

        Returns:
            Transformed data matching pipeline schema
        """
        transformed = []

        for item in trends_data:
            transformed_item = {
                "source": "google_trends",
                "source_id": f"gt_{item.get('term', '')}_{item.get('timestamp', '')}",
                "content": item.get('term', ''),
                "data_type": data_type,
                "metadata": {
                    "rank": item.get('rank'),
                    "region": item.get('region', 'NG'),
                    "interest_value": item.get('interest'),
                    "related_queries": item.get('related_queries', [])
                },
                "collected_at": item.get('timestamp', datetime.utcnow().isoformat()),
                "geo_location": "Nigeria"
            }
            transformed.append(transformed_item)

        return transformed

    async def get_comprehensive_analysis(
        self,
        keywords: List[str],
        include_related: bool = True,
        include_regional: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive analysis for multiple keywords

        Args:
            keywords: List of keywords to analyze
            include_related: Include related queries analysis
            include_regional: Include regional interest analysis

        Returns:
            Comprehensive analysis data
        """
        try:
            logger.info(f"Starting comprehensive analysis for {len(keywords)} keywords")

            results = {
                "keywords": keywords,
                "interest_over_time": None,
                "related_data": [],
                "regional_data": [],
                "timestamp": datetime.utcnow().isoformat()
            }

            # Get interest over time for all keywords
            results["interest_over_time"] = await self.get_interest_over_time(keywords)

            # Get related and regional data for each keyword
            if include_related or include_regional:
                for keyword in keywords:
                    if include_related:
                        related = await self.get_related_queries(keyword)
                        results["related_data"].append(related)

                        # Rate limiting
                        await asyncio.sleep(1)

                    if include_regional:
                        regional = await self.get_regional_interest(keyword)
                        results["regional_data"].append(regional)

                        # Rate limiting
                        await asyncio.sleep(1)

            logger.info("Comprehensive analysis completed")
            return results

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e), "keywords": keywords}


# Singleton instance
_google_trends_service = None


def get_google_trends_service() -> GoogleTrendsService:
    """Get or create Google Trends service instance"""
    global _google_trends_service
    if _google_trends_service is None:
        _google_trends_service = GoogleTrendsService()
    return _google_trends_service
