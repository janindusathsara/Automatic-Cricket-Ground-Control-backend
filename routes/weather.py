"""
Weather API Routes
GET /weather/current - Get current weather data
"""

from fastapi import APIRouter, HTTPException
from weather_service import weather_service
from firebase_config import FirebaseDB
from typing import Dict

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current")
async def get_current_weather() -> Dict:
    """
    Get current weather data from Weather API
    
    Returns:
        {
            "provider": "weatherapi",
            "city": "London",
            "temperature": 22.5,
            "humidity": 65,
            "condition": "Partly Cloudy",
            "wind_speed": 12,
            "pressure": 1013,
            "precipitation": 0,
            "cloud_coverage": 35,
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    try:
        weather_data = weather_service.get_current_weather()

        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        # Optionally store in Firebase
        try:
            FirebaseDB.write("cricket_ground/weather/current", weather_data)
        except Exception as e:
            print(f"⚠ Warning: Could not write to Firebase: {str(e)}")

        return {"success": True, "data": weather_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features")
async def get_weather_ml_features() -> Dict:
    """
    Get weather features extracted for ML model
    
    Returns extracted and normalized features
    """
    try:
        weather_data = weather_service.get_current_weather()

        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        features = weather_service.extract_ml_features(weather_data)

        return {
            "success": True,
            "features": features,
            "weather_data": weather_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
