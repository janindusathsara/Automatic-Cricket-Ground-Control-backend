"""
Weather API integration service
Supports WeatherAPI and OpenWeatherMap
Stores weather data to Firebase RTDB
"""

import requests
from datetime import datetime
from config import Config
from typing import Optional, Dict
from utils.firebase_helper import FirebaseHelper
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """Weather data retrieval service"""

    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.provider = Config.WEATHER_API_PROVIDER
        self.city = Config.WEATHER_API_CITY

    def get_current_weather(self) -> Optional[Dict]:
        """
        Get current weather data and store to Firebase
        Returns temperature, humidity, conditions
        """
        try:
            if self.provider == "weatherapi":
                weather_data = self._get_weatherapi_data()
            elif self.provider == "openweather":
                weather_data = self._get_openweather_data()
            else:
                logger.error(f"✗ Unknown weather provider: {self.provider}")
                return None

            if weather_data:
                # Store to Firebase
                self._store_to_firebase(weather_data)
                logger.info("✓ Weather fetched successfully")
            
            return weather_data
            
        except Exception as e:
            logger.error(f"✗ Error fetching weather: {str(e)}")
            return None

    def _get_weatherapi_data(self) -> Optional[Dict]:
        """Fetch from WeatherAPI.com"""
        url = "https://api.weatherapi.com/v1/current.json"
        params = {"key": self.api_key, "q": self.city, "aqi": "yes"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            "provider": "weatherapi",
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "condition": data["current"]["condition"]["text"],
            "wind_kph": data["current"]["wind_kph"],
            "pressure_mb": data["current"]["pressure_mb"],
            "precip_mm": data["current"]["precip_mm"],
            "cloud": data["current"]["cloud"],
            "dewpoint_c": data["current"]["dewpoint_c"],
            "uv": data["current"]["uv"],
            "last_updated": data["current"]["last_updated"],
            "timestamp": datetime.now().isoformat(),
        }

    def _get_openweather_data(self) -> Optional[Dict]:
        """Fetch from OpenWeatherMap"""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": self.city, "appid": self.api_key, "units": "metric"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            "provider": "openweather",
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "wind_kph": data["wind"]["speed"] * 3.6,  # m/s to kph
            "pressure_mb": data["main"]["pressure"],
            "precip_mm": data.get("rain", {}).get("1h", 0),
            "cloud": data["clouds"]["all"],
            "dewpoint_c": data["main"].get("dew_point", data["main"]["temp"] - 5),
            "uv": data.get("uvi", 5),
            "last_updated": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat(),
        }

    def _store_to_firebase(self, weather_data: Dict):
        """Store weather data to Firebase"""
        try:
            firebase_data = {
                "wind_kph": weather_data.get("wind_kph", 0),
                "cloud": weather_data.get("cloud", 0),
                "precip_mm": weather_data.get("precip_mm", 0),
                "pressure_mb": weather_data.get("pressure_mb", 1013),
                "dewpoint_c": weather_data.get("dewpoint_c", 15),
                "uv": weather_data.get("uv", 5),
                "last_updated": weather_data.get("last_updated", ""),
                "timestamp": weather_data.get("timestamp", datetime.now().isoformat()),
            }
            
            success = FirebaseHelper.write("cricket_ground/weather", firebase_data)
            if success:
                logger.info("✓ Weather node updated")
            else:
                logger.warning("⚠ Failed to update weather node")
        except Exception as e:
            logger.error(f"⚠ Warning: Could not store weather to Firebase: {str(e)}")

    def extract_ml_features(self, weather_data: Dict) -> Dict:
        """
        Extract features for ML model from weather data
        Returns ML-ready features
        """
        if not weather_data:
            return {
                "wind_kph": 0,
                "cloud": 0,
                "precip_mm": 0,
                "pressure_mb": 1013,
                "dewpoint_c": 15,
                "uv": 5,
            }

        return {
            "wind_kph": weather_data.get("wind_kph", 0),
            "cloud": weather_data.get("cloud", 0),
            "precip_mm": weather_data.get("precip_mm", 0),
            "pressure_mb": weather_data.get("pressure_mb", 1013),
            "dewpoint_c": weather_data.get("dewpoint_c", 15),
            "uv": weather_data.get("uv", 5),
        }


# Create singleton instance
weather_service = WeatherService()
