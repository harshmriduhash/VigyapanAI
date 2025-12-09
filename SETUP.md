# VigyapanAI SaaS MVP Setup

This project now uses FastAPI + Redis + RQ, Supabase auth, Replicate + Gemini for hosted generation/analysis, and S3 for storage.

## Prerequisites
- Python 3.10+
- Node 18+
- Redis (local or managed)
- FFmpeg available on PATH (already installed in the backend Dockerfile)
- Supabase project (URL, anon key, JWT secret)
- S3 bucket + creds (or R2 with S3 compatibility)
- Replicate API token and Google Gemini API key

## Environment
Use `backend/env.example.txt` as a template. Required vars:
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_JWT_SECRET=          # Supabase JWT secret/service role key
REPLICATE_API_TOKEN=
GOOGLE_API_KEY=
S3_BUCKET=
S3_REGION=
S3_ENDPOINT=                  # optional
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:8080
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=3600
```
Frontend `.env` (create in `frontend/.env.local`):
```
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=<SUPABASE_URL>
VITE_SUPABASE_ANON_KEY=<SUPABASE_ANON_KEY>
```

## Run locally
Backend API:
```
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Worker:
```
cd backend
.\.venv\Scripts\activate
python worker.py
```
Redis:
```
redis-server
```
Frontend:
```
cd frontend
npm install
npm run dev -- --host --port 8080
```

## Docker
```
docker-compose up --build
```
Ensure env vars are exported in your shell (compose passes Supabase vars to frontend).

## Smoke tests
1) Auth: Sign up/login via frontend; verify token stored.
2) Generate: Submit generator form; poll job completes; video download via signed URL.
3) Analyze: Provide a reachable MP4 URL; poll analysis job; get report link.
4) Rate limit: Hit `/generate` > limit to confirm 429.

## Deployment notes
- Set `FRONTEND_URL` to your production domain; keep CORS restricted.
- Run API + worker + Redis; ensure ffmpeg available (Dockerfile already installs it).
- Monitor Replicate/Gemini usage; adjust `RATE_LIMIT_*` for cost control.

