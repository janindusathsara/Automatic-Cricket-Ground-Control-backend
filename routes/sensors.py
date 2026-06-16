"""
Sensor Routes
GET /sensors/latest - Get latest sensor data from Firebase
GET /sensors/history - Get sensor data history
"""

from fastapi import APIRouter, HTTPException
from sensor_service import sensor_service
from typing import Dict, Optional

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/latest")
async def get_latest_sensors() -> Dict:
    """
    Get latest sensor data from Firebase RTDB
    
    Returns:
        {
            "success": true,
            "data": {
                "soil_moisture": 65,
                "light_intensity": 450,
                "temperature": 22,
                "humidity": 60,
                "timestamp": "2024-01-01T12:00:00"
            }
        }
    """
    try:
        sensor_data = sensor_service.get_latest_sensor_data()

        if not sensor_data:
            raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

        return {"success": True, "data": sensor_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features")
async def get_sensor_ml_features() -> Dict:
    """
    Get sensor features extracted for ML model
    
    Returns extracted sensor features
    """
    try:
        sensor_data = sensor_service.get_latest_sensor_data()

        if not sensor_data:
            raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

        features = sensor_service.extract_ml_features(sensor_data)

        return {
            "success": True,
            "features": features,
            "sensor_data": sensor_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_sensor_history(limit: Optional[int] = None) -> Dict:
    """
    Get historical sensor data from Firebase
    
    Args:
        limit: Number of records to retrieve (optional)
    
    Returns:
        Historical sensor data
    """
    try:
        history = sensor_service.get_sensor_history(limit=limit)

        return {
            "success": True,
            "data": history,
            "message": "Sensor history retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
