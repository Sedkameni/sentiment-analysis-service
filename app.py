"""
app.py - Flask application for the Sentiment Analysis Microservice.
"""

import logging
from flask import Flask, request, jsonify
from model import load_model, predict_sentiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Pre-load the model when the app starts
load_model()


@app.route("/", methods=["GET"])
def home():
    """Health-check / welcome route."""
    return jsonify(
        {
            "service": "Sentiment Analysis Service",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "GET /": "Service info",
                "POST /predict": "Predict sentiment for submitted text",
            },
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    """
    Sentiment prediction endpoint.

    Accepts JSON body: { "text": "<your text here>" }
    Returns JSON: { "sentiment": "positive|negative|neutral", "score": float, ... }
    """
    data = request.get_json(silent=True)

    if not data or "text" not in data:
        return (
            jsonify(
                {
                    "error": "Bad request. Provide JSON body with a 'text' field.",
                    "example": {"text": "I love this product!"},
                }
            ),
            400,
        )

    text = data["text"]

    if not isinstance(text, str):
        return jsonify({"error": "'text' must be a string."}), 400

    result = predict_sentiment(text)
    logger.info("Prediction: %s (score=%.4f)", result["sentiment"], result["score"])
    return jsonify(result), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
