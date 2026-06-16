"""
ML Model Routes
POST /ml/predict - Make a multi-output prediction with all 11 features
POST /ml/run-full-pipeline - Get weather + sensors + predict + save to Firebase
GET /ml/model-info - Get model information
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from ml_prediction import pitch_predictor
from weather_service import weather_service
from sensor_service import sensor_service
from utils.firebase_helper import FirebaseHelper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ml"])


class PredictionRequest(BaseModel):
    """Request model for multi-output prediction"""

    temperature: float
    humidity: float
    light: float
    rain: int  # 1 or 0
    soilMoisture: float
    wind_kph: float
    cloud: float
    precip_mm: float
    pressure_mb: float
    dewpoint_c: float
    uv: float


@router.post("/predict")
async def predict_pitch_condition(request: PredictionRequest) -> Dict:
    """
    Make a multi-output prediction for cricket pitch characteristics
    
    Returns:
        {
            "success": true,
            "pitch_type": "Batting Friendly",
            "bounce": "High & Consistent",
            "spin": "Low",
            "seam_movement": "Low",
            "confidence": 0.87,
            "timestamp": "2026-06-16T..."
        }
    """
    try:
        result = pitch_predictor.predict(
            temperature=request.temperature,
            humidity=request.humidity,
            light=request.light,
            rain=request.rain,
            soilMoisture=request.soilMoisture,
            wind_kph=request.wind_kph,
            cloud=request.cloud,
            precip_mm=request.precip_mm,
            pressure_mb=request.pressure_mb,
            dewpoint_c=request.dewpoint_c,
            uv=request.uv,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-full-pipeline")
async def run_full_prediction_pipeline() -> Dict:
    """
    Run complete prediction pipeline:
    
    Step 1: Read sensor data from cricket_ground/data
    Step 2: Fetch current weather from Weather API (auto-saves to cricket_ground/weather)
    Step 3: Combine sensor + weather features
    Step 4: Run multi-output ML prediction
    Step 5: Write prediction to cricket_ground/prediction
    Step 6: Return response
    
    Returns:
        {
            "success": true,
            "prediction": {
                "pitch_type": "Batting Friendly",
                "bounce": "High & Consistent",
                "spin": "Low",
                "seam_movement": "Low",
                "confidence": 0.87
            },
            "sensor_data": {...},
            "weather_data": {...},
            "firebase_written": true,
            "timestamp": "2026-06-16T..."
        }
    """
    try:
        logger.info("📊 Starting full prediction pipeline...")

        # Step 1: Read sensor data from Firebase
        logger.info("Step 1: Reading sensor data from Firebase...")
        sensor_data = sensor_service.get_latest_sensor_data()
        if not sensor_data:
            raise HTTPException(status_code=500, detail="Failed to load sensor data")

        # Step 2: Fetch weather data (automatically saves to Firebase)
        logger.info("Step 2: Fetching weather data from Weather API...")
        weather_data = weather_service.get_current_weather()
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        # Step 3: Extract ML features
        logger.info("Step 3: Preparing ML features...")
        sensor_features = sensor_service.extract_ml_features(sensor_data)
        weather_features = weather_service.extract_ml_features(weather_data)

        # Step 4: Run prediction
        logger.info("Step 4: Running prediction...")
        prediction_result = pitch_predictor.predict(
            temperature=sensor_features.get("temperature", 25),
            humidity=sensor_features.get("humidity", 65),
            light=sensor_features.get("light", 700),
            rain=sensor_features.get("rain", 0),
            soilMoisture=sensor_features.get("soilMoisture", 45),
            wind_kph=weather_features.get("wind_kph", 0),
            cloud=weather_features.get("cloud", 0),
            precip_mm=weather_features.get("precip_mm", 0),
            pressure_mb=weather_features.get("pressure_mb", 1013),
            dewpoint_c=weather_features.get("dewpoint_c", 15),
            uv=weather_features.get("uv", 5),
        )

        if not prediction_result.get("success"):
            raise HTTPException(
                status_code=500, detail=prediction_result.get("error", "Prediction failed")
            )

        logger.info("✓ Prediction generated")

        # Step 5: Write to Firebase
        logger.info("Step 5: Writing prediction to Firebase...")
        firebase_data = {
            "pitch_type": prediction_result.get("pitch_type"),
            "bounce": prediction_result.get("bounce"),
            "spin": prediction_result.get("spin"),
            "seam_movement": prediction_result.get("seam_movement"),
            "confidence": prediction_result.get("confidence"),
            "timestamp": datetime.now().isoformat(),
        }

        firebase_written = FirebaseHelper.write("cricket_ground/prediction", firebase_data)
        if firebase_written:
            logger.info("✓ Prediction node updated")
        else:
            logger.warning("⚠ Failed to write prediction to Firebase")

        # Step 6: Prepare response
        logger.info("✓ Pipeline completed successfully")

        return {
            "success": True,
            "prediction": {
                "pitch_type": prediction_result.get("pitch_type"),
                "bounce": prediction_result.get("bounce"),
                "spin": prediction_result.get("spin"),
                "seam_movement": prediction_result.get("seam_movement"),
                "confidence": prediction_result.get("confidence"),
            },
            "sensor_data": sensor_data,
            "weather_data": {
                "temperature": weather_data.get("temperature"),
                "condition": weather_data.get("condition"),
                "wind_kph": weather_data.get("wind_kph"),
                "cloud": weather_data.get("cloud"),
                "precip_mm": weather_data.get("precip_mm"),
            },
            "firebase_written": firebase_written,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_information() -> Dict:
    """
    Get information about the trained ML models
    
    Returns:
        {
            "loaded": true,
            "models": ["pitch_type", "bounce", "spin", "seam_movement"],
            "features": [11 feature names],
            "description": "Multi-output cricket pitch prediction model"
        }
    """
    try:
        return {
            "loaded": pitch_predictor.is_loaded,
            "models": pitch_predictor.targets,
            "features": pitch_predictor.features,
            "feature_count": len(pitch_predictor.features) if pitch_predictor.features else 0,
            "description": "Multi-output Random Forest classifier for cricket pitch prediction",
            "fallback_engine": "Available (rule-based)",
        }

    except Exception as e:
        logger.error(f"✗ Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
