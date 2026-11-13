# Deploy & handoff notes (menumatch-coffee-app)

Portable setup notes for continuing work outside Cursor (e.g. Claude Code).  
**No secrets are stored in this file.** Keep real values in `.env` (local) and Render / Supabase dashboards.

## What this app is

- **FastAPI** backend (`main.py` / `app.py`) + static Encinitas coffee guide (`encinitas.html`).
- Data lives in **Supabase** (`restaurants`, `menus`, `menu_versions`).
- Production host is **Render** (Procfile → uvicorn). Root `/` serves `encinitas.html`; API under `/menus/...` and `/api/...`.
- Theme Studio (`theme-studio.html`) talks to `/api/theme` and can sync via BroadcastChannel / `?preset=` / `?studio-preview=1`.

## GitHub

| Item | Value |
|------|--------|
| Repo | https://github.com/tmccardle/menumatch-coffee-app |
| Default branch | `main` |
| Ignore secrets | `.env` is in `.gitignore` — never commit it |

Useful local commands:

```bash
git clone https://github.com/tmccardle/menumatch-coffee-app
cd menumatch-coffee-app
python -m venv .venv && source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
cp .env.example .env   # create if missing; see env vars below
python app.py          # http://localhost:8000
```

Optional seed (API must be running; needs write key):

```bash
export MENU_API_BASE=http://localhost:8000
export MENU_WRITE_KEY=...   # same value as server
python seed_encinitas.py
```

## Environment variables

Required for the API process (`database.py` loads `.env` next to the project root):

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Preferred public/anon key (also accepts `SUPABASE_KEY` or `SUPABASE_SERVICE_ROLE_KEY`) |
| `MENU_WRITE_KEY` | Shared secret for mutating routes; send as header `X-Menu-Key`. If unset, writes return 503 |

Optional (seed script only):

| Variable | Default | Purpose |
|----------|---------|---------|
| `MENU_API_BASE` | `http://localhost:8000` | Base URL for `seed_encinitas.py` |

Example `.env` (do not commit):

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJ...
MENU_WRITE_KEY=long-random-string
```

## Supabase

Tables used by `routers/menus.py`:

1. **`restaurants`** — `name`, `city`, `area`, `address`, `website`, …
2. **`menus`** — `restaurant_id`, `title`, …
3. **`menu_versions`** — schema in `menu_versions.sql` (`raw_menu`, `parsed_menu`, `characterization`, `is_current`, version trigger)

Read path used by the guide: `GET /menus/restaurants` (enriched with current menu versions).

Write paths (need `X-Menu-Key`):

- `POST /menus/restaurants`
- `POST /menus/`
- `POST /menus/versions`

Apply / verify SQL in the Supabase SQL editor from `menu_versions.sql` (and ensure `restaurants` / `menus` exist to match the API). Prefer the **anon** key for the Render service if RLS allows the intended reads; use service role only if you knowingly bypass RLS.

Fill in for your project (not in git):

- Project ref / URL: `________________`
- Dashboard: `https://supabase.com/dashboard/project/________________`

## Render

| Item | Notes |
|------|--------|
| Start command | `web: uvicorn main:app --host 0.0.0.0 --port $PORT` (`Procfile`) |
| Runtime | Python; deps from `requirements.txt` |
| Env vars on Render | Same as above: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (or alias), `MENU_WRITE_KEY` |
| Public site | `/` → Encinitas guide; `/api` → readiness JSON; `/theme-studio.html` → Theme Studio |

Frontend API base (`encinitas.html` → `defaultApiBase()`):

- Local static ports `8085` / `5500` / `5501` → `hostname:8000`
- On Render (or any same-origin host) → **`location.origin`** (do not hardcode `:8000` on HTTPS)
- If the API call fails / hangs, UI falls back to bundled **sample shops** so the list is never blank

Fill in:

- Render service URL: `https://________________.onrender.com`
- Auto-deploy from `main`: yes / no — `____`

Smoke checks after deploy:

```bash
curl -sS https://YOUR-RENDER-HOST/api
curl -sS https://YOUR-RENDER-HOST/menus/restaurants
```

Open the Render root in a browser and confirm shops load from the API (status line), not only sample data.

## Local vs Cloud Agent (Cursor context)

From prior Cursor Cloud Agent chat (this machine was attached to a different repo by mistake):

- **Cloud Agents** clone GitHub into an ephemeral VM. Laptop-only files and local `.env` are **not** available unless pushed / configured as Cloud Agent secrets.
- **Remote Control** (iPhone → laptop) keeps tools on the computer: local checkout, Docker, Supabase keys in `.env` stay local; the laptop must stay awake and online.
- Durable artifacts for Claude Code: this **GitHub repo**, **Render** service + env, **Supabase** project + schema/data. Cursor chat history and `.cursor/rules` are not required if this file + env dashboards are complete.

This repo had **no `.cursor/rules`** at handoff time. Important operational facts are captured here instead.

## API surface (quick map)

| Method | Path | Auth |
|--------|------|------|
| GET | `/` | public — Encinitas HTML |
| GET | `/api` | public — ready message |
| GET/POST | `/api/theme` | public — reads/writes `active_theme.json` on disk |
| GET | `/menus/restaurants` | public — shops + current menus |
| GET | `/menus/`, `/menus/{id}/versions` | public |
| POST | `/menus/restaurants`, `/menus/`, `/menus/versions` | `X-Menu-Key` |

Entry points: `python app.py` (port 8000) or uvicorn via Procfile on Render.

## Checklist for Claude Code

1. Clone `tmccardle/menumatch-coffee-app` and install `requirements.txt`.
2. Recreate `.env` from Render / Supabase (never from git).
3. Confirm Supabase tables match the API + `menu_versions.sql`.
4. Run locally; hit `/menus/restaurants`; seed if empty.
5. On Render, confirm env vars and that the live guide uses same-origin API (not `:8000`).
6. Do not commit `.env`, service-role keys, or `MENU_WRITE_KEY`.
