import os


class Settings:
    app_name = os.getenv("APP_NAME", "OIL SIF Intelligence")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./sif_intelligence.db")
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
    model_dir = os.getenv("MODEL_DIR", "backend/ml/artifacts")


settings = Settings()
