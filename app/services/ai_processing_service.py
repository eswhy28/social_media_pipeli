"""
AI Processing Service for ApifyScrapedData
Handles batch processing of scraped data with intelligent tracking to avoid reprocessing
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from textblob import TextBlob
import time

from app.models.social_media_sources import ApifyScrapedData
from app.models.ai_analysis import (
    ApifyDataProcessingStatus,
    ApifySentimentAnalysis,
    ApifyLocationExtraction,
    ApifyEntityExtraction,
    ApifyKeywordExtraction,
    ApifyAIBatchJob
)
from app.services.geocoding_service import get_geocoding_service

logger = logging.getLogger(__name__)


class AIProcessingService:
    """Service for processing scraped data with AI models"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.geocoding_service = get_geocoding_service()
    
    async def get_unprocessed_data(
        self,
        service_type: str = "all",
        limit: Optional[int] = None
    ) -> List[ApifyScrapedData]:
        """
        Get scraped data that hasn't been processed yet
        
        Args:
            service_type: Type of service to check ("sentiment", "location", "entity", "keyword", "all")
            limit: Maximum number of records to return
        
        Returns:
            List of unprocessed ApifyScrapedData records
        """
        try:
            # Get all scraped data IDs
            scraped_data_query = select(ApifyScrapedData.id)
            result = await self.db.execute(scraped_data_query)
            all_ids = {row[0] for row in result.all()}
            
            # Get processed IDs based on service type
            status_query = select(ApifyDataProcessingStatus.scraped_data_id)
            
            if service_type == "sentiment":
                status_query = status_query.where(ApifyDataProcessingStatus.sentiment_processed == True)
            elif service_type == "location":
                status_query = status_query.where(ApifyDataProcessingStatus.location_processed == True)
            elif service_type == "entity":
                status_query = status_query.where(ApifyDataProcessingStatus.entity_processed == True)
            elif service_type == "keyword":
                status_query = status_query.where(ApifyDataProcessingStatus.keyword_processed == True)
            elif service_type == "all":
                status_query = status_query.where(ApifyDataProcessingStatus.is_processed == True)
            
            result = await self.db.execute(status_query)
            processed_ids = {row[0] for row in result.all()}
            
            # Get unprocessed IDs
            unprocessed_ids = all_ids - processed_ids
            
            if not unprocessed_ids:
                return []
            
            # Fetch unprocessed records
            query = select(ApifyScrapedData).where(ApifyScrapedData.id.in_(list(unprocessed_ids)))
            
            if limit:
                query = query.limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting unprocessed data: {e}")
            return []
    
    async def process_sentiment_batch(
        self,
        limit: Optional[int] = None,
        model_name: str = "textblob"
    ) -> Dict[str, Any]:
        """
        Process sentiment analysis for unprocessed data
        
        Args:
            limit: Maximum number of records to process
            model_name: Name of the sentiment model to use
        
        Returns:
            Processing results summary
        """
        try:
            # Create batch job
            batch_job = ApifyAIBatchJob(
                job_type="sentiment",
                status="processing",
                started_at=datetime.utcnow(),
                config={"model_name": model_name}
            )
            self.db.add(batch_job)
            await self.db.commit()
            
            # Get unprocessed data
            unprocessed = await self.get_unprocessed_data("sentiment", limit)
            
            batch_job.total_records = len(unprocessed)
            await self.db.commit()
            
            processed_count = 0
            failed_count = 0
            errors = []
            
            for data in unprocessed:
                try:
                    start_time = time.time()
                    
                    # Perform sentiment analysis
                    sentiment_result = await self._analyze_sentiment(data.content, model_name)
                    
                    processing_time = (time.time() - start_time) * 1000  # ms
                    
                    # Store sentiment result
                    sentiment_record = ApifySentimentAnalysis(
                        scraped_data_id=data.id,
                        label=sentiment_result['label'],
                        score=sentiment_result['score'],
                        confidence=sentiment_result['confidence'],
                        model_name=model_name,
                        all_scores=sentiment_result.get('all_scores', {}),
                        text_length=len(data.content),
                        language_detected=data.raw_data.get('lang', 'unknown') if data.raw_data else 'unknown',
                        processing_time_ms=processing_time
                    )
                    self.db.add(sentiment_record)
                    
                    # Update processing status
                    await self._update_processing_status(data.id, sentiment_processed=True)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing sentiment for {data.id}: {e}")
                    errors.append({"id": data.id, "error": str(e)})
                    failed_count += 1
                
                # Commit in batches of 10
                if processed_count % 10 == 0:
                    await self.db.commit()
            
            # Final commit
            await self.db.commit()
            
            # Update batch job
            batch_job.status = "completed" if failed_count == 0 else "partial"
            batch_job.processed_records = processed_count
            batch_job.failed_records = failed_count
            batch_job.completed_at = datetime.utcnow()
            batch_job.processing_time_seconds = (batch_job.completed_at - batch_job.started_at).total_seconds()
            batch_job.avg_time_per_record = batch_job.processing_time_seconds / processed_count if processed_count > 0 else 0
            batch_job.errors = errors
            batch_job.results_summary = {
                "total": len(unprocessed),
                "processed": processed_count,
                "failed": failed_count
            }
            await self.db.commit()
            
            return {
                "job_id": batch_job.id,
                "total_records": len(unprocessed),
                "processed": processed_count,
                "failed": failed_count,
                "processing_time_seconds": batch_job.processing_time_seconds
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment batch processing: {e}")
            if batch_job:
                batch_job.status = "failed"
                batch_job.errors = [{"error": str(e)}]
                await self.db.commit()
            raise
    
    async def process_location_batch(
        self,
        limit: Optional[int] = None,
        model_name: str = "geocoding"
    ) -> Dict[str, Any]:
        """
        Process location extraction for unprocessed data
        
        Extracts locations from content and geocodes them
        """
        try:
            # Create batch job
            batch_job = ApifyAIBatchJob(
                job_type="location",
                status="processing",
                started_at=datetime.utcnow(),
                config={"model_name": model_name}
            )
            self.db.add(batch_job)
            await self.db.commit()
            
            # Get unprocessed data
            unprocessed = await self.get_unprocessed_data("location", limit)
            
            batch_job.total_records = len(unprocessed)
            await self.db.commit()
            
            processed_count = 0
            failed_count = 0
            locations_found = 0
            
            for data in unprocessed:
                try:
                    # Extract and geocode locations
                    locations = await self._extract_locations(data)
                    
                    for loc_data in locations:
                        location_record = ApifyLocationExtraction(
                            scraped_data_id=data.id,
                            location_text=loc_data['text'],
                            location_type=loc_data['type'],
                            confidence=loc_data['confidence'],
                            model_name=model_name,
                            country=loc_data.get('country'),
                            state_province=loc_data.get('state_province'),
                            city=loc_data.get('city'),
                            region=loc_data.get('region'),
                            coordinates=loc_data.get('coordinates')
                        )
                        self.db.add(location_record)
                        locations_found += 1
                    
                    # Update processing status
                    await self._update_processing_status(data.id, location_processed=True)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing locations for {data.id}: {e}")
                    failed_count += 1
                
                if processed_count % 10 == 0:
                    await self.db.commit()
            
            await self.db.commit()
            
            # Update batch job
            batch_job.status = "completed"
            batch_job.processed_records = processed_count
            batch_job.failed_records = failed_count
            batch_job.completed_at = datetime.utcnow()
            batch_job.processing_time_seconds = (batch_job.completed_at - batch_job.started_at).total_seconds()
            batch_job.results_summary = {
                "total": len(unprocessed),
                "processed": processed_count,
                "failed": failed_count,
                "locations_found": locations_found
            }
            await self.db.commit()
            
            return {
                "job_id": batch_job.id,
                "total_records": len(unprocessed),
                "processed": processed_count,
                "failed": failed_count,
                "locations_found": locations_found
            }
            
        except Exception as e:
            logger.error(f"Error in location batch processing: {e}")
            raise
    
    async def _analyze_sentiment(self, text: str, model_name: str) -> Dict[str, Any]:
        """
        Perform sentiment analysis on text
        
        Args:
            text: Text to analyze
            model_name: Model to use (currently only textblob)
        
        Returns:
            Sentiment analysis results
        """
        if model_name == "textblob":
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine label
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                "label": label,
                "score": polarity,
                "confidence": abs(polarity),  # Use polarity magnitude as confidence
                "all_scores": {
                    "polarity": polarity,
                    "subjectivity": subjectivity
                }
            }
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    async def _extract_locations(self, data: ApifyScrapedData) -> List[Dict[str, Any]]:
        """
        Extract and geocode locations from scraped data
        
        Uses author location and content analysis
        """
        locations = []
        
        # 1. Use author location if available
        if data.location:
            enriched = self.geocoding_service.enrich_location_data(data.location)
            if enriched['coordinates']:
                locations.append({
                    "text": data.location,
                    "type": "AUTHOR_LOCATION",
                    "confidence": 1.0,
                    "country": enriched.get('country'),
                    "state_province": None,
                    "city": None,
                    "region": enriched.get('region'),
                    "coordinates": enriched.get('coordinates')
                })
        
        # 2. Extract from content (simple keyword matching for now)
        # In production, use NER model like spaCy or Hugging Face
        nigerian_cities = [
            "Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt",
            "Benin City", "Kaduna", "Enugu", "Calabar", "Warri",
            "Aba", "Jos", "Ilorin", "Oyo", "Abeokuta"
        ]
        
        content_lower = data.content.lower()
        for city in nigerian_cities:
            if city.lower() in content_lower:
                enriched = self.geocoding_service.enrich_location_data(city)
                if enriched['coordinates']:
                    locations.append({
                        "text": city,
                        "type": "GPE",  # Geo-Political Entity
                        "confidence": 0.8,  # Lower confidence for keyword match
                        "country": "Nigeria",
                        "state_province": None,
                        "city": city,
                        "region": enriched.get('region'),
                        "coordinates": enriched.get('coordinates')
                    })
        
        return locations
    
    async def _update_processing_status(
        self,
        scraped_data_id: str,
        sentiment_processed: bool = False,
        location_processed: bool = False,
        entity_processed: bool = False,
        keyword_processed: bool = False
    ):
        """Update or create processing status for a scraped data record"""
        try:
            # Check if status record exists
            result = await self.db.execute(
                select(ApifyDataProcessingStatus).where(
                    ApifyDataProcessingStatus.scraped_data_id == scraped_data_id
                )
            )
            status = result.scalar_one_or_none()
            
            if status:
                # Update existing
                if sentiment_processed:
                    status.sentiment_processed = True
                if location_processed:
                    status.location_processed = True
                if entity_processed:
                    status.entity_processed = True
                if keyword_processed:
                    status.keyword_processed = True
                
                # Check if all processing is complete
                if (status.sentiment_processed and status.location_processed and
                    status.entity_processed and status.keyword_processed):
                    status.is_processed = True
                    status.processing_completed_at = datetime.utcnow()
            else:
                # Create new
                status = ApifyDataProcessingStatus(
                    scraped_data_id=scraped_data_id,
                    sentiment_processed=sentiment_processed,
                    location_processed=location_processed,
                    entity_processed=entity_processed,
                    keyword_processed=keyword_processed,
                    processing_started_at=datetime.utcnow()
                )
                self.db.add(status)
            
        except Exception as e:
            logger.error(f"Error updating processing status: {e}")
            raise
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get overall processing statistics"""
        try:
            # Total scraped data
            total_result = await self.db.execute(select(ApifyScrapedData))
            total_count = len(total_result.scalars().all())
            
            # Processed counts
            sentiment_result = await self.db.execute(
                select(ApifyDataProcessingStatus).where(
                    ApifyDataProcessingStatus.sentiment_processed == True
                )
            )
            sentiment_count = len(sentiment_result.scalars().all())
            
            location_result = await self.db.execute(
                select(ApifyDataProcessingStatus).where(
                    ApifyDataProcessingStatus.location_processed == True
                )
            )
            location_count = len(location_result.scalars().all())
            
            fully_processed_result = await self.db.execute(
                select(ApifyDataProcessingStatus).where(
                    ApifyDataProcessingStatus.is_processed == True
                )
            )
            fully_processed_count = len(fully_processed_result.scalars().all())
            
            return {
                "total_records": total_count,
                "fully_processed": fully_processed_count,
                "sentiment_processed": sentiment_count,
                "location_processed": location_count,
                "unprocessed": total_count - fully_processed_count,
                "processing_percentage": round(fully_processed_count / total_count * 100, 2) if total_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            return {}


def get_ai_processing_service(db: AsyncSession) -> AIProcessingService:
    """Get AI processing service instance"""
    return AIProcessingService(db)
