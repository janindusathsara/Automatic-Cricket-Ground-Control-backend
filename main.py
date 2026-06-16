"""
Cricket Ground Automation System - Backend
FastAPI application entry point

Data Flow:
Weather API → FastAPI → Firebase Sensor Data → ML Model → Prediction → Firebase RTDB Update
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import Config
from firebase_config import FirebaseDB
from routes import weather, sensors, ml
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Cricket Ground Automation Backend",
    description="ML-powered pitch condition prediction system",
    version="1.0.0",
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
    FirebaseDB.initialize()
except Exception as e:
    print(f"⚠ Firebase initialization warning: {str(e)}")


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
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": Config.APP_ENV,
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
            "weather": {
                "GET /weather/current": "Get current weather data from Weather API",
                "GET /weather/features": "Get weather features for ML model",
            },
            "sensors": {
                "GET /sensors/latest": "Get latest sensor data from Firebase",
                "GET /sensors/features": "Get sensor features for ML model",
                "GET /sensors/history": "Get sensor data history",
            },
            "ml": {
                "POST /ml/predict": "Make a single pitch prediction",
                "POST /ml/run-full-pipeline": "Run complete pipeline (weather + sensors + predict)",
                "POST /ml/batch-predict": "Make batch predictions",
                "GET /ml/model-info": "Get ML model information",
            },
        },
        "data_flow": "Weather API → FastAPI → Firebase Sensors → ML Model → Prediction → Firebase RTDB",
    }


@app.get("/database-structure")
async def database_structure():
    """Firebase Database Structure Guide"""
    return {
        "firebase_structure": {
            "cricket_ground/": {
                "sensors/": {
                    "soil_moisture": "float",
                    "light_intensity": "float",
                    "temperature": "float",
                    "humidity": "float",
                    "timestamp": "string",
                },
                "weather/": {
                    "current": {
                        "temperature": "float",
                        "humidity": "float",
                        "condition": "string",
                        "timestamp": "string",
                    }
                },
                "ml/": {
                    "pitch_report/": {
                        "prediction": "string (Dry Pitch | Wet Pitch | Balanced Pitch)",
                        "confidence": "float",
                        "timestamp": "string",
                    }
                },
            }
        },
        "notes": "Set Firebase Security Rules to allow read/write for authenticated users",
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


def main():
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
        log_level="info",
    )


if __name__ == "__main__":
    main()
