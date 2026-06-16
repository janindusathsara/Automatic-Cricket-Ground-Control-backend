"""
ML Model Routes
POST /ml/predict - Make a single prediction
POST /ml/run-full-pipeline - Get weather + sensors + predict + save to Firebase
GET /ml/model-info - Get model information
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from ml_prediction import pitch_predictor
from weather_service import weather_service
from sensor_service import sensor_service
from firebase_config import FirebaseDB
from datetime import datetime

router = APIRouter(prefix="/ml", tags=["ml"])


class PredictionRequest(BaseModel):
    """Request model for direct prediction"""

    humidity: float
    temperature: float
    soil_moisture: float
    light_intensity: float


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""

    predictions: list


@router.post("/predict")
async def predict_pitch_condition(request: PredictionRequest) -> Dict:
    """
    Make a prediction using provided sensor data
    
    Args:
        humidity: Humidity percentage (0-100)
        temperature: Temperature in Celsius
        soil_moisture: Soil moisture level (0-100)
        light_intensity: Light intensity in lumens
    
    Returns:
        {
            "success": true,
            "prediction": "Balanced Pitch",
            "confidence": 0.87,
            "all_predictions": {
                "Wet Pitch": 0.05,
                "Dry Pitch": 0.08,
                "Balanced Pitch": 0.87
            }
        }
    """
    try:
        result = pitch_predictor.predict(
            request.humidity, request.temperature, request.soil_moisture, request.light_intensity
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-full-pipeline")
async def run_full_prediction_pipeline() -> Dict:
    """
    Run complete pipeline:
    1. Fetch current weather from Weather API
    2. Fetch latest sensor data from Firebase
    3. Combine data and run ML prediction
    4. Write result to Firebase under cricket_ground/ml/pitch_report
    
    Returns:
        {
            "success": true,
            "weather": {...},
            "sensors": {...},
            "prediction": "Balanced Pitch",
            "confidence": 0.87,
            "firebase_written": true,
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    try:
        # Step 1: Get weather data
        weather_data = weather_service.get_current_weather()
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        # Step 2: Get sensor data
        sensor_data = sensor_service.get_latest_sensor_data()
        if not sensor_data:
            raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

        # Step 3: Make prediction
        prediction_result = pitch_predictor.predict(
            humidity=sensor_data.get("humidity", 50),
            temperature=sensor_data.get("temperature", 20),
            soil_moisture=sensor_data.get("soil_moisture", 0),
            light_intensity=sensor_data.get("light_intensity", 0),
        )

        if not prediction_result.get("success"):
            raise HTTPException(
                status_code=500, detail=prediction_result.get("error", "Prediction failed")
            )

        # Step 4: Prepare output
        output = {
            "success": True,
            "weather": weather_data,
            "sensors": sensor_data,
            "prediction": prediction_result.get("prediction"),
            "confidence": prediction_result.get("confidence"),
            "all_predictions": prediction_result.get("all_predictions"),
            "timestamp": datetime.now().isoformat(),
        }

        # Step 5: Write to Firebase
        firebase_written = False
        try:
            pitch_report = {
                "prediction": prediction_result.get("prediction"),
                "confidence": prediction_result.get("confidence"),
                "all_predictions": prediction_result.get("all_predictions"),
                "weather": weather_data,
                "sensors": sensor_data,
                "timestamp": datetime.now().isoformat(),
            }

            firebase_written = FirebaseDB.write("cricket_ground/ml/pitch_report", pitch_report)
            output["firebase_written"] = firebase_written

        except Exception as e:
            print(f"⚠ Warning: Could not write to Firebase: {str(e)}")
            output["firebase_written"] = False
            output["firebase_error"] = str(e)

        return output

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-predict")
async def batch_predict_pitch_conditions(request: BatchPredictionRequest) -> Dict:
    """
    Make predictions on multiple samples
    
    Args:
        predictions: List of dicts with humidity, temperature, soil_moisture, light_intensity
    
    Returns:
        List of predictions
    """
    try:
        result = pitch_predictor.batch_predict(request.predictions)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_information() -> Dict:
    """
    Get information about the trained ML model
    
    Returns:
        {
            "loaded": true,
            "model_type": "RandomForestClassifier",
            "features": ["humidity", "temperature", "soil_moisture", "light_intensity"],
            "classes": ["Dry Pitch", "Wet Pitch", "Balanced Pitch"],
            "feature_importances": {...}
        }
    """
    try:
        info = pitch_predictor.get_model_info()
        return info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
