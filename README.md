# CodeTrace

CodeTrace is a C++ execution visualizer. The current milestone implements the Sprint 0/1 backend spike and `/api/trace` endpoint.

## Local setup

```powershell
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python backend/spike.py
pytest -q backend/tests
uvicorn app.main:app --app-dir backend --reload
```

POST source code to `http://localhost:8000/api/trace` as `{ "code": "..." }`.

For chat, copy `backend/.env.example` to `backend/.env` and set `NIM_API_KEY`. The actual `.env` file is ignored by Git and must never be committed.

Tracing limits are configurable with `CODETRACE_MAX_STEPS` (default 2000) and `CODETRACE_MAX_SECONDS` (default 20).

Snippets use local SQLite by default (`backend/codetrace.db`). Set `CODETRACE_DB_PATH` to use another location. The API stores source code only and recomputes its execution trace when loaded: `POST /api/snippets` then `GET /api/snippets/{id}`.

## CI and deployment

GitHub Actions builds the backend container, runs the GDB tests with network and resource limits, then builds the frontend. Render can deploy the backend using `render.yaml`; set `NIM_API_KEY` and `CODETRACE_ALLOWED_ORIGIN` in the Render dashboard. Deploy `frontend` to Vercel with `VITE_API_URL` pointing at the Render service.

The tracer compiles with debug symbols and no optimization, uses GDB/MI for line and local-variable state, caps execution at five seconds/2000 steps, and captures program stdout separately. Public deployment must run the service in a container with no network, memory/CPU/PID limits, and a non-root user; the included compose file provides the local baseline.
