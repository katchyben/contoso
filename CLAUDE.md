# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A FastAPI backend paired with a React frontend, split into `backend/` and `frontend/` directories.

## Backend (`backend/`)

FastAPI app (`main.py`). Dependencies managed with `uv` (see `pyproject.toml` / `uv.lock`). Requires Python >=3.13.

Install dependencies:
```
cd backend && uv sync
```

Run the dev server (auto-reload):
```
cd backend && uv run uvicorn app.main:app --reload
```

Listens on `http://127.0.0.1:8000` by default. `test_main.http` contains sample requests for the existing endpoints (`/` and `/hello/{name}`) — usable directly from an editor with an HTTP client plugin, or as a reference for `curl`.

CORS is enabled for any `http://localhost:<port>` / `http://127.0.0.1:<port>` origin (see `allow_origin_regex` in `main.py`), so the frontend dev server can call it regardless of which port Vite picks.

Config is loaded from `backend/.env` (via `python-dotenv`, wired up in `app/__init__.py`); see `backend/.env.example` for the variables it reads (`DATABASE_URL`, `JWT_SECRET_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`).

The customer support chatbot (`app/services/chat_service.py`) is grounded via a local Ollama model (`mistral` by default, no API key needed) rather than a hosted LLM API — see `OLLAMA_BASE_URL`/`OLLAMA_MODEL` above. Ollama runs natively on the host (not as a docker-compose service or k8s pod); pull the model once with `ollama pull mistral` before expecting real replies — until then `ChatService` falls back to a canned message. docker-compose and k8s point `OLLAMA_BASE_URL` at `http://host.docker.internal:11434` to reach this same host-installed Ollama.

Backend has a pytest suite (`backend/tests/`) covering services, repositories, and routers (incl. the `/ws/chat` websocket) against an in-memory SQLite DB — no external services needed:
```
cd backend && uv run pytest
```

There is no linter or formatter configured yet.

## End-to-end tests (`e2e/`)

Playwright-based (Python) browser tests that drive the real frontend + backend + Postgres together, via this project's `docker-compose.yml`. Separate `uv` project from `backend/` since it has its own dependency set (`playwright`, `pytest-playwright`).

```
docker compose up -d                                            # from repo root: db + backend + frontend
cd backend && DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/contoso" uv run python seed.py
cd e2e && uv sync && uv run playwright install chromium          # one-time setup
uv run pytest
```

Tests assume the seeded fixture logins from `backend/seed.py` (`ada.lovelace@example.com` / `customer123`, `admin@contoso.local` / `admin123`). The chat widget test tolerates either a real Ollama reply or the graceful fallback message — it doesn't require the model to be pulled, since it only asserts that *some* assistant reply arrives.

If you've changed `backend/pyproject.toml` since the backend container was last built, its `.venv` (an anonymous Docker volume, isolated from `backend/.venv` on the host) can go stale and crash-loop on missing imports. Fix with `docker compose exec backend uv sync --locked` followed by `docker compose restart backend`, or `docker compose build backend` if you have registry access.

## Frontend (`frontend/`)

Vite + React + TypeScript. Calls the backend directly via `fetch` against `http://127.0.0.1:8000` (see `API_BASE` in `src/App.tsx`) — no proxy is configured.

Install dependencies:
```
cd frontend && npm install
```

Run the dev server:
```
cd frontend && npm run dev
```

Type-check:
```
cd frontend && npx tsc --noEmit
```

Build:
```
cd frontend && npm run build
```

## Kubernetes (`k8s/`)

Plain YAML manifests for running the full stack (Postgres, MinIO, backend, frontend) on a local cluster (minikube or kind) — this is the active, documented deployment path for local use. See `k8s/README.md` for build/load/apply/access steps.

`ansible/` (EC2 provisioning + native install) still exists in the repo but is no longer the recommended path — left in place, untouched, superseded by `k8s/` for local use.

## Architecture

Both apps are minimal starters, not yet split into further submodules:
- Backend: all routes are defined directly on the `app` instance in `backend/main.py`. No router/settings split yet.
- Frontend: a single `App.tsx` component, no routing or state management library.

The two apps run as independent processes (backend on 8000, frontend on Vite's dev port) and talk over plain HTTP with CORS — there is no shared build step or monorepo tooling (no workspaces, no shared package).