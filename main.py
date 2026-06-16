"""
Cricket Ground Automation System - Backend
FastAPI application entry point

Data Flow:
Weather API → Firebase Weather → Sensor Data → ML Model → Prediction → Firebase
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
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
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
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
try:
    FirebaseHelper.initialize()
    logger.info("✓ Firebase initialized successfully")
except Exception as e:
    logger.warning(f"⚠ Firebase initialization warning: {str(e)}")


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
        "firebase_initialized": True,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/docs")
async def api_documentation():
    """API Documentation"""
    return {
        "endpoints": {
            "prediction": {
                "POST /ml/predict": "Make multi-output prediction with 11 features",
                "POST /ml/run-full-pipeline": "Run complete pipeline (sensor+weather+predict+save)",
                "GET /ml/model-info": "Get model information",
            },
            "weather": {
                "GET /weather/current": "Get current weather from Weather API",
            },
            "sensors": {
                "GET /sensors/latest": "Get latest sensor data from Firebase",
            },
        },
        "ml_features": [
            "temperature", "humidity", "light", "rain", "soilMoisture",
            "wind_kph", "cloud", "precip_mm", "pressure_mb", "dewpoint_c", "uv"
        ],
        "ml_outputs": [
            "pitch_type", "bounce", "spin", "seam_movement"
        ]
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
    """Run the FastAPI application"""
    print("\n" + "=" * 60)
    print("🏏 Cricket Ground Automation Backend")
    print("=" * 60)
    print(f"Environment: {Config.APP_ENV}")
    print(f"Host: {Config.HOST}:{Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print("=" * 60)

    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
    )
        log_level="info",
    )


if __name__ == "__main__":
    main()
