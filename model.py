"""
model.py - Sentiment analysis model loading and prediction functions.
Uses HuggingFace Transformers with DistilBERT fine-tuned on SST-2.
"""

from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variable (loaded once at startup)
_sentiment_pipeline = None


def load_model():
    """Load the pre-trained DistilBERT sentiment analysis model."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info("Loading DistilBERT sentiment model...")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            tokenizer="distilbert-base-uncased-finetuned-sst-2-english",
        )
        logger.info("Model loaded successfully.")
    return _sentiment_pipeline


def predict_sentiment(text: str) -> dict:
    """
    Run sentiment prediction on input text.

    Args:
        text: Input string to classify.

    Returns:
        dict with keys: label (POSITIVE/NEGATIVE), score (float 0-1),
        and a normalized sentiment string (positive/negative/neutral).
    """
    if not text or not text.strip():
        return {
            "label": "NEUTRAL",
            "score": 0.0,
            "sentiment": "neutral",
            "message": "Empty input provided.",
        }

    model = load_model()

    # DistilBERT supports up to 512 tokens; truncate long inputs
    truncated = text[:512]
    results = model(truncated)
    result = results[0]

    label = result["label"]           # "POSITIVE" or "NEGATIVE"
    score = round(result["score"], 4)

    # Map to three-way sentiment using confidence threshold
    if label == "POSITIVE" and score >= 0.60:
        sentiment = "positive"
    elif label == "NEGATIVE" and score >= 0.60:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "label": label,
        "score": score,
        "sentiment": sentiment,
        "text_preview": text[:100] + ("..." if len(text) > 100 else ""),
    }
