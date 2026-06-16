"""
ML Model Prediction Service
Supports multi-output prediction for cricket pitch characteristics
Includes fallback rule-based engine when model is unavailable
"""

import pickle
import numpy as np
import os
from config import Config
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PitchPredictor:
    """Service for predicting cricket pitch characteristics"""

    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        self.features = None
        self.targets = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained models from pickle file"""
        try:
            if not os.path.exists(Config.MODEL_PATH):
                logger.warning(f"⚠ Model file not found at {Config.MODEL_PATH}")
                logger.info("   Please run: python ml_training.py")
                logger.info("   Using fallback rule-based engine")
                return False

            with open(Config.MODEL_PATH, "rb") as f:
                data = pickle.load(f)
                self.models = data.get("models", {})
                self.label_encoders = data.get("label_encoders", {})
                self.features = data.get("features", [])
                self.targets = data.get("targets", [])
                self.is_loaded = True

            logger.info(f"✓ Model loaded successfully from {Config.MODEL_PATH}")
            return True

        except Exception as e:
            logger.error(f"✗ Error loading model: {str(e)}")
            return False

    def predict(
        self,
        temperature: float,
        humidity: float,
        light: float,
        rain: int,
        soilMoisture: float,
        wind_kph: float,
        cloud: float,
        precip_mm: float,
        pressure_mb: float,
        dewpoint_c: float,
        uv: float,
    ) -> Optional[Dict]:
        """
        Predict cricket pitch characteristics
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity percentage (0-100)
            light: Light intensity in lumens (0-1000)
            rain: Rain (1=true, 0=false)
            soilMoisture: Soil moisture percentage (0-100)
            wind_kph: Wind speed in kph
            cloud: Cloud cover percentage (0-100)
            precip_mm: Precipitation in mm
            pressure_mb: Pressure in mb
            dewpoint_c: Dew point in Celsius
            uv: UV index (0-15)
            
        Returns:
            Dict with pitch_type, bounce, spin, seam_movement and confidence
        """
        try:
            # Prepare input features
            features_array = np.array(
                [
                    [
                        temperature,
                        humidity,
                        light,
                        rain,
                        soilMoisture,
                        wind_kph,
                        cloud,
                        precip_mm,
                        pressure_mb,
                        dewpoint_c,
                        uv,
                    ]
                ]
            )

            if self.is_loaded and self.models:
                # Use ML models
                return self._predict_with_models(features_array)
            else:
                # Use fallback rule-based engine
                logger.info("Using fallback rule-based prediction engine")
                return self._predict_with_fallback(
                    temperature,
                    humidity,
                    light,
                    rain,
                    soilMoisture,
                    wind_kph,
                    cloud,
                    precip_mm,
                    pressure_mb,
                    dewpoint_c,
                    uv,
                )

        except Exception as e:
            logger.error(f"✗ Error making prediction: {str(e)}")
            return {"success": False, "error": str(e)}

    def _predict_with_models(self, features_array: np.ndarray) -> Dict:
        """Make predictions using trained ML models"""
        predictions = {}
        confidences = []

        for target in self.targets:
            if target not in self.models:
                logger.warning(f"⚠ Model for {target} not found")
                continue

            model = self.models[target]
            le = self.label_encoders[target]

            # Get prediction
            pred_encoded = model.predict(features_array)[0]
            pred_label = le.inverse_transform([pred_encoded])[0]

            # Get confidence
            probabilities = model.predict_proba(features_array)[0]
            confidence = float(np.max(probabilities))

            predictions[target] = pred_label
            confidences.append(confidence)

        avg_confidence = np.mean(confidences) if confidences else 0

        return {
            "success": True,
            "pitch_type": predictions.get("pitch_type", "Balanced"),
            "bounce": predictions.get("bounce", "Medium"),
            "spin": predictions.get("spin", "Low"),
            "seam_movement": predictions.get("seam_movement", "Moderate"),
            "confidence": round(avg_confidence, 4),
            "timestamp": datetime.now().isoformat(),
        }

    def _predict_with_fallback(
        self,
        temperature: float,
        humidity: float,
        light: float,
        rain: int,
        soilMoisture: float,
        wind_kph: float,
        cloud: float,
        precip_mm: float,
        pressure_mb: float,
        dewpoint_c: float,
        uv: float,
    ) -> Dict:
        """
        Rule-based fallback prediction engine
        Uses domain knowledge to predict pitch characteristics
        """

        # Pitch Type Logic
        if humidity > 75 and precip_mm > 2:
            pitch_type = "Bowling Friendly"
        elif light > 800 and soilMoisture < 40 and humidity < 50:
            pitch_type = "Pace Friendly"
        elif temperature > 28 and soilMoisture < 30:
            pitch_type = "Pace Friendly"
        elif soilMoisture > 60 and cloud > 60 and humidity > 70:
            pitch_type = "Spin Friendly"
        elif cloud < 30 and light > 750 and soilMoisture < 45:
            pitch_type = "Batting Friendly"
        else:
            pitch_type = "Balanced"

        # Bounce Logic
        if soilMoisture < 30 and light > 800:
            bounce = "High & Consistent"
        elif soilMoisture > 65:
            bounce = "Low"
        elif 40 < soilMoisture < 60:
            bounce = "Medium"
        elif soilMoisture < 35 and temperature > 25:
            bounce = "High"
        else:
            bounce = "Variable"

        # Spin Logic
        if soilMoisture > 60 and temperature > 25:
            spin = "High"
        elif soilMoisture > 50 and temperature > 22:
            spin = "Moderate"
        elif soilMoisture < 40 or light > 850:
            spin = "Very Low"
        else:
            spin = "Low"

        # Seam Movement Logic
        if humidity > 75 and cloud > 70 and wind_kph > 12:
            seam_movement = "High"
        elif humidity > 65 and wind_kph > 10:
            seam_movement = "Moderate"
        else:
            seam_movement = "Low"

        # Calculate fallback confidence (0.5-0.8)
        confidence = 0.65

        return {
            "success": True,
            "pitch_type": pitch_type,
            "bounce": bounce,
            "spin": spin,
            "seam_movement": seam_movement,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "engine": "fallback_rule_based",
        }


# Create singleton instance
pitch_predictor = PitchPredictor()
            predictions.append(pred)

        return {"success": True, "total_predictions": len(predictions), "predictions": predictions}

    def get_model_info(self) -> Dict:
        """Get information about the trained model"""
        if not self.is_loaded:
            return {"loaded": False, "message": "Model not loaded"}

        return {
            "loaded": True,
            "model_type": type(self.model).__name__,
            "features": self.features,
            "classes": list(self.label_encoder.classes_),
            "model_path": Config.MODEL_PATH,
            "n_estimators": self.model.n_estimators if hasattr(self.model, "n_estimators") else None,
            "feature_importances": {
                feat: float(imp)
                for feat, imp in zip(self.features, self.model.feature_importances_)
            },
        }


# Create singleton instance
pitch_predictor = PitchPredictor()
