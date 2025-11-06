"""
Enhanced AI Service using Hugging Face Transformers for sentiment analysis and NER
"""
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re
from collections import Counter

# Core dependencies
import numpy as np
from textblob import TextBlob

# Hugging Face dependencies
try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        AutoModelForTokenClassification, pipeline,
        logging as transformers_logging
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
    # Reduce transformers logging
    transformers_logging.set_verbosity_error()
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# SpaCy for NER
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

logger = logging.getLogger(__name__)


class EnhancedAIService:
    """Enhanced AI service with Hugging Face transformers for sentiment analysis and NER"""
    
    def __init__(self):
        """Initialize the enhanced AI service"""
        self.sentiment_model = None
        self.sentiment_tokenizer = None
        self.ner_pipeline = None
        self.nlp = None
        self._models_loaded = False
        self._loading_started = False
        
        # Model configurations
        self.sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.ner_model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
    
    async def _load_models(self):
        """Load AI models asynchronously"""
        try:
            logger.info("Loading AI models...")
            
            # Ensure NLTK data is available
            try:
                import nltk
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    logger.info("Downloading NLTK punkt tokenizer...")
                    nltk.download('punkt', quiet=True)
                    nltk.download('punkt_tab', quiet=True)
            except Exception as e:
                logger.warning(f"NLTK setup warning: {e}")
            
            if TRANSFORMERS_AVAILABLE:
                # Load sentiment analysis model
                try:
                    self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                        self.sentiment_model_name,
                        cache_dir="./model_cache"
                    )
                    self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                        self.sentiment_model_name,
                        cache_dir="./model_cache"
                    )
                    logger.info("✅ Sentiment analysis model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load sentiment model: {e}")
                
                # Load NER pipeline with better error handling
                try:
                    # Set Hugging Face token for model access
                    hf_token = os.getenv("HUGGINGFACE_TOKEN")
                    
                    self.ner_pipeline = pipeline(
                        "ner",
                        model=self.ner_model_name,
                        tokenizer=self.ner_model_name,
                        aggregation_strategy="simple",
                        device=-1,  # Force CPU usage for compatibility
                        token=hf_token
                    )
                    logger.info("✅ NER model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load NER model: {e}")
                    # Try alternative NER models
                    alternative_models = [
                        "dslim/bert-base-NER",
                        "dbmdz/bert-large-cased-finetuned-conll03-english",
                        "microsoft/DialoGPT-medium"
                    ]
                    
                    for alt_model in alternative_models:
                        try:
                            self.ner_pipeline = pipeline(
                                "ner",
                                model=alt_model,
                                aggregation_strategy="simple",
                                device=-1,
                                token=hf_token
                            )
                            logger.info(f"✅ Alternative NER model loaded successfully: {alt_model}")
                            self.ner_model_name = alt_model  # Update the model name
                            break
                        except Exception as e2:
                            logger.warning(f"Failed to load alternative NER model {alt_model}: {e2}")
                            continue
            
            # Load spaCy model for additional NER
            if SPACY_AVAILABLE:
                try:
                    # Try to load English model
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("✅ SpaCy model loaded successfully")
                except OSError:
                    logger.warning("SpaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            
            self._models_loaded = True
            logger.info("🚀 All AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            self._models_loaded = False
    
    async def _ensure_models_loaded(self):
        """Ensure models are loaded, load them if they aren't"""
        if not self._models_loaded and not self._loading_started:
            self._loading_started = True
            await self._load_models()

    async def analyze_sentiment_advanced(self, text: str) -> Dict[str, Any]:
        """
        Advanced sentiment analysis using Hugging Face RoBERTa model
        Falls back to TextBlob if transformers not available
        """
        try:
            # Ensure models are loaded
            await self._ensure_models_loaded()
            
            if not text or not text.strip():
                return {
                    "label": "neutral",
                    "score": 0.0,
                    "confidence": 0.0,
                    "model": "none"
                }
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Use Hugging Face model if available
            if TRANSFORMERS_AVAILABLE and self.sentiment_model and self.sentiment_tokenizer:
                return await self._analyze_with_roberta(cleaned_text)
            else:
                # Fallback to TextBlob
                return await self._analyze_with_textblob(cleaned_text)
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "model": "error"
            }
    
    async def _analyze_with_roberta(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using RoBERTa model"""
        try:
            # Tokenize
            inputs = self.sentiment_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                padding=True, 
                max_length=512
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Convert to labels (RoBERTa model: 0=negative, 1=neutral, 2=positive)
            scores = predictions[0].numpy()
            labels = ['negative', 'neutral', 'positive']
            
            # Get the prediction
            predicted_idx = np.argmax(scores)
            predicted_label = labels[predicted_idx]
            confidence = float(scores[predicted_idx])
            
            # Convert to score (-1 to 1 scale)
            if predicted_label == 'positive':
                score = confidence
            elif predicted_label == 'negative':
                score = -confidence
            else:
                score = 0.0
            
            return {
                "label": predicted_label,
                "score": float(score),
                "confidence": confidence,
                "model": "roberta",
                "all_scores": {
                    "negative": float(scores[0]),
                    "neutral": float(scores[1]),
                    "positive": float(scores[2])
                }
            }
            
        except Exception as e:
            logger.error(f"Error with RoBERTa analysis: {e}")
            return await self._analyze_with_textblob(text)
    
    async def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            confidence = min(abs(polarity) + subjectivity * 0.3, 1.0)
            
            return {
                "label": label,
                "score": float(polarity),
                "confidence": float(confidence),
                "model": "textblob"
            }
            
        except Exception as e:
            logger.error(f"Error with TextBlob analysis: {e}")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "model": "error"
            }
    
    async def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract location entities from text using NER models
        """
        try:
            # Ensure models are loaded
            await self._ensure_models_loaded()
            
            locations = []
            
            # Use Hugging Face NER pipeline
            if TRANSFORMERS_AVAILABLE and self.ner_pipeline:
                hf_locations = await self._extract_locations_hf(text)
                locations.extend(hf_locations)
            
            # Use spaCy NER as additional source
            if SPACY_AVAILABLE and self.nlp:
                spacy_locations = await self._extract_locations_spacy(text)
                locations.extend(spacy_locations)
            
            # Remove duplicates and return
            unique_locations = self._deduplicate_locations(locations)
            return unique_locations
            
        except Exception as e:
            logger.error(f"Error extracting locations: {e}")
            return []
    
    async def _extract_locations_hf(self, text: str) -> List[Dict[str, Any]]:
        """Extract locations using Hugging Face NER"""
        try:
            entities = self.ner_pipeline(text)
            locations = []
            
            for entity in entities:
                if entity['entity_group'] in ['LOC', 'GPE']:  # Location or Geopolitical entity
                    locations.append({
                        "text": entity['word'],
                        "label": entity['entity_group'],
                        "confidence": float(entity['score']),
                        "start": int(entity['start']),
                        "end": int(entity['end']),
                        "source": "huggingface"
                    })
            
            return locations
            
        except Exception as e:
            logger.error(f"Error with Hugging Face NER: {e}")
            return []
    
    async def _extract_locations_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract locations using spaCy NER"""
        try:
            doc = self.nlp(text)
            locations = []
            
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:  # Geopolitical entity or Location
                    locations.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "confidence": 0.8,  # spaCy doesn't provide confidence scores
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "source": "spacy"
                    })
            
            return locations
            
        except Exception as e:
            logger.error(f"Error with spaCy NER: {e}")
            return []
    
    def _deduplicate_locations(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate location mentions"""
        seen = set()
        unique_locations = []
        
        for loc in locations:
            # Normalize text for comparison
            normalized = loc['text'].lower().strip()
            if normalized not in seen and len(normalized) > 1:
                seen.add(normalized)
                unique_locations.append(loc)
        
        # Sort by confidence
        return sorted(unique_locations, key=lambda x: x['confidence'], reverse=True)
    
    async def analyze_text_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis including sentiment and location extraction
        """
        try:
            # Run sentiment and location analysis in parallel
            sentiment_task = asyncio.create_task(self.analyze_sentiment_advanced(text))
            location_task = asyncio.create_task(self.extract_locations(text))
            
            sentiment_result = await sentiment_task
            locations = await location_task
            
            # Extract additional features
            keywords = await self._extract_keywords_advanced(text)
            entities = await self._extract_entities(text)
            
            return {
                "text": text,
                "sentiment": sentiment_result,
                "locations": locations,
                "keywords": keywords,
                "entities": entities,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "models_used": self._get_models_status()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                "text": text,
                "sentiment": {"label": "neutral", "score": 0.0, "confidence": 0.0},
                "locations": [],
                "keywords": [],
                "entities": [],
                "error": str(e)
            }
    
    async def _extract_keywords_advanced(self, text: str) -> List[Dict[str, str]]:
        """Extract keywords using multiple methods"""
        try:
            keywords = []
            
            # TextBlob noun phrases
            blob = TextBlob(text)
            noun_phrases = list(blob.noun_phrases)
            
            for phrase in noun_phrases[:10]:  # Top 10
                keywords.append({
                    "text": phrase,
                    "type": "noun_phrase",
                    "source": "textblob"
                })
            
            # Simple frequency analysis
            cleaned_text = self._clean_text(text)
            words = [w.lower() for w in cleaned_text.split() 
                    if len(w) > 3 and w.lower() not in self._get_stop_words()]
            
            word_freq = Counter(words)
            for word, freq in word_freq.most_common(5):
                keywords.append({
                    "text": word,
                    "type": "frequent_word",
                    "source": "frequency",
                    "count": freq
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities (persons, organizations, etc.)"""
        try:
            entities = []
            
            # Use Hugging Face NER for all entity types
            if TRANSFORMERS_AVAILABLE and self.ner_pipeline:
                ner_results = self.ner_pipeline(text)
                
                for entity in ner_results:
                    entities.append({
                        "text": entity['word'],
                        "label": entity['entity_group'],
                        "confidence": float(entity['score']),
                        "start": int(entity['start']),
                        "end": int(entity['end']),
                        "source": "huggingface"
                    })
            
            # Use spaCy for additional entities
            if SPACY_AVAILABLE and self.nlp:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "confidence": 0.8,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "source": "spacy"
                    })
            
            return self._deduplicate_entities(entities)
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for ent in entities:
            key = (ent['text'].lower(), ent['label'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)
        
        return sorted(unique_entities, key=lambda x: x['confidence'], reverse=True)
    
    async def batch_analyze_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch analyze multiple posts for sentiment and location
        """
        try:
            results = []
            
            for post in posts:
                text = post.get('text', '')
                if text:
                    analysis = await self.analyze_text_comprehensive(text)
                    
                    # Add post metadata
                    analysis.update({
                        "post_id": post.get('id'),
                        "platform": post.get('platform'),
                        "posted_at": post.get('posted_at')
                    })
                    
                    results.append(analysis)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def _get_stop_words(self) -> set:
        """Return common stop words"""
        return {
            'about', 'above', 'after', 'again', 'against', 'all', 'also', 'and',
            'any', 'are', 'aren', 'because', 'been', 'before', 'being', 'below',
            'between', 'both', 'but', 'can', 'cannot', 'could', 'did', 'didn',
            'does', 'doesn', 'doing', 'don', 'down', 'during', 'each', 'few',
            'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have',
            'haven', 'having', 'her', 'here', 'hers', 'herself', 'him', 'himself',
            'his', 'how', 'into', 'isn', 'just', 'more', 'most', 'mustn',
            'myself', 'needn', 'nor', 'not', 'now', 'only', 'other', 'our',
            'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan', 'she',
            'should', 'shouldn', 'some', 'such', 'than', 'that', 'the', 'their',
            'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they',
            'this', 'those', 'through', 'too', 'under', 'until', 'very', 'was',
            'wasn', 'were', 'weren', 'what', 'when', 'where', 'which', 'while',
            'who', 'whom', 'why', 'will', 'with', 'won', 'would', 'wouldn',
            'you', 'your', 'yours', 'yourself'
        }
    
    def _get_models_status(self) -> Dict[str, bool]:
        """Get status of loaded models"""
        return {
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "spacy_available": SPACY_AVAILABLE,
            "sentiment_model_loaded": self.sentiment_model is not None,
            "ner_pipeline_loaded": self.ner_pipeline is not None,
            "spacy_model_loaded": self.nlp is not None,
            "models_loaded": self._models_loaded
        }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "sentiment_model": self.sentiment_model_name,
            "ner_model": self.ner_model_name,
            "status": self._get_models_status(),
            "capabilities": {
                "sentiment_analysis": True,
                "location_extraction": True,
                "entity_recognition": True,
                "keyword_extraction": True,
                "batch_processing": True
            }}



# Singleton instance
enhanced_ai_service = EnhancedAIService()