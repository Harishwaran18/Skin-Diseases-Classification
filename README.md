# SkinCare AI — AI-Assisted Skin-Health Monitoring

A production-style web prototype for AI-assisted skin-health monitoring, symptom
tracking, trigger analysis, treatment adherence, trend monitoring, AI image
screening (demo/mock model), and PDF reporting.

> ⚠️ **Screening / monitoring tool only — never diagnostic.**
> SkinCare AI does **not** diagnose skin conditions and cannot replace a
> qualified healthcare professional. AI results are produced by a **demo
> model** and are illustrative only. If you are experiencing a medical
> emergency, seek care immediately.

## Features

- **Auth & profiles** — JWT auth, per-user private data, patient profile, full data export.
- **Symptom tracking** — 8-dimension 0–5 scale (itching, redness, dryness, pain, swelling, irritation, burning, scaling) + lesion count, with 30-day trend analysis (rolling average + slope-based direction).
- **Trigger analysis** — log lifestyle/food/environmental triggers; correlation engine computes symptom lift after each trigger vs. baseline.
- **Treatment adherence** — track treatments, mark completed/skipped, per-treatment and overall adherence %.
- **AI image screening** — secure upload with quality gate (blur/brightness/resolution), demo classifier with calibrated-style probabilities, severity estimate, and an explicit reliability threshold. Low-confidence predictions report **no category** and recommend consultation.
- **Honest AI uncertainty** — confidence threshold, `reliable` flag, attention/explainability note (clearly labelled as synthetic for the demo), and persistent disclaimers on every AI output.
- **Risk level engine** — Green / Yellow / Red based on trend + severity, with templated, non-diagnostic messaging and an emergency disclaimer.
- **PDF reports** — doctor-friendly ReportLab PDF: patient info, symptom summary, trigger associations, adherence, AI results, optional images, disclaimer footer.
- **Dashboard** — aggregated overview: today's score, trend, adherence, risk, recent triggers, reminders, latest screening.
- **Privacy** — images stored privately per user, owner-only access, full JSON data export.

## Architecture

```
skin-diseases-classification/
├── backend/                  # FastAPI + SQLAlchemy + Pydantic
│   ├── app/
│   │   ├── api/routers/      # auth, profile, symptoms, triggers, treatments, images, ai, reports, dashboard
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # business logic + analytics (trend, risk, trigger correlation)
│   │   ├── ai/               # image_quality gate, safety/disclaimer layer
│   │   ├── core/             # config, database session
│   │   └── utils/            # errors, ids
│   ├── requirements.txt
│   └── Dockerfile
├── ml/                       # ML inference (strategy pattern)
│   ├── inference/
│   │   ├── classifier.py     # abstract interface + PredictionResult
│   │   ├── demo_backend.py   # deterministic mock (default)
│   │   ├── torch_backend.py  # real model backend (optional, requires torch)
│   │   └── factory.py        # backend selection
│   ├── models/               # architecture scaffold (not trained)
│   ├── preprocessing/        # transforms
│   ├── training/             # stub (out of scope)
│   └── evaluation/           # stub (out of scope)
├── frontend/                 # React + Vite + Recharts
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # Navbar, common UI
│   │   ├── context/          # Auth context
│   │   ├── pages/            # Login, Dashboard, Symptoms, Triggers, Images, Treatments, Reports, Profile
│   │   └── styles/
│   ├── Dockerfile            # multi-stage build → nginx
│   └── package.json
├── docker-compose.yml        # db (postgres) + backend + frontend
└── .env.example
```

## Quick start (local dev)

### 1. Backend

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env       # defaults to sqlite + demo AI backend
uvicorn app.main:app --reload --port 12000
```

API docs at `http://localhost:12000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI at `http://localhost:5173` (proxies `/api` to the backend).

### 3. Smoke test

```bash
cd backend
# with the backend running on :12000
python scripts/smoke_test.py
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:12000`
- Postgres: `localhost:5432`

## AI backend selection

Set `AI_BACKEND`:
- `demo` (default) — deterministic mock classifier. No model is loaded; results are illustrative.
- `torch` — loads a real checkpoint from `AI_MODEL_PATH` (requires `torch`/`torchvision`, see `ml/requirements-ml.txt`). Falls back to `demo` with a notice if unavailable.

> **No model is trained or distributed in this repository.** The `ml/models`,
> `ml/training`, and `ml/evaluation` packages are scaffolds. The integration
> path exists, but no accuracy or clinical validity is claimed.

## Safety & ethics

- **Non-diagnostic by design** — every AI response, report, and dashboard view includes a disclaimer.
- **Honest uncertainty** — predictions below the confidence threshold (`AI_CONFIDENCE_THRESHOLD`, default 0.55) report `reliable: false`, omit the category, and recommend consultation.
- **Quality gate** — images failing blur/brightness/resolution checks are stored but blocked from AI analysis.
- **Privacy** — per-user storage isolation, owner-only image serving, JWT auth on all endpoints, full data export.
- **Risk messaging** — templated, cautious, never asserts a diagnosis; includes an emergency disclaimer.

## Tech stack

- **Backend:** FastAPI, SQLAlchemy 2, Pydantic v2, python-jose (JWT), passlib/bcrypt, ReportLab, Pillow, OpenCV (headless)
- **Frontend:** React 18, Vite 5, React Router 6, Recharts
- **DB:** SQLite (dev) / PostgreSQL (docker)
- **ML:** numpy, Pillow; optional torch/torchvision

## License

Prototype / demonstration. Not a medical device.