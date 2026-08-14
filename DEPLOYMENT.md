# 🚀 Deployment Guide: Vercel & Neon Serverless PostgreSQL

This guide walks you through deploying the **Autonomous Multi-Agent Research Platform** to **Vercel** with a cloud-native **Neon PostgreSQL** database.

---

## 🏗️ Architecture Overview

- **Frontend**: Django Web App running on Vercel Serverless Function (`frontend/api/index.py` + WhiteNoise static assets)
- **Backend**: FastAPI Multi-Agent Engine running on Vercel Serverless Function (`backend/api/index.py`)
- **Database**: Neon Serverless PostgreSQL (`neon.tech`) with auto-scaling & branching
- **Routing**: Unified `vercel.json` edge routing

---

## 1. 🐘 Step 1: Set Up Neon Database (neon.tech)

1. Go to [Neon Console](https://console.neon.tech/) and create a free project (e.g. `research-platform`).
2. Copy your **PostgreSQL Connection String**. It will look like:
   ```text
   postgresql://alex:AbCdEfGh123@ep-cool-resonance-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. *(Optional)* Run Alembic or direct table migration from local terminal:
   ```bash
   cd backend
   # In backend/.env set: DATABASE_URL=postgresql://alex:AbCdEfGh123@ep-cool-resonance-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   python test_postgres_connection.py
   ```
   *(Note: The FastAPI backend automatically initializes all tables on startup as well!)*

---

## 2. ▲ Step 2: Deploy to Vercel

### Method A: Single-Click Unified Monorepo (Recommended)

1. Push your repository to **GitHub** / **GitLab**.
2. Open the [Vercel Dashboard](https://vercel.com/new) and **Import** your repository.
3. Keep **Root Directory** as `./` (default).
4. Under **Environment Variables**, add the following:

| Variable | Description | Example Value |
|---|---|---|
| `DATABASE_URL` | Neon PostgreSQL Connection String | `postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require` |
| `SECRET_KEY` | Application Secret Key | `generate-a-secure-random-string` |
| `DEFAULT_PROVIDER` | Default LLM Provider | `gemini` (or `groq`, `nvidia`, `openrouter`) |
| `DEFAULT_MODEL` | Default LLM Model | `gemini-2.5-flash` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIzaSy...` |
| `TAVILY_API_KEY` | Tavily Search API Key | `tvly-...` |
| `GROQ_API_KEY` | *(Optional)* Groq API Key | `gsk_...` |
| `NVIDIA_API_KEY` | *(Optional)* NVIDIA NIM API Key | `nvapi-...` |
| `OPENROUTER_API_KEY` | *(Optional)* OpenRouter Key | `sk-or-...` |

5. Click **Deploy**. Vercel will build both the FastAPI backend (`/api/*`) and Django frontend (`/*`) automatically using the root `vercel.json`.

---

### Method B: Split Deployment (Independent Frontend & Backend)

If you prefer two separate Vercel projects:

#### 1. Backend Project
- **Root Directory**: `backend`
- **Build Settings**: Detected via `backend/vercel.json`
- **Environment Variables**: Add `DATABASE_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY`.
- After deploy, copy the generated URL: `https://your-backend.vercel.app`.

#### 2. Frontend Project
- **Root Directory**: `frontend`
- **Build Settings**: Detected via `frontend/vercel.json`
- **Environment Variables**:
  - `BACKEND_URL`: `https://your-backend.vercel.app`
  - `DATABASE_URL`: Your Neon connection string
  - `SECRET_KEY`: Your secret key

---

## 3. 🔍 Step 3: Verify Your Deployment

1. Visit your Vercel deployment URL (e.g. `https://your-project.vercel.app/`).
2. Log in / Sign up to access your workspace.
3. Start a new research task in the **Research Wizard**.
4. Check real-time execution streaming and report generation.

---

## 🛠️ Local Development with Neon DB

To test locally with your Neon PostgreSQL database:

1. In `backend/.env`:
   ```env
   DATABASE_URL=postgresql://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
2. Start FastAPI Backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
3. Start Django Frontend:
   ```bash
   cd frontend
   python manage.py runserver 3000
   ```
