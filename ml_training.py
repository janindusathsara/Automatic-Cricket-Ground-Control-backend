"""
ML Model Training Script
Trains multi-output Random Forest classifiers for cricket pitch prediction
Predicts: pitch_type, bounce, spin, seam_movement
Run this script once to generate the model.pkl file
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """ML Model trainer for multi-output cricket pitch prediction"""

    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        self.feature_columns = [
            "temperature",
            "humidity",
            "light",
            "rain",
            "soilMoisture",
            "wind_kph",
            "cloud",
            "precip_mm",
            "pressure_mb",
            "dewpoint_c",
            "uv",
        ]
        self.target_columns = ["pitch_type", "bounce", "spin", "seam_movement"]

    def load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Load training dataset"""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")

        df = pd.read_csv(dataset_path)
        logger.info(f"✓ Dataset loaded: {len(df)} samples")
        logger.info(f"  Columns: {list(df.columns)}")
        return df

    def train(self, dataset_path: str = None) -> bool:
        """Train multi-output ML models"""
        try:
            if dataset_path is None:
                dataset_path = Config.DATASET_PATH

            # Load dataset
            df = self.load_dataset(dataset_path)

            # Validate required columns
            required_cols = self.feature_columns + self.target_columns
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing columns in dataset: {missing_cols}")

            # Extract features
            X = df[self.feature_columns].values

            logger.info(f"\n📊 Dataset Statistics:")
            logger.info(f"  Total samples: {len(df)}")
            logger.info(f"  Feature shape: {X.shape}")

            # Split data (once for all targets)
            X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

            logger.info(f"\n📋 Train-Test Split:")
            logger.info(f"  Training samples: {len(X_train)}")
            logger.info(f"  Testing samples: {len(X_test)}")

            # Train separate model for each target
            logger.info(f"\n🤖 Training Multi-Output Random Forest Models...")
            for target in self.target_columns:
                logger.info(f"\n  Training model for: {target}")
                
                # Create train/test split
                indices = np.arange(len(df))
                train_indices, test_indices = train_test_split(
                    indices, test_size=0.2, random_state=42
                )
                
                # Get target data
                y_train = df[target].iloc[train_indices].values
                y_test = df[target].iloc[test_indices].values
                X_train_split = df[self.feature_columns].iloc[train_indices].values
                X_test_split = df[self.feature_columns].iloc[test_indices].values

                # Encode target labels
                le = LabelEncoder()
                y_train_encoded = le.fit_transform(y_train)
                y_test_encoded = le.transform(y_test)

                # Train Random Forest model
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                )

                model.fit(X_train_split, y_train_encoded)

                # Evaluate model
                train_accuracy = model.score(X_train_split, y_train_encoded)
                test_accuracy = model.score(X_test_split, y_test_encoded)

                logger.info(f"    Train Accuracy: {train_accuracy:.4f}")
                logger.info(f"    Test Accuracy: {test_accuracy:.4f}")
                logger.info(f"    Classes: {le.classes_}")

                # Store model and encoder
                self.models[target] = model
                self.label_encoders[target] = le

            logger.info(f"\n✓ All models trained successfully!")

            # Feature importance (from first model)
            first_model = self.models[self.target_columns[0]]
            logger.info(f"\n📊 Feature Importance:")
            for feature, importance in zip(self.feature_columns, first_model.feature_importances_):
                logger.info(f"  {feature}: {importance:.4f}")

            # Save models
            self.save_model()
            return True

        except Exception as e:
            logger.error(f"✗ Error during training: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def save_model(self, model_path: str = None):
        """Save trained models and label encoders"""
        if model_path is None:
            model_path = Config.MODEL_PATH

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Save all models and encoders
        with open(model_path, "wb") as f:
            pickle.dump(
                {
                    "models": self.models,
                    "label_encoders": self.label_encoders,
                    "features": self.feature_columns,
                    "targets": self.target_columns,
                },
                f,
            )

        logger.info(f"✓ Model saved to {model_path}")

    @staticmethod
    def run():
        """Run the training pipeline"""
        trainer = ModelTrainer()
        success = trainer.train()
        if success:
            logger.info("\n✅ Training completed successfully!")
        else:
            logger.error("\n❌ Training failed!")
        return success


if __name__ == "__main__":
    ModelTrainer.run()
