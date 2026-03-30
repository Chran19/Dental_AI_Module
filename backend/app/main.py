"""
Chairside Companion — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
from app.routes.clinical_input import router as clinical_input_router
from app.routes.risk_engine import router as risk_engine_router
from app.routes.diagnosis import router as diagnosis_router
from app.routes.investigation import router as investigation_router
from app.routes.treatment import router as treatment_router
from app.routes.explainability import router as explainability_router
from app.routes.image_analysis import router as image_analysis_router
from app.routes.auth import router as auth_router
from app.routes.patients import router as patients_router
from app.routes.images import router as images_router
from app.routes.implants import router as implants_router
from app.routes.queue import router as queue_router

from fastapi.staticfiles import StaticFiles
from pathlib import Path


# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan (startup / shutdown) ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


# ─── App Factory ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered prosthodontic clinical platform. "
        "Module 1: Clinical Input Processing. "
        "Module 2: Rule-Based Risk Engine."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware ───────────────────────────────────────────────────────────────

# Configure CORS - remove allow_credentials if using "*" 
cors_allow_credentials = "*" not in settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ──────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Transform Pydantic validation errors into the Module 1 error format (§10).
    Returns 422 with per-field error array.
    """
    errors = []
    for error in exc.errors():
        # Extract the field name from the location tuple
        loc = error.get("loc", ())
        field = ".".join(str(part) for part in loc if part != "body")
        errors.append({
            "field": field or "unknown",
            "message": error.get("msg", "Validation error"),
        })

    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "errors": errors,
        },
    )
    # Add CORS headers for preflight requests
    origin = request.headers.get("origin")
    if origin and "*" in settings.CORS_ORIGINS or origin in settings.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin if origin in settings.CORS_ORIGINS else "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler — returns a generic 500 per §10."""
    logger.exception("Unhandled exception: %s", str(exc))
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error."},
    )
    # Add CORS headers
    origin = request.headers.get("origin")
    if origin and ("*" in settings.CORS_ORIGINS or origin in settings.CORS_ORIGINS):
        response.headers["Access-Control-Allow-Origin"] = origin if origin in settings.CORS_ORIGINS else "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# ─── Request Size Limiting Middleware ────────────────────────────────────────

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """
    Limit request payload size.
    - File uploads to image-analysis: MAX_UPLOAD_SIZE_MB
    - Regular requests: MAX_REQUEST_BODY_MB
    """
    content_length = request.headers.get("content-length")
    if not content_length:
        return await call_next(request)
    
    content_length_int = int(content_length)
    
    # Check if this is a file upload request
    if request.url.path == "/image-analysis/upload":
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    else:
        max_bytes = settings.MAX_REQUEST_BODY_MB * 1024 * 1024
    
    if content_length_int > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": f"Request payload too large. Maximum: {max_mb}MB"},
        )
    return await call_next(request)


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(queue_router)
app.include_router(images_router)
app.include_router(implants_router)
app.include_router(clinical_input_router)

# ─── Static Files ────────────────────────────────────────────────────────────

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(risk_engine_router)
app.include_router(diagnosis_router)
app.include_router(investigation_router)
app.include_router(treatment_router)
app.include_router(explainability_router)
app.include_router(image_analysis_router)


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
