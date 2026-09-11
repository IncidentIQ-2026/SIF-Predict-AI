from pathlib import Path
import re
import joblib

from ..config import settings
from .precursor_engine import extract_precursors
from .risk_engine import risk_level

ARTIFACT_DIR = Path(settings.model_dir)
KEYWORDS = ("energized", "isolation", "lockout", "confined", "height", "suspended", "excavat", "line of fire", "unprotected", "no permit", "failed")


def _fallback_probability(text: str) -> float:
    normalized = text.lower()
    matches = sum(keyword in normalized for keyword in KEYWORDS)
    return min(0.94, 0.12 + matches * 0.16)


def predict(text: str, activity: str = "General Operations") -> dict:
    probability = None
    model_path = ARTIFACT_DIR / "model.joblib"
    vectorizer_path = ARTIFACT_DIR / "vectorizer.joblib"
    if model_path.exists() and vectorizer_path.exists():
        try:
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            probability = float(model.predict_proba(vectorizer.transform([text]))[0][1])
        except Exception:
            probability = None
    probability = probability if probability is not None else _fallback_probability(text)
    precursor = extract_precursors(text, activity)
    label = "SIF-Potential" if probability >= 0.5 else "Non-SIF-Potential"
    rule = precursor["life_saving_rule"]
    explanation = f"The report contains indicators associated with {rule}. The model and control vocabulary estimate {probability:.0%} SIF potential; HSE verification is required."
    return {"sif_label": label, "sif_probability": round(probability, 4), "risk_level": risk_level(probability), **precursor, "explanation": explanation}
