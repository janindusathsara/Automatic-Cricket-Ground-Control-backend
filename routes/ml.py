"""
ML Model Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from services.prediction_service import pitch_predictor
from services.weather_service import weather_service
from sensor_service import sensor_service
from utils.firebase_helper import FirebaseHelper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["ml"])


class PredictionRequest(BaseModel):
    temperature: float
    humidity: float
    light: float
    rain: int
    soilMoisture: float
    wind_kph: float
    cloud: float
    precip_mm: float
    pressure_mb: float
    dewpoint_c: float
    uv: float


@router.post("/predict")
async def predict_pitch_condition(request: PredictionRequest) -> Dict:
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
        logger.error(f"- Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-full-pipeline")
async def run_full_prediction_pipeline() -> Dict:
    try:
        logger.info("[DATA] Starting full prediction pipeline...")

        sensor_data = sensor_service.get_latest_sensor_data()
        if not sensor_data:
            raise HTTPException(status_code=500, detail="Failed to load sensor data")

        weather_data = weather_service.get_current_weather()
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        sensor_features = sensor_service.extract_ml_features(sensor_data)
        weather_features = weather_service.extract_ml_features(weather_data)

        prediction_result = pitch_predictor.predict(
            temperature=sensor_features.get("temperature", 25.0),
            humidity=sensor_features.get("humidity", 65.0),
            light=sensor_features.get("light", 700.0),
            rain=sensor_features.get("rain", 0),
            soilMoisture=sensor_features.get("soilMoisture", 45.0),
            wind_kph=weather_features.get("wind_kph", 0.0),
            cloud=weather_features.get("cloud", 0.0),
            precip_mm=weather_features.get("precip_mm", 0.0),
            pressure_mb=weather_features.get("pressure_mb", 1013.0),
            dewpoint_c=weather_features.get("dewpoint_c", 15.0),
            uv=weather_features.get("uv", 5.0),
        )

        if not prediction_result.get("success"):
            raise HTTPException(
                status_code=500, detail=prediction_result.get("error", "Prediction failed")
            )

        generated_at_time = datetime.utcnow().isoformat() + "Z"
        firebase_data = {
            "pitch_type": prediction_result.get("pitch_type"),
            "bounce": prediction_result.get("bounce"),
            "spin": prediction_result.get("spin"),
            "seam_movement": prediction_result.get("seam_movement"),
            "confidence": prediction_result.get("confidence"),
            "generated_at": generated_at_time,
        }

        firebase_written = FirebaseHelper.write("cricket_ground/prediction", firebase_data)
        if firebase_written:
            logger.info("Prediction node updated")

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
                "wind_kph": weather_data.get("wind_kph"),
                "cloud": weather_data.get("cloud"),
                "precip_mm": weather_data.get("precip_mm"),
                "pressure_mb": weather_data.get("pressure_mb"),
                "dewpoint_c": weather_data.get("dewpoint_c"),
                "uv": weather_data.get("uv"),
            },
            "firebase_written": firebase_written,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"- Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_information() -> Dict:
    try:
        return {
            "loaded": pitch_predictor.is_loaded,
            "models": pitch_predictor.targets if pitch_predictor.targets else ["pitch_type", "bounce", "spin", "seam_movement"],
            "features": pitch_predictor.features if pitch_predictor.features else [],
            "feature_count": len(pitch_predictor.features) if pitch_predictor.features else 11,
            "description": "Multi-output Random Forest classifier for cricket pitch prediction",
            "fallback_engine": "Available (rule-based)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))