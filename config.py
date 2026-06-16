"""
Configuration management for Cricket Ground Automation System
Loads and validates environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # FastAPI Configuration
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
    FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

    # Weather API Configuration
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    WEATHER_API_PROVIDER = os.getenv("WEATHER_API_PROVIDER", "weatherapi")
    WEATHER_API_CITY = os.getenv("WEATHER_API_CITY", "London")

    # ML Model Configuration
    MODEL_PATH = os.getenv("MODEL_PATH", "data/model.pkl")
    DATASET_PATH = os.getenv("DATASET_PATH", "data/sample_dataset.csv")

    @staticmethod
    def validate_firebase_config():
        """Validate Firebase configuration"""
        required_fields = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_DATABASE_URL",
        ]
        missing = [
            field for field in required_fields if not getattr(Config, field)
        ]
        if missing:
            raise ValueError(f"Missing Firebase configuration: {', '.join(missing)}")

    @staticmethod
    def validate_weather_config():
        """Validate Weather API configuration"""
        if not Config.WEATHER_API_KEY:
            raise ValueError("Missing WEATHER_API_KEY in environment variables")


# Create default config instance
config = Config()
