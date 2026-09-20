# Setup & Run Instructions

[← Back to README](../README.md)

> The deployed MVP is available from the [live URL](https://team-cb-001-submission.vercel.app/). These instructions are for local development when the live service is unavailable.

## Prerequisites

| Tool | Version |
|---|---|
| Node.js | `20.x` or later |
| Python | `3.11` recommended |
| PostgreSQL | `15` or later |
| Google Gemini API key | Required for live visual assessment |

## 1. Clone

```bash
git clone https://github.com/visheshdevanur/TEAM-CB001-submission.git
cd TEAM-CB001-submission
```

## 2. Environment Variables

Create the backend environment file from the provided example:

```powershell
Copy-Item src/.env.example src/.env
```

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string, for example `postgresql://user:password@localhost:5432/beforeafterai`. |
| `GEMINI_API_KEY` | Yes for AI review | Server-side Gemini key; never expose it in the frontend. |
| `AUTH_SECRET` | Yes | Long random secret used for authentication tokens. |
| `MCC_ADMIN_EMAIL` | Yes | Email for the initial MCC administrator account. |
| `MCC_ADMIN_PASSWORD` | Yes | Password for the initial MCC administrator account. |
| `UPLOAD_DIR` | No | Local temporary upload folder; evidence bytes are also persisted with the evidence record. |

> Never commit `src/.env` or a real Gemini key. Commit only `src/.env.example`.

## 3. Database and Backend

Create a local PostgreSQL database named `beforeafterai`, then install Python dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src/requirements.txt
cd src/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On first start, the API creates its tables and creates the MCC administrator from `MCC_ADMIN_EMAIL` and `MCC_ADMIN_PASSWORD` when those variables are set. There is no separate migration or seed command required for the hackathon MVP.

## 4. Frontend

In a second terminal from the repository root:

```powershell
cd src/frontend
npm install
$env:VITE_API_BASE = "http://localhost:8000"
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5176`. Create a public account, create a worker from the MCC dashboard, and allot a worker area to exercise the complete flow.

## Offline Mode

Offline complaint submission and automatic sync are not implemented in this MVP. Keep the browser online for authentication, map/address lookup, uploads, API requests, and Gemini assessment.

## Troubleshooting

| Problem | Fix |
|---|---|
| Backend cannot connect to PostgreSQL | Confirm PostgreSQL is running and `DATABASE_URL` in `src/.env` is correct. |
| Gemini result is unavailable | Confirm `GEMINI_API_KEY`, network access, and provider quota; upload clear category-matching Before/After images. |
| Browser blocks the API request | Use `http://localhost:5176` for local development or add the frontend origin to FastAPI CORS settings. |
| Port is already in use | Stop the existing process or use another port, then update `VITE_API_BASE` to match the backend port. |
