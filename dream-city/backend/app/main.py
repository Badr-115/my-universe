from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import load_cities
from .config import get_settings
from .models import AnalyzeResponse, DreamRequest
from .services import analyze_dream

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    """Liveness/readiness endpoint used by Docker and deployment platforms."""
    catalog_size = len(load_cities())
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment, "cities": catalog_size}


@app.get("/api/ready")
def ready() -> dict:
    """Readiness check: verifies both catalog and lexicon can be loaded."""
    from .analyzer import load_lexicon
    catalog_size = len(load_cities())
    lexicon_size = len(load_lexicon())
    return {"status": "ready", "cities": catalog_size, "lexicon_entries": lexicon_size}


@app.get("/api/cities")
def cities() -> dict:
    catalog = load_cities()
    return {"count": len(catalog), "cities": [{"id": c.id, "name": c.name, "name_ar": c.name_ar} for c in catalog]}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(payload: DreamRequest):
    text = payload.dream.strip()
    if len(text) < 3:
        raise HTTPException(status_code=422, detail="Dream text is too short to analyze.")
    try:
        return analyze_dream(text, payload.language)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Dream analysis failed. Please try again.") from exc
