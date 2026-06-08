//code
import os
import json
import re
import joblib
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from flask import Flask, render_template, request, jsonify
from scipy.sparse import csr_matrix, hstack
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_PATH = os.path.join(BASE_DIR, "support_tickets.csv")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

tfidf = None
category_model = None
priority_model = None
metrics_data = None


def load_models():
    """Load trained models and metrics from disk."""
    global tfidf, category_model, priority_model, metrics_data

    try:
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
        nltk.download("stopwords", quiet=True)
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
    except Exception:
        pass

    tfidf = joblib.load(os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
    category_model = joblib.load(os.path.join(MODELS_DIR, "category_model.joblib"))
    priority_model = joblib.load(os.path.join(MODELS_DIR, "priority_model.joblib"))

    with open(os.path.join(MODELS_DIR, "evaluation_results.json"), "r") as f:
        metrics_data = json.load(f)

    print("Models loaded successfully!")


def clean_text(text):
    """Clean and preprocess a single text string."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_single(text):
    """Preprocess a single text for prediction."""
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
    return " ".join(tokens)


def build_urgency_features_single(text):
    """Build urgency features for a single text (must match train_model.py)."""
    urgent_keywords = [
        "urgent", "immediately", "emergency", "critical", "asap", "right away",
        "help me", "need it now", "cannot wait", "serious", "safety", "hazard",
        "fire", "smoke", "exploded", "hacked", "compromised", "breach", "stolen",
        "unauthorized", "fraud", "police", "deadline", "halt", "bricked"
    ]
    medium_keywords = [
        "intermittent", "sometimes", "occasionally", "frustrating", "persists",
        "keeps", "multiple times", "tried", "not working", "issue", "problem",
        "error", "confused", "discrepancy"
    ]
    low_keywords = [
        "just curious", "no rush", "not in a hurry", "just checking",
        "for my records", "when convenient", "minor", "small", "wondering",
        "interested", "would like to know", "planning"
    ]
    text_lower = text.lower() if isinstance(text, str) else ""
    feat = []
    feat.append(sum(1 for kw in urgent_keywords if kw in text_lower))
    feat.append(sum(1 for kw in medium_keywords if kw in text_lower))
    feat.append(sum(1 for kw in low_keywords if kw in text_lower))
    feat.append(len(text_lower))
    feat.append(text.count("!") if isinstance(text, str) else 0)
    feat.append(text.count("?") if isinstance(text, str) else 0)
    upper_chars = sum(1 for c in (text or "") if c.isupper())
    feat.append(upper_chars / max(len(text or "x"), 1))
    feat.append(len(text_lower.split()))
    return csr_matrix(np.array([feat]))


@app.route("/")
def index():
    """Serve the main dashboard page."""
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    """Classify a support ticket and assign priority."""
    data = request.get_json()
    ticket_text = data.get("text", "")

    if not ticket_text.strip():
        return jsonify({"error": "Ticket text is required"}), 400

    processed = preprocess_single(ticket_text)
    features = tfidf.transform([processed])

    category = category_model.predict(features)[0]

    urgency_feat = build_urgency_features_single(ticket_text)
    priority_features = hstack([features, urgency_feat])
    priority = priority_model.predict(priority_features)[0]

    priority_descriptions = {
        "Low": "Non-urgent issue that can be addressed during regular workflow",
        "Medium": "Moderate issue requiring attention within standard SLA",
        "High": "Urgent issue requiring prompt attention and escalation",
        "Critical": "Emergency issue requiring immediate action"
    }

    category_descriptions = {
        "Technical Issue": "Hardware or software malfunction requiring technical support",
        "Billing Inquiry": "Payment, invoice, or financial account related question",
        "Product Inquiry": "Questions about product features, specs, or availability",
        "Account Access": "Login, authentication, or account security related issue",
        "General Query": "General information request or feedback"
    }

    return jsonify({
        "category": category,
        "category_description": category_descriptions.get(category, ""),
        "priority": priority,
        "priority_description": priority_descriptions.get(priority, ""),
        "processed_text": processed,
        "original_text": ticket_text
    })


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Return model evaluation metrics."""
    return jsonify(metrics_data)


@app.route("/api/sample-tickets", methods=["GET"])
def sample_tickets():
    """Return sample tickets for demonstration."""
    try:
        df = pd.read_csv(DATA_PATH)
        samples = df.sample(n=10, random_state=None).to_dict(orient="records")
        return jsonify(samples)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    load_models()
    print("\n" + "=" * 60)
    print("  SUPPORT TICKET CLASSIFIER - WEB DASHBOARD")
    print("=" * 60)
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
