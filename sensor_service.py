"""
Sensor data service - reads sensor data from Firebase RTDB
Reads from: cricket_ground/data
"""

from utils.firebase_helper import FirebaseHelper
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SensorService:
    """Service for handling sensor data from Firebase"""

    SENSORS_PATH = "cricket_ground/data"

    @classmethod
    def get_latest_sensor_data(cls) -> Optional[Dict]:
        """
        Get the latest sensor data from Firebase
        Expected Firebase structure:
        cricket_ground/data/
            temperature: value
            humidity: value
            light: value
            rain: boolean
            soilMoisture: value
        """
        try:
            sensor_data = FirebaseHelper.read(cls.SENSORS_PATH)

            if not sensor_data:
                logger.warning("⚠ No sensor data found in Firebase")
                return cls._get_default_sensor_data()

            result = {
                "temperature": sensor_data.get("temperature", 25),
                "humidity": sensor_data.get("humidity", 65),
                "light": sensor_data.get("light", 700),
                "rain": bool(sensor_data.get("rain", False)),
                "soilMoisture": sensor_data.get("soilMoisture", 45),
                "timestamp": sensor_data.get("timestamp", datetime.now().isoformat()),
            }
            
            logger.info("✓ Sensor data loaded")
            return result

        except Exception as e:
            logger.error(f"✗ Error fetching sensor data: {str(e)}")
            return cls._get_default_sensor_data()

    @classmethod
    def _get_default_sensor_data(cls) -> Dict:
        """Return default sensor data structure"""
        return {
            "temperature": 25,
            "humidity": 65,
            "light": 700,
            "rain": False,
            "soilMoisture": 45,
            "timestamp": datetime.now().isoformat(),
        }

    @classmethod
    def get_sensor_history(cls, limit: int = 10) -> Optional[Dict]:
        """Get historical sensor data (if available)"""
        try:
            return FirebaseHelper.read(f"{cls.SENSORS_PATH}/history")
        except Exception as e:
            logger.error(f"✗ Error fetching sensor history: {str(e)}")
            return None

    @classmethod
    def extract_ml_features(cls, sensor_data: Dict) -> Dict:
        """Extract and normalize sensor features for ML model"""
        if not sensor_data:
            sensor_data = cls._get_default_sensor_data()

        # Convert rain boolean to numeric (1 or 0)
        rain_numeric = 1 if sensor_data.get("rain", False) else 0

        return {
            "temperature": sensor_data.get("temperature", 25),
            "humidity": sensor_data.get("humidity", 65),
            "light": sensor_data.get("light", 700),
            "rain": rain_numeric,
            "soilMoisture": sensor_data.get("soilMoisture", 45),
        }


# Create singleton instance
sensor_service = SensorService()
