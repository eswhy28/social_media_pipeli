#!/usr/bin/env python3
"""
Setup script to download all required models and data for the AI services
"""
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        logger.info("Downloading NLTK data...")
        
        # Download required NLTK packages
        packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for package in packages:
            try:
                nltk.download(package, quiet=True)
                logger.info(f"✅ Downloaded NLTK package: {package}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to download NLTK package {package}: {e}")
        
        # Download TextBlob corpora
        from textblob import download_corpora
        download_corpora.download_all()
        logger.info("✅ Downloaded TextBlob corpora")
        
    except Exception as e:
        logger.error(f"❌ Error downloading NLTK data: {e}")

def download_spacy_models():
    """Download spaCy models"""
    try:
        import subprocess
        logger.info("Downloading spaCy models...")
        
        # Download English model
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                      check=True, capture_output=True)
        logger.info("✅ Downloaded spaCy en_core_web_sm model")
        
    except Exception as e:
        logger.error(f"❌ Error downloading spaCy models: {e}")

def verify_transformers():
    """Verify transformers installation and test model loading"""
    try:
        import transformers
        import torch
        logger.info("✅ Transformers and PyTorch available")
        
        # Test imports
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        logger.info("✅ Transformers imports working")
        
        # Test Hugging Face token
        hf_token = "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"
        
        # Test loading a simple model
        try:
            tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
            logger.info("✅ Sentiment model tokenizer loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Sentiment model loading test failed: {e}")
        
        # Test NER pipeline with alternative models
        ner_models = ["dslim/bert-base-NER", "dbmdz/bert-large-cased-finetuned-conll03-english"]
        for model_name in ner_models:
            try:
                ner_pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple", device=-1, token=hf_token)
                logger.info(f"✅ NER model {model_name} loaded successfully")
                break
            except Exception as e:
                logger.warning(f"⚠️ NER model {model_name} failed: {e}")
                continue
        
    except Exception as e:
        logger.error(f"❌ Transformers verification failed: {e}")

def main():
    """Main setup function"""
    logger.info("🚀 Starting AI models setup...")
    
    # Create model cache directory
    cache_dir = "./model_cache"
    os.makedirs(cache_dir, exist_ok=True)
    logger.info(f"✅ Created model cache directory: {cache_dir}")
    
    # Download all required data
    download_nltk_data()
    download_spacy_models()
    verify_transformers()
    
    logger.info("🎉 AI models setup completed!")

if __name__ == "__main__":
    main()