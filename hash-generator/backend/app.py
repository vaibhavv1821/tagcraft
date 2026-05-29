from flask import Flask, request, jsonify
from flask_cors import CORS

from src.nlp import (
    get_score, get_score_label, categorize,
    extract_keywords, detect_topics
)
from src.trends    import get_trending_hashtags, get_cache_status
from src.predictor import predict_all
from src.ml_engine import get_engine

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://*.vercel.app"
])

# Pre-load ML engine
print("[app] Pre-loading ML engine...")
_ml = get_engine()
print(f"[app] ML engine ready: {_ml.ready}")