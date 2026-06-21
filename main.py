"""
Cricket Ground Automation System - Backend
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import Config
from utils.firebase_helper import FirebaseHelper
from routes import weather, sensors, ml
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cricket Ground Automation Backend",
    description="Multi-output ML-powered cricket pitch prediction system",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase early
try:
    FirebaseHelper.initialize()
except Exception as e:
    logger.warning(f"! Firebase initialization warning: {str(e)}")

# Include routers
app.include_router(weather.router)
app.include_router(sensors.router)
app.include_router(ml.router)


@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "service": "Cricket Ground Automation Backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": Config.APP_ENV,
        "features": [
            "Multi-output ML prediction",
            "Weather API integration",
            "Firebase RTDB storage",
            "Rule-based fallback engine",
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "firebase_initialized": FirebaseHelper._initialized,
        "timestamp": datetime.now().isoformat(),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("        Cricket Cricket Ground Automation Backend")
    print("=" * 60)
    print(f"Environment: {Config.APP_ENV}")
    print(f"Host: {Config.HOST}:{Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info",
    )