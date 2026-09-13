import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).parents[1] / ".env")


class Settings:
    app_name = os.getenv("APP_NAME", "SIF-Predict AI")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./sif_intelligence.db")
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
    model_dir = os.getenv("MODEL_DIR", "backend/ml/artifacts")
    auth_secret = os.getenv("AUTH_SECRET", "dev-only-change-this-secret")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", "alerts@sif-predict-ai.local")
    smtp_starttls = os.getenv("SMTP_STARTTLS", "true").lower() == "true"


settings = Settings()
