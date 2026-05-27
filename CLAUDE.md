# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Russian Fishing 4 (RF4) helper web app — a monorepo with a Django/DRF backend and Vue 3 frontend. Core features: fish encyclopedia (browse/search/filter), catch recognition (upload game screenshots → object detection + OCR → extract fish species/weight/price), and JWT user auth.

## Development Commands

### Backend

```bash
cd backend
uv venv && uv sync          # create venv + install deps
cd app
python manage.py migrate
python manage.py runserver 0.0.0.0:8888   # dev server (SQLite, DEBUG=True when ENV=dev)
```

Import fish data: `python manage.py fish_import data/fish_data.json` (add `--clear` to wipe first).

Docker (production-like): `docker build -t polarsnowleopard/rf4-backend:latest backend && docker run --rm -p 9999:9999 --env-file .env polarsnowleopard/rf4-backend:latest`

### Frontend

```bash
cd frontend
yarn install
yarn dev        # Vite dev server (--host, default port 5173)
yarn build      # production build → dist/
```

### Full Stack (Docker)

```bash
docker compose up -d    # pulls backend image, serves on :9999
```

## Architecture

### Backend (`backend/app/`)

- **Django project**: `rf4/` — settings, root URL conf, ASGI/WSGI entry points
- **Apps**:
  - `wiki/` — Fish model + Catch model, REST views (`fishView.py`), serializers, management command `fish_import`
  - `user/` — registration + JWT login/refresh via `djangorestframework-simplejwt`
- **Services**: `services/catch_extractor/` — image recognition pipeline:
  1. Roboflow workflow API for fish-card object detection (`fish_cards.py`)
  2. Baidu OCR API for text extraction (`get_ocr_result.py`)
  3. Merge bounding boxes, match text to fish cards, extract structured data (`main.py`)
- **URL routing**: `rf4/urls.py` → `api/urls.py` → `user/urls.py` + `wiki/urls.py`. All API paths prefixed `/api/`.
- **DB**: SQLite in dev (`ENV=dev`), MySQL in production (configured via env vars `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- **Python version**: 3.12, managed with `uv`

### Frontend (`frontend/src/`)

- **Framework**: Vue 3 + Vite + ant-design-vue 4.x + Pinia + Vue Router
- **API layer**: `utils/request.js` — Axios instance with JWT interceptor (auto-attaches Bearer token, refreshes on 401)
- **Key views**: `FishManueList.vue`, `FishDetailView.vue`, `CatchFromImage.vue`, `Agent.vue`
- **API base URL**: hardcoded in `utils/request.js` (`baseURL`), points to production by default — change for local dev

### External Service Dependencies

- **Roboflow** — object detection workflow (requires `ROBOFLOW_API_KEY` env var)
- **Baidu OCR** — text recognition (requires `BAIDU_API_KEY` + `BAIDU_SECRET_KEY` env vars)

## CI/CD

Backend only (`.github/workflows/backend-cicd.yml`): on push to `main` → build Docker image → push to Docker Hub → SSH deploy to production server. Frontend has no CI pipeline (runs `yarn dev` on prod).

## Key Conventions

- `APPEND_SLASH = False` — Django URLs do NOT use trailing slashes
- Backend uses `ENV=dev` env var to toggle debug mode and SQLite vs MySQL
- Production backend runs via Gunicorn + Uvicorn workers on port 9999
- CORS is configured for `http://fdueblab.cn:5173` only

## Git Commit Rules

- Do NOT add `Co-Authored-By` lines to commit messages
