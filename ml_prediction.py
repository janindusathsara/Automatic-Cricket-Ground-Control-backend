"""
ML Model Prediction Service
Uses the trained model to predict pitch conditions
"""

import pickle
import numpy as np
import os
from config import Config
from typing import Dict, Optional, Tuple
from datetime import datetime


class PitchPredictor:
    """Service for predicting pitch conditions"""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.features = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from pickle file"""
        try:
            if not os.path.exists(Config.MODEL_PATH):
                print(f"⚠ Model file not found at {Config.MODEL_PATH}")
                print("   Please run: python ml_training.py")
                return False

            with open(Config.MODEL_PATH, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.label_encoder = data["label_encoder"]
                self.features = data["features"]
                self.is_loaded = True

            print(f"✓ Model loaded successfully from {Config.MODEL_PATH}")
            return True

        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            return False

    def predict(
        self, humidity: float, temperature: float, soil_moisture: float, light_intensity: float
    ) -> Optional[Dict]:
        """
        Predict pitch condition
        
        Args:
            humidity: Humidity percentage (0-100)
            temperature: Temperature in Celsius
            soil_moisture: Soil moisture level (0-100)
            light_intensity: Light intensity in lumens
            
        Returns:
            Dict with prediction, confidence, and probabilities
        """
        if not self.is_loaded:
            return {
                "success": False,
                "error": "Model not loaded. Please train the model first.",
            }

        try:
            # Prepare input features
            features_array = np.array([[humidity, temperature, soil_moisture, light_intensity]])

            # Get prediction
            prediction_encoded = self.model.predict(features_array)[0]
            prediction_label = self.label_encoder.inverse_transform([prediction_encoded])[0]

            # Get prediction probabilities
            probabilities = self.model.predict_proba(features_array)[0]
            confidence = float(np.max(probabilities))

            # Get all class probabilities
            class_probabilities = {
                class_label: float(prob)
                for class_label, prob in zip(self.label_encoder.classes_, probabilities)
            }

            return {
                "success": True,
                "prediction": prediction_label,
                "confidence": round(confidence, 4),
                "all_predictions": class_probabilities,
                "input": {
                    "humidity": humidity,
                    "temperature": temperature,
                    "soil_moisture": soil_moisture,
                    "light_intensity": light_intensity,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"✗ Error making prediction: {str(e)}")
            return {"success": False, "error": str(e)}

    def batch_predict(self, data_list: list) -> Dict:
        """
        Make predictions on multiple samples
        
        Args:
            data_list: List of dicts with humidity, temperature, soil_moisture, light_intensity
            
        Returns:
            List of predictions
        """
        predictions = []
        for data in data_list:
            pred = self.predict(
                data.get("humidity", 0),
                data.get("temperature", 20),
                data.get("soil_moisture", 0),
                data.get("light_intensity", 0),
            )
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
