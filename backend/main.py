from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, engine
from .routes import actions, alerts, analysis, dashboard, reports

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(reports.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(actions.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


frontend = Path(__file__).parents[1] / "frontend"
if frontend.exists():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
