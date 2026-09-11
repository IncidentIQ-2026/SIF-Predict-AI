from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).parents[2]
DATA = ROOT / "backend" / "data" / "safety_reports.csv"
ARTIFACTS = ROOT / "backend" / "ml" / "artifacts"


def main():
    frame = pd.read_csv(DATA)
    labels = (frame["sif_label"] == "SIF-Potential").astype(int)
    train_text, test_text, train_labels, test_labels = train_test_split(frame["report_text"], labels, test_size=0.2, random_state=42, stratify=labels)
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    train_vectors = vectorizer.fit_transform(train_text)
    test_vectors = vectorizer.transform(test_text)
    model = LogisticRegression(class_weight="balanced", max_iter=1000)
    model.fit(train_vectors, train_labels)
    predictions = model.predict(test_vectors)
    metrics = {"accuracy": accuracy_score(test_labels, predictions), "classification_report": classification_report(test_labels, predictions, target_names=["Non-SIF", "SIF"], output_dict=True), "confusion_matrix": confusion_matrix(test_labels, predictions).tolist(), "priority": "Recall is prioritized using balanced class weights."}
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACTS / "model.joblib")
    joblib.dump(vectorizer, ARTIFACTS / "vectorizer.joblib")
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
