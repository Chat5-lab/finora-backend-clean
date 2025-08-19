# Finora Backend (Starter)
![Tests](https://github.com/Chat5-lab/finora-backend-clean/actions/workflows/ci.yml/badge.svg)
A ready-to-run **FastAPI + SQLite** backend starter for **Finora**.

## Quick start
1. Create a new **Python** app in Replit.
2. Upload all files from this folder into your app.
3. In the Shell: `pip install -r requirements.txt`
4. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Open `/docs`.

## Endpoints
- `GET /health`
- `POST /accountant`
- `GET /accountant`
- `POST /accountant/invite`
- `POST /accountant/accept`
- `POST /accountant/revoke`

## GitHub workflow
1. Create private repo `finora-backend`.
2. Upload these files to GitHub.
3. In Replit: Import from GitHub.
## Features
- FastAPI app with auto docs at `/docs` (Swagger) and `/redoc`
- `/` redirects to `/docs`
- Health endpoint with build metadata
- SQLite by default; switchable via `DATABASE_URL`
- Minimal CI workflow on GitHub Actions (Python 3.11)

## Quick start (Replit)
1. Open the Replit for this repo.
2. Press **Run**. The `.replit` config calls `bash run.sh`, which:
   - creates/uses `.venv`
   - installs `requirements.txt`
   - starts `uvicorn` on port **8000**
3. Click the **Open in a new tab** icon in the preview, then visit `/docs`.

## Quick start (Local)
