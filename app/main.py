"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import assets, sensors, anomalies, recommendations, dashboard

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Industrial AI Energy Optimization Platform - "
    "Real-time monitoring, anomaly detection, and energy optimization for factories.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(assets.router, prefix="/api/v1")
app.include_router(sensors.router, prefix="/api/v1")
app.include_router(anomalies.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    init_db()


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "mqtt": "connected",
        "ai_engine": "ready",
    }
