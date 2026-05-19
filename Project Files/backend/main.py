"""
IntelliSQL — FastAPI Backend Entry Point

Central application setup:
- CORS middleware
- Route registration
- Database initialization on startup
- Health check endpoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.database import init_db

# ── Route imports ─────────────────────────────────────────────
from routes.auth import router as auth_router
from routes.generate import router as generate_router
from routes.execute import router as execute_router
from routes.history import router as history_router


# ── Lifespan: runs on startup / shutdown ──────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    print("[STARTING] IntelliSQL backend...")
    init_db()
    print("[OK] Database tables verified.")
    yield
    print("[STOPPED] IntelliSQL backend shut down.")


# ── App factory ───────────────────────────────────────────────

app = FastAPI(
    title="IntelliSQL API",
    description="Intelligent SQL Querying with LLMs — FastAPI Backend",
    version="2.0.0",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register routers ─────────────────────────────────────────

app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(execute_router)
app.include_router(history_router)


# ── Root health check ────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "app": "IntelliSQL API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Detailed health check — verifies DB connectivity."""
    from models.database import engine
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "cors_origins": settings.cors_origin_list,
    }
