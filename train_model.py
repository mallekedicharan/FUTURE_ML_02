import pandas as pd
import numpy as np
import os
import json
import re
import string
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_PATH = os.path.join(BASE_DIR, "support_tickets.csv")


def download_nltk_data():
    """Download required NLTK data packages."""
    packages = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass


def load_data():
    """Load the support ticket dataset."""
    print("\n[1/6] Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Loaded {len(df)} tickets")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  Ticket Type distribution:")
    for cat, count in df["Ticket Type"].value_counts().items():
        print(f"    {cat}: {count}")
    print(f"\n  Priority distribution:")
    for pri, count in df["Ticket Priority"].value_counts().items():
        print(f"    {pri}: {count}")
    return df


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


def preprocess_texts(texts):
    """Preprocess a list of texts: clean, tokenize, remove stopwords, lemmatize."""
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    processed = []

    for text in texts:
        cleaned = clean_text(text)
        tokens = word_tokenize(cleaned)
        tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
        processed.append(" ".join(tokens))

    return processed


def preprocess_data(df):
    """Preprocess the dataset texts."""
    print("\n[2/6] Preprocessing text data...")

    df["combined_text"] = df["Ticket Subject"].fillna("") + " " + df["Ticket Description"].fillna("")

    print("  Cleaning text (lowercasing, removing punctuation, stopwords)...")
    df["processed_text"] = preprocess_texts(df["combined_text"].tolist())

    print(f"  Sample original: {df['combined_text'].iloc[0][:100]}...")
    print(f"  Sample cleaned:  {df['processed_text'].iloc[0][:100]}...")

    return df


def extract_features(train_texts, test_texts):
    """Extract TF-IDF features from text data."""
    print("\n[3/6] Extracting TF-IDF features...")

    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )

    X_train = tfidf.fit_transform(train_texts)
    X_test = tfidf.transform(test_texts)

    print(f"  Vocabulary size: {len(tfidf.vocabulary_)}")
    print(f"  Training features shape: {X_train.shape}")
    print(f"  Test features shape: {X_test.shape}")

    top_features = sorted(tfidf.vocabulary_.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"  Top features: {[f[0] for f in top_features]}")

    return X_train, X_test, tfidf


def train_category_model(X_train, y_train, X_test, y_test):
    """Train the ticket category classification model using LinearSVC."""
    print("\n[4/6] Training Category Classifier (LinearSVC)...")

    model = LinearSVC(
        C=1.0,
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print(f"\n  Category Classification Results:")
    print(f"  {'='*40}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n  Confusion Matrix:")
    labels = sorted(set(y_test))
    print(f"  Labels: {labels}")
    for i, row in enumerate(cm):
        print(f"    {labels[i]}: {row}")

    return model, {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": labels
    }


def build_urgency_features(texts_original):
    """Build handcrafted urgency features from original (uncleaned) text."""
    from scipy.sparse import csr_matrix

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

    features = []
    for text in texts_original:
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
        features.append(feat)

    return csr_matrix(np.array(features))


def train_priority_model(X_train, y_train, X_test, y_test, train_originals, test_originals):
    """Train the ticket priority classification model using Random Forest."""
    from scipy.sparse import hstack
    print("\n[5/6] Training Priority Classifier (Random Forest)...")

    train_urgency = build_urgency_features(train_originals)
    test_urgency = build_urgency_features(test_originals)

    X_train_combined = hstack([X_train, train_urgency])
    X_test_combined = hstack([X_test, test_urgency])

    print(f"  Combined features shape: {X_train_combined.shape} (TF-IDF + urgency)")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=40,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2
    )
    model.fit(X_train_combined, y_train)

    y_pred = model.predict(X_test_combined)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print(f"\n  Priority Classification Results:")
    print(f"  {'='*40}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    priority_order = ["Low", "Medium", "High", "Critical"]
    labels = sorted(set(y_test), key=lambda x: priority_order.index(x) if x in priority_order else 99)

    print(f"\n  Confusion Matrix:")
    print(f"  Labels: {labels}")
    cm_ordered = confusion_matrix(y_test, y_pred, labels=labels)
    for i, row in enumerate(cm_ordered):
        print(f"    {labels[i]}: {row}")

    return model, {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "classification_report": report,
        "confusion_matrix": cm_ordered.tolist(),
        "labels": labels
    }


def save_models(tfidf, category_model, priority_model, category_metrics, priority_metrics):
    """Save all models and metrics to disk."""
    print("\n[6/6] Saving models and metrics...")

    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(tfidf, os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(category_model, os.path.join(MODELS_DIR, "category_model.joblib"))
    joblib.dump(priority_model, os.path.join(MODELS_DIR, "priority_model.joblib"))

    metrics = {
        "category": category_metrics,
        "priority": priority_metrics
    }

    with open(os.path.join(MODELS_DIR, "evaluation_results.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"  Models saved to: {MODELS_DIR}")
    print(f"  Files: tfidf_vectorizer.joblib, category_model.joblib, priority_model.joblib")
    print(f"  Metrics: evaluation_results.json")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("  SUPPORT TICKET CLASSIFICATION - MODEL TRAINING")
    print("=" * 60)

    download_nltk_data()

    df = load_data()

    df = preprocess_data(df)

    train_idx, test_idx = train_test_split(
        df.index, test_size=0.2, random_state=42, stratify=df["Ticket Type"]
    )

    train_df = df.loc[train_idx]
    test_df = df.loc[test_idx]

    X_train_text = train_df["processed_text"].tolist()
    X_test_text = test_df["processed_text"].tolist()

    X_train, X_test, tfidf = extract_features(X_train_text, X_test_text)

    category_model, category_metrics = train_category_model(
        X_train, train_df["Ticket Type"].tolist(), X_test, test_df["Ticket Type"].tolist()
    )

    train_originals = train_df["combined_text"].tolist()
    test_originals = test_df["combined_text"].tolist()

    priority_model, priority_metrics = train_priority_model(
        X_train, train_df["Ticket Priority"].tolist(),
        X_test, test_df["Ticket Priority"].tolist(),
        train_originals, test_originals
    )

    save_models(tfidf, category_model, priority_model, category_metrics, priority_metrics)

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print("=" * 60)
    print(f"\n  Category Model Accuracy:  {category_metrics['accuracy']:.2%}")
    print(f"  Priority Model Accuracy:  {priority_metrics['accuracy']:.2%}")
    print(f"\n  Run 'python app.py' to start the web dashboard!")
    print("=" * 60)


if __name__ == "__main__":
    main()
