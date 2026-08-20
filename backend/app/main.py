# ============================================================
# FastAPI Main Application Entrypoint
# ============================================================

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware.auth import init_firebase
from app.services.csv_ingestion import ingest_rules_into_firestore
from app.routers import health, reviews, rules

# Configure application logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler:
    - Runs on startup: initializes Firebase Admin and ingests CSV historical rules into Firestore.
    - Runs on shutdown: cleans up resources.
    """
    logger.info("Initializing Multi-Agent AI Code Reviewer Backend...")

    # 1. Initialize Firebase Admin SDK
    init_firebase()

    # 2. Ingest CSV rules into Firestore
    try:
        rule_count = ingest_rules_into_firestore()
        logger.info(f"Startup rule ingestion completed: {rule_count} rules loaded.")
    except Exception as e:
        logger.warning(f"Startup rule ingestion notice: {e}")

    logger.info("Backend service is ready to accept requests.")
    yield
    logger.info("Shutting down Multi-Agent AI Code Reviewer Backend...")


# Initialize FastAPI application
app = FastAPI(
    title="Multi-Agent AI Code Reviewer API",
    description="Serverless API orchestrating 7 specialized AI agents to deliver scored code reviews.",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_origin_regex=r"https://.*\.a\.run\.app|http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Router Registration ─────────────────────────────────────
app.include_router(health.router)
app.include_router(reviews.router)
app.include_router(rules.router)


@app.get("/", tags=["Root"])
async def root():
    """Root metadata endpoint."""
    return {
        "name": "Multi-Agent AI Code Reviewer API",
        "status": "operational",
        "docs_url": "/docs",
        "health_check": "/api/v1/health",
    }
