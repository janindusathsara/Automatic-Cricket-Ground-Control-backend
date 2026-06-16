"""
Weather API integration service
Supports WeatherAPI and OpenWeatherMap
"""

import requests
from datetime import datetime
from config import Config
from typing import Optional, Dict


class WeatherService:
    """Weather data retrieval service"""

    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.provider = Config.WEATHER_API_PROVIDER
        self.city = Config.WEATHER_API_CITY

    def get_current_weather(self) -> Optional[Dict]:
        """
        Get current weather data
        Returns temperature, humidity, conditions
        """
        try:
            if self.provider == "weatherapi":
                return self._get_weatherapi_data()
            elif self.provider == "openweather":
                return self._get_openweather_data()
            else:
                print(f"✗ Unknown weather provider: {self.provider}")
                return None
        except Exception as e:
            print(f"✗ Error fetching weather: {str(e)}")
            return None

    def _get_weatherapi_data(self) -> Optional[Dict]:
        """Fetch from WeatherAPI.com"""
        url = "https://api.weatherapi.com/v1/current.json"
        params = {"key": self.api_key, "q": self.city, "aqi": "no"}

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
            "wind_speed": data["current"]["wind_kph"],
            "pressure": data["current"]["pressure_mb"],
            "precipitation": data["current"]["precip_mm"],
            "cloud_coverage": data["current"]["cloud"],
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
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "precipitation": data.get("rain", {}).get("1h", 0),
            "cloud_coverage": data["clouds"]["all"],
            "timestamp": datetime.now().isoformat(),
        }

    def extract_ml_features(self, weather_data: Dict) -> Dict:
        """
        Extract features for ML model from weather data
        Returns normalized features
        """
        if not weather_data:
            return None

        return {
            "temperature": weather_data.get("temperature", 20),
            "humidity": weather_data.get("humidity", 50),
            "wind_speed": weather_data.get("wind_speed", 0),
            "precipitation": weather_data.get("precipitation", 0),
            "cloud_coverage": weather_data.get("cloud_coverage", 0),
            "pressure": weather_data.get("pressure", 1013),
        }


# Create singleton instance
weather_service = WeatherService()
