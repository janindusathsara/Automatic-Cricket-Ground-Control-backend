"""
Sensor data service - reads sensor data from Firebase RTDB
"""

from firebase_config import FirebaseDB
from datetime import datetime
from typing import Optional, Dict


class SensorService:
    """Service for handling sensor data from Firebase"""

    SENSORS_PATH = "cricket_ground/sensors"

    @classmethod
    def get_latest_sensor_data(cls) -> Optional[Dict]:
        """
        Get the latest sensor data from Firebase
        Expected Firebase structure:
        cricket_ground/sensors/
            soil_moisture: value
            light_intensity: value
            temperature: value
            humidity: value
            timestamp: value
        """
        try:
            sensor_data = FirebaseDB.read(cls.SENSORS_PATH)

            if not sensor_data:
                # Return default values if no data exists
                return cls._get_default_sensor_data()

            return {
                "soil_moisture": sensor_data.get("soil_moisture", 0),
                "light_intensity": sensor_data.get("light_intensity", 0),
                "temperature": sensor_data.get("temperature", 20),
                "humidity": sensor_data.get("humidity", 50),
                "timestamp": sensor_data.get("timestamp", datetime.now().isoformat()),
            }

        except Exception as e:
            print(f"✗ Error fetching sensor data: {str(e)}")
            return cls._get_default_sensor_data()

    @classmethod
    def _get_default_sensor_data(cls) -> Dict:
        """Return default sensor data structure"""
        return {
            "soil_moisture": 0,
            "light_intensity": 0,
            "temperature": 20,
            "humidity": 50,
            "timestamp": datetime.now().isoformat(),
        }

    @classmethod
    def get_sensor_history(cls, limit: int = 10) -> Optional[Dict]:
        """Get historical sensor data (if available)"""
        try:
            return FirebaseDB.read(f"{cls.SENSORS_PATH}/history")
        except Exception as e:
            print(f"✗ Error fetching sensor history: {str(e)}")
            return None

    @classmethod
    def extract_ml_features(cls, sensor_data: Dict) -> Dict:
        """Extract and normalize sensor features for ML model"""
        if not sensor_data:
            return None

        return {
            "soil_moisture": sensor_data.get("soil_moisture", 0),
            "light_intensity": sensor_data.get("light_intensity", 0),
            "temperature": sensor_data.get("temperature", 20),
            "humidity": sensor_data.get("humidity", 50),
        }


# Create singleton instance
sensor_service = SensorService()
