# SIF Prediction AI

AI/NLP-based system for detecting **Serious Injury & Fatality (SIF) precursors** from workplace safety reports.

## 📌 Overview

SIF Prediction AI analyzes **Unsafe Act, Unsafe Condition, and Near-Miss reports** using Natural Language Processing (NLP) and Machine Learning techniques.

The system helps identify high-risk reports and supports **proactive workplace safety management** by detecting potential SIF precursors before serious incidents occur.

## 🎯 Objectives

* Detect potential SIF precursors from safety reports
* Analyze unstructured textual safety data
* Classify reports based on risk level
* Support early identification of high-risk situations
* Help organizations improve preventive safety measures

## 🔄 Workflow
# OIL SIF Intelligence

Production-style FastAPI + vanilla JavaScript safety intelligence platform for SIH 2026 problem statement **SIH26165**. It classifies Unsafe Act, Unsafe Condition, Near Miss, and Incident narratives for Serious Injury & Fatality potential, maps critical controls to IOGP Life-Saving Rules, and tracks review work.

The included records are synthetic demo data only. They are not OIL operational data. Replace `backend/data/safety_reports.csv` with an authorized dataset after validating its schema and access controls.

## Features

- TF-IDF + class-balanced Logistic Regression baseline with saved artifacts and metrics.
- Explainable rule-based fallback when model artifacts are absent.
- SIF label, probability, risk level, activity, barrier failure, consequence, and Life-Saving Rule extraction.
- Self-service registration and login with PBKDF2 password hashing and expiring bearer sessions.
- High-risk hazard email delivery to the submitting worker and optional HSE distribution list.
- SQLite development database using SQLAlchemy models that can migrate to PostgreSQL through `DATABASE_URL`.
- Live dashboard for sites, activities, rules, trends, alerts, reports, precursor density, and corrective actions.
- Responsive HTML5/CSS3/vanilla JS frontend with Chart.js. No React or JSX.
- Pydantic validation, CORS configuration, status updates, and high-risk alert creation.

## Project structure

```text
frontend/                 Static dashboard
backend/main.py           FastAPI app and static serving
backend/database.py       SQLAlchemy engine and session
backend/models.py         users, reports, ai_analysis, alerts, actions
backend/schemas.py        API validation and response models
backend/routes/           REST endpoints
backend/services/         NLP, risk, and precursor logic
backend/ml/               Dataset generator, training, artifacts
backend/data/             Synthetic safety_reports.csv (1,000 rows)
```

## Install and run

Requirements: Python 3.11+ and a modern browser.

```powershell
cd SIF-Predict-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m backend.ml.generate_dataset
python -m backend.ml.train_model
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. The API docs are at <http://127.0.0.1:8000/docs>.

For PostgreSQL, set `DATABASE_URL` before starting, for example `postgresql+psycopg://user:password@localhost/oil_sif`. Install the matching PostgreSQL driver separately.

Optional environment variables: `APP_NAME`, `DATABASE_URL`, `CORS_ORIGINS`, and `MODEL_DIR`.

### Email alerts

Configure SMTP in the project root `.env` file before starting FastAPI. The repository includes `.env.example`; copy it to `.env` and replace the placeholders:

```powershell
Copy-Item .env.example .env
notepad .env
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

For Gmail, set `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USERNAME` and `SMTP_FROM` to the sending Gmail address, `SMTP_PASSWORD` to a Google App Password, and `HSE_ALERT_EMAILS` to comma-separated HSE recipients. `.env` is ignored by Git and must never be committed.

The app does not expose SMTP credentials in the frontend. Without `SMTP_HOST`, high-risk reports continue to be stored and surfaced in the dashboard, while the backend logs that delivery is not configured. For production, use a secret manager and a transactional provider or organizational SMTP relay.

## ML pipeline

```powershell
python -m backend.ml.generate_dataset
python -m backend.ml.train_model
```

Training performs a stratified train/test split, TF-IDF unigram/bigram extraction, balanced Logistic Regression, and writes `backend/ml/artifacts/model.joblib`, `vectorizer.joblib`, and `metrics.json`. The metrics file includes accuracy, precision, recall, F1, and confusion matrix. Class balancing prioritizes recall for SIF-Potential. A Transformer can later replace `services/nlp_engine.py` while retaining its `predict()` contract.

## API examples

Analyze and persist a report:

```powershell
$body = @{ report_text = 'Maintenance was being carried out while the equipment was still energized and proper isolation was not confirmed.'; report_type = 'Near Miss'; location = 'Duliajan Central'; department = 'Maintenance'; activity = 'Equipment Maintenance'; persist = $true } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/analysis/ -Method Post -ContentType 'application/json' -Body $body
```

Available endpoints include `POST /reports/`, `GET /reports/`, `GET /reports/{id}`, `POST /analysis/`, `GET /dashboard/stats`, `GET /dashboard/sif-trend`, `GET /dashboard/top-sites`, `GET /dashboard/top-activities`, `GET /dashboard/top-rules`, `GET /dashboard/precursors`, `GET /alerts/`, `PATCH /alerts/{id}`, `POST /actions/`, `GET /actions/`, and `PATCH /actions/{id}`.

Expected result for the demo narrative is an `Energy Isolation` mapping, high risk, a dynamically calculated probability, and a persisted high-risk alert.

## Testing

With the server running, check the complete path:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/dashboard/stats
```

Then submit the API example above and confirm the new row appears in Safety Reports, SIF Alerts, and dashboard counts. For a production deployment, add authenticated identity, PostgreSQL migrations, audit logging, rate limiting, and an authorized OIL-labelled validation set before using predictions operationally.
