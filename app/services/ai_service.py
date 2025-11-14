from typing import Dict, List, Any, Optional
import logging
import re
from collections import Counter
from datetime import datetime, timedelta
from textblob import TextBlob
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
#from app.models import SocialPost, SentimentTimeSeries, TrendingTopic, AnomalyDetection

logger = logging.getLogger(__name__)


class AIService:
    """AI service for sentiment analysis and text processing using TextBlob"""

    def __init__(self):
        """Initialize AI service"""
        self.stop_words = self._get_stop_words()

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using TextBlob
        Returns sentiment label, score, and confidence
        """
        try:
            if not text or not text.strip():
                return {
                    "label": "neutral",
                    "score": 0.0,
                    "confidence": 0.0
                }

            # Clean text
            cleaned_text = self._clean_text(text)

            # Analyze with TextBlob
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Classify sentiment
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"

            # Use subjectivity as confidence proxy (more subjective = more confident)
            confidence = min(abs(polarity) + subjectivity * 0.3, 1.0)

            return {
                "label": label,
                "score": float(polarity),
                "confidence": float(confidence)
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }

    async def batch_analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            result = await self.analyze_sentiment(text)
            results.append(result)
        return results

    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Simple anomaly detection using statistical methods
        Detects values that are more than threshold standard deviations from mean
        """
        try:
            if not data or len(data) < 3:
                return []

            # Extract values
            values = [item.get('value', 0) for item in data]

            # Calculate statistics
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5

            if std_dev == 0:
                return []

            # Detect anomalies
            anomalies = []
            for i, item in enumerate(data):
                value = item.get('value', 0)
                z_score = abs((value - mean) / std_dev)

                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "timestamp": item.get('timestamp'),
                        "value": value,
                        "expected": mean,
                        "deviation": z_score,
                        "severity": "high" if z_score > 3 else "medium"
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []

    async def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract key phrases from text using simple frequency analysis"""
        try:
            cleaned_text = self._clean_text(text)
            blob = TextBlob(cleaned_text)

            # Get noun phrases
            noun_phrases = blob.noun_phrases

            # Count frequencies
            phrase_counts = Counter(noun_phrases)

            # Return top N
            return [phrase for phrase, count in phrase_counts.most_common(top_n)]

        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []

    async def detect_trending_topics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect trending topics from a list of posts"""
        try:
            hashtag_counter = Counter()
            keyword_counter = Counter()
            
            for post in posts:
                text = post.get('text', '')
                
                # Extract hashtags
                hashtags = re.findall(r'#(\w+)', text.lower())
                hashtag_counter.update(hashtags)
                
                # Extract keywords from cleaned text
                cleaned = self._clean_text(text)
                words = [w.lower() for w in cleaned.split() if len(w) > 3 and w.lower() not in self.stop_words]
                keyword_counter.update(words)
            
            return {
                "hashtags": [
                    {"topic": tag, "count": count, "change": 0.0}
                    for tag, count in hashtag_counter.most_common(10)
                ],
                "keywords": [
                    {"topic": word, "count": count, "change": 0.0}
                    for word, count in keyword_counter.most_common(10)
                ]
            }
        
        except Exception as e:
            logger.error(f"Error detecting trending topics: {str(e)}")
            return {"hashtags": [], "keywords": []}

    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def _get_stop_words(self) -> set:
        """Return common stop words to filter out"""
        return {
            'about', 'above', 'after', 'again', 'against', 'all', 'also', 'and',
            'any', 'are', 'aren', 'because', 'been', 'before', 'being', 'below',
            'between', 'both', 'but', 'can', 'cannot', 'could', 'did', 'didn',
            'does', 'doesn', 'doing', 'don', 'down', 'during', 'each', 'few',
            'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have',
            'haven', 'having', 'her', 'here', 'hers', 'herself', 'him', 'himself',
            'his', 'how', 'into', 'isn', 'it', 'its', 'itself', 'just', 'more',
            'most', 'mustn', 'myself', 'needn', 'nor', 'not', 'now', 'only',
            'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same',
            'shan', 'she', 'should', 'shouldn', 'some', 'such', 'than', 'that',
            'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
            'these', 'they', 'this', 'those', 'through', 'too', 'under',
            'until', 'very', 'was', 'wasn', 'we', 'were', 'weren', 'what',
            'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will',
            'with', 'won', 'would', 'wouldn', 'you', 'your', 'yours', 'yourself'
        }

    def _parse_date_range(self, range_str: str) -> tuple:
        """Parse date range string into start and end datetime"""
        end = datetime.utcnow()

        if range_str == "Today":
            start = end.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range_str == "Last 7 Days":
            start = end - timedelta(days=7)
        elif range_str == "Last 30 Days":
            start = end - timedelta(days=30)
        elif range_str == "Last 90 Days":
            start = end - timedelta(days=90)
        else:
            start = end - timedelta(days=7)

        return start, end

    async def generate_summary(
        self,
        section: str,
        subject: str,
        template: str,
        range: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI summary for report sections using TextBlob insights
        This is a simplified implementation for POC
        """
        try:
            # Extract key metrics from context
            total_posts = context.get('total_posts', 0)
            sentiment_data = context.get('sentiment', {})

            # Generate summary based on section
            if section == "overview":
                summary = self._generate_overview_summary(subject, total_posts, sentiment_data, range)
            elif section == "sentiment":
                summary = self._generate_sentiment_summary(sentiment_data, total_posts)
            elif section == "timeline":
                summary = self._generate_timeline_summary(context, range)
            elif section == "influencers":
                summary = self._generate_influencer_summary(context)
            elif section == "geo":
                summary = self._generate_geographic_summary(context)
            else:
                summary = f"Analysis summary for {subject} over {range}"

            return {
                "summary": summary,
                "word_count": len(summary.split()),
                "key_points": self._extract_key_points(summary)
            }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "summary": f"Unable to generate summary for {section}",
                "word_count": 0,
                "key_points": []
            }

    async def generate_insights(
        self,
        section: str,
        subject: str,
        template: str,
        range: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed AI insights for report sections
        This is a simplified implementation for POC
        """
        try:
            insights = []

            # Generate insights based on section
            if section == "sentiment":
                insights = self._generate_sentiment_insights(context)
            elif section == "narratives":
                insights = self._generate_narrative_insights(context)
            elif section == "topPosts":
                insights = self._generate_top_posts_insights(context)
            elif section == "influencers":
                insights = self._generate_influencer_insights(context)
            else:
                insights = [f"Key insight about {subject} from {section} analysis"]

            return {
                "insights": insights,
                "confidence": 0.75,
                "recommendations": self._generate_recommendations(context, section)
            }

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "insights": [],
                "confidence": 0.0,
                "recommendations": []
            }

    def _generate_overview_summary(self, subject: str, total_posts: int, sentiment_data: Dict, range_str: str) -> str:
        """Generate overview summary"""
        pos = sentiment_data.get('positive', 0)
        neg = sentiment_data.get('negative', 0)
        neu = sentiment_data.get('neutral', 0)
        total = pos + neg + neu

        if total == 0:
            return f"No data available for {subject} in the {range_str} period."

        pos_pct = (pos / total * 100) if total > 0 else 0
        neg_pct = (neg / total * 100) if total > 0 else 0

        sentiment_trend = "positive" if pos > neg else "negative" if neg > pos else "neutral"

        return (f"Analysis of '{subject}' over {range_str} reveals {total_posts:,} total mentions. "
                f"Sentiment analysis shows {pos_pct:.1f}% positive, {neg_pct:.1f}% negative sentiment, "
                f"indicating an overall {sentiment_trend} trend in public discourse.")

    def _generate_sentiment_summary(self, sentiment_data: Dict, total_posts: int) -> str:
        """Generate sentiment analysis summary"""
        pos = sentiment_data.get('positive', 0)
        neg = sentiment_data.get('negative', 0)

        if pos > neg:
            return f"Overall sentiment is predominantly positive with {pos} positive mentions compared to {neg} negative ones across {total_posts} total posts."
        elif neg > pos:
            return f"Overall sentiment leans negative with {neg} negative mentions compared to {pos} positive ones across {total_posts} total posts."
        else:
            return f"Sentiment is evenly balanced between positive and negative mentions across {total_posts} total posts."

    def _generate_timeline_summary(self, context: Dict, range_str: str) -> str:
        """Generate timeline summary"""
        return f"Timeline analysis over {range_str} shows varying levels of engagement and sentiment shifts in the conversation."

    def _generate_influencer_summary(self, context: Dict) -> str:
        """Generate influencer summary"""
        influencers = context.get('influencers', [])
        if not influencers:
            return "No significant influencer activity detected in this period."

        return f"Analysis identified {len(influencers)} key influencers driving the conversation with significant reach and engagement."

    def _generate_geographic_summary(self, context: Dict) -> str:
        """Generate geographic summary"""
        return "Geographic analysis shows distribution of mentions across different regions with varying sentiment patterns."

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from summary text"""
        sentences = text.split('. ')
        return [s.strip() + '.' for s in sentences if len(s.split()) > 5][:3]

    def _generate_sentiment_insights(self, context: Dict) -> List[str]:
        """Generate sentiment-specific insights"""
        sentiment_data = context.get('sentiment', {})
        total = sum(sentiment_data.values()) if sentiment_data else 0

        if total == 0:
            return ["Insufficient data for sentiment analysis"]

        insights = []
        pos_pct = (sentiment_data.get('positive', 0) / total * 100)
        neg_pct = (sentiment_data.get('negative', 0) / total * 100)

        if pos_pct > 60:
            insights.append("Strong positive sentiment indicates favorable public perception")
        elif neg_pct > 60:
            insights.append("Elevated negative sentiment suggests areas of concern requiring attention")

        insights.append(f"Sentiment distribution shows {pos_pct:.1f}% positive vs {neg_pct:.1f}% negative")

        return insights

    def _generate_narrative_insights(self, context: Dict) -> List[str]:
        """Generate narrative insights"""
        return [
            "Multiple narrative threads identified in the conversation",
            "Dominant narratives show consistent themes across time periods",
            "Counter-narratives present but with lower engagement"
        ]

    def _generate_top_posts_insights(self, context: Dict) -> List[str]:
        """Generate insights from top posts"""
        posts = context.get('posts', [])
        if not posts:
            return ["No significant posts to analyze"]

        return [
            f"Top {len(posts)} posts generated significant engagement",
            "High-engagement posts share common characteristics in messaging",
            "Viral content shows correlation with emotional appeal"
        ]

    def _generate_influencer_insights(self, context: Dict) -> List[str]:
        """Generate influencer insights"""
        return [
            "Key influencers amplify message reach significantly",
            "Influencer engagement patterns show coordinated activity",
            "Network effects visible in influencer-driven conversations"
        ]

    def _generate_recommendations(self, context: Dict, section: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        sentiment_data = context.get('sentiment', {})
        total = sum(sentiment_data.values()) if sentiment_data else 0

        if total > 0:
            neg_pct = (sentiment_data.get('negative', 0) / total * 100)
            if neg_pct > 50:
                recommendations.append("Address negative sentiment drivers through targeted messaging")
                recommendations.append("Monitor conversation for escalating concerns")

        recommendations.append("Continue monitoring sentiment trends for early warning signals")
        recommendations.append("Engage with key influencers to amplify positive messaging")

        return recommendations


# Singleton instance
ai_service = AIService()


# Factory function for dependency injection
def get_ai_service() -> AIService:
    """Get AI service instance"""
    return ai_service

