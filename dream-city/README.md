# Dream Atlas

Dream Atlas is a bilingual Arabic/English web application that turns a written dream into a weighted semantic profile, maps it to one of **240 fictional city profiles**, and renders the selected city as a lightweight procedural 3D scene.

The project is designed to run locally, in Docker, or as two independently deployed services. It does not require API keys or hosted AI services for the default experience.

## What the pipeline does

```text
Dream text
   ↓
Arabic / English analysis
   ↓
Signals + metrics + weighted dream vector
   ↓
240 city-profile similarity ranking
   ↓
Scene configuration
   ↓
Procedural Three.js city
```

The analysis keeps contradictory concepts instead of reducing the dream to one keyword. The selected profile controls terrain, architecture, density, roads, water, vegetation, weather, lighting, sky and landmark parameters in the existing 3D renderer.

## Stack

- **Frontend:** React 18 + TypeScript + Vite + React Three Fiber / Three.js
- **Backend:** FastAPI + Pydantic + Uvicorn
- **Data:** JSON lexicon + 240 city templates
- **Deployment:** Docker Compose with an Nginx frontend reverse-proxying `/api` to FastAPI
- **CI:** GitHub Actions for backend tests and frontend production build

## Repository structure

```text
.
├── backend/
│   ├── app/
│   │   ├── analyzer.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── scene_config.py
│   │   └── services.py
│   ├── data/
│   │   ├── city_templates.json
│   │   └── lexicon.json
│   ├── tests/
│   │   └── test_analyzer.py
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── nginx/default.conf
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── tsconfig*.json
│   └── vite.config.ts
├── scripts/
│   └── generate_city_catalog.py
├── .github/workflows/ci.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Requirements

For local development:

- Python 3.11+
- Node.js 20+
- npm 10+

For Docker deployment:

- Docker Engine with Compose v2

## Environment configuration

Copy `.env.example` to `.env` when you need local environment overrides.

Important variables:

| Variable | Purpose | Local default |
|---|---|---|
| `ENVIRONMENT` | Runtime environment label | `development` |
| `APP_NAME` | Backend service name | `Dream Atlas API` |
| `APP_VERSION` | API version string | `1.0.0` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:5173` |
| `VITE_API_URL` | API origin for separately hosted frontend | empty |

No secret, token, database password, or API key is required by the default project.

## Run locally

### Backend

Linux/macOS:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend endpoints:

- `GET /api/health` — health/readiness information
- `GET /api/cities` — city catalog summary
- `POST /api/analyze` — dream analysis
- `/docs` — FastAPI OpenAPI documentation

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

During development, Vite proxies `/api/*` to `http://localhost:8000`, so the browser uses the same API path as production.

For a separately hosted API, set `VITE_API_URL` to the public API origin before building.

## Docker deployment

The included Compose setup is the recommended simple production path for a single VM/server.

```bash
docker compose up --build -d
```

Then open:

```text
http://localhost
```

Architecture:

```text
Browser
  │
  ▼
Nginx :80
  ├── /        → React static files
  └── /api/*   → backend:8000
                    │
                    └── FastAPI
```

The backend has a Docker health check on `/api/health`, and Compose waits for that health check before starting the frontend service.

### HTTPS / public hosting

For a public server, put the Compose stack behind an HTTPS reverse proxy/load balancer such as Caddy, Traefik, or a cloud load balancer. Terminate TLS there and forward traffic to the frontend container on port 80.

If frontend and API are deployed on different domains, set `VITE_API_URL` at frontend build time and set `CORS_ORIGINS` on the backend to the exact frontend origin(s), for example:

```text
CORS_ORIGINS=https://dream.example.com
VITE_API_URL=https://api.example.com
```

Do not use `*` for production CORS unless that behavior is deliberately required.

## Production compatibility

The production frontend intentionally defaults `VITE_API_URL` to an empty string. That makes requests relative to the current origin (`/api/analyze`). The Docker Nginx configuration proxies those requests to FastAPI, avoiding a hard-coded `localhost` API URL in production.

For local development, Vite's proxy keeps the same `/api` contract while forwarding to port 8000.

## Testing

Backend tests:

```bash
cd backend
python -m pytest -q
```

Frontend production build:

```bash
cd frontend
npm install
npm run build
```

GitHub Actions runs both automatically for pushes to `main`/`master` and pull requests.

## GitHub workflow

A clean checkout can be used directly:

```bash
git clone <your-repository-url>
cd dream-city
```

No generated `node_modules`, Python virtual environment, cache, editor settings, `.env`, or build output is committed. `.gitignore` excludes these local artifacts.

The repository contains no application secrets. `.env.example` documents configuration without storing credentials.

## Updating the city catalog

The catalog is stored in `backend/data/city_templates.json` and currently contains 240 profiles.

If the generator is changed:

```bash
python scripts/generate_city_catalog.py
```

Run the backend tests after regenerating the catalog.

## Extending the analysis engine

Add bilingual lexical concepts to `backend/data/lexicon.json`. The analyzer supports weighted evidence, phrase matching, modifiers, negation, repetition and derived emotional/atmospheric metrics.

Keep the analyzer and city-profile contract stable when adding a future semantic model. The default project intentionally remains deterministic and does not require an external AI provider.

## Security and production notes

- Do not commit `.env` files or credentials.
- Keep `CORS_ORIGINS` explicit in production.
- Serve the public application through HTTPS.
- Keep the backend behind the frontend reverse proxy or a protected API gateway where appropriate.
- The health endpoint exposes only service status and catalog count; it does not expose secrets or configuration values.
- The JSON catalog is read-only application data. A database is unnecessary unless the catalog becomes user-editable or substantially larger.

## Current verification

The backend test suite passes locally. Frontend dependency installation was attempted in the build environment; the package installation timed out before dependencies became available, so a successful local production frontend build could not be claimed in this environment. GitHub Actions is configured to perform a clean `npm install` and `npm run build` on GitHub.

## License

No license has been imposed by the project yet. Add a `LICENSE` file before distributing the repository publicly if you want to grant explicit reuse rights.


## Final Polish

- 240 city profiles remain data-driven; the renderer consumes `SceneConfig`, so adding city 241 only requires adding catalog data.
- Backend exposes `/api/health` for liveness and `/api/ready` for readiness.
- Production frontend uses same-origin `/api` through Nginx; local Vite development proxies `/api` to port 8000.
- No API keys or credentials are required by the application. Keep `.env` local and commit only `.env.example`.
- CI runs backend tests and the frontend production build on GitHub Actions.

### Clean install

```bash
cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pytest -q
cd ../frontend && npm ci && npm run check
```

### Docker

```bash
docker compose up --build
```

Open `http://localhost`; the frontend proxies `/api` to the backend container.
