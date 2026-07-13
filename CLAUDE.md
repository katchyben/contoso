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
cd backend && uv run uvicorn main:app --reload
```

Listens on `http://127.0.0.1:8000` by default. `test_main.http` contains sample requests for the existing endpoints (`/` and `/hello/{name}`) — usable directly from an editor with an HTTP client plugin, or as a reference for `curl`.

CORS is enabled for any `http://localhost:<port>` / `http://127.0.0.1:<port>` origin (see `allow_origin_regex` in `main.py`), so the frontend dev server can call it regardless of which port Vite picks.

There is no test suite, linter, or formatter configured yet.

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

## Architecture

Both apps are minimal starters, not yet split into further submodules:
- Backend: all routes are defined directly on the `app` instance in `backend/main.py`. No router/settings split yet.
- Frontend: a single `App.tsx` component, no routing or state management library.

The two apps run as independent processes (backend on 8000, frontend on Vite's dev port) and talk over plain HTTP with CORS — there is no shared build step or monorepo tooling (no workspaces, no shared package).