# MeetFlow AI — Production Deployment Guide

## 1. Architecture Overview

- **Frontend**: Vite SPA hosted on Vercel, Netlify, or Render Static Site.
- **Backend**: FastAPI modular monolith hosted on Render, Fly.io, or AWS ECS.
- **Database**: Managed PostgreSQL (e.g. Neon, Supabase, Render PostgreSQL, AWS RDS).
- **AI Inference**: NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`).

---

## 2. Environment Variables

### Backend (`.env`)
```bash
APP_ENV=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/meetflow
JWT_SECRET_KEY=<generate-strong-random-64-char-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
NVIDIA_API_KEY=<your-nvidia-nim-key>
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
FRONTEND_URL=https://meetflow-ai.vercel.app
BACKEND_PUBLIC_URL=https://meetflow-api.onrender.com
UPLOAD_MAX_SIZE_MB=15
```

### Frontend (`frontend/.env.production`)
```bash
VITE_API_BASE_URL=https://meetflow-api.onrender.com/api/v1
```

---

## 3. Render Deployment (Backend)

1. Connect your GitHub repository to Render.
2. Create a new **Web Service**.
3. Set Environment to **Python 3.11+**.
4. Build Command:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Start Command:
   ```bash
   cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
6. Add the environment variables specified above.
7. Connect managed PostgreSQL database.

---

## 4. Vercel Deployment (Frontend)

1. Connect your GitHub repository to Vercel.
2. Set Root Directory to `frontend`.
3. Framework Preset: **Vite**.
4. Build Command: `npm run build`.
5. Output Directory: `dist`.
6. Add `VITE_API_BASE_URL` in environment variables.
7. Verify SPA routing with `vercel.json`:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```

---

## 5. Docker Deployment

Build and run both services using docker-compose:
```bash
docker compose up --build
```
This boots PostgreSQL, runs migrations, spins up FastAPI on port 8000, and starts the Nginx-served React frontend on port 80.

