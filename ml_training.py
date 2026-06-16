"""
ML Model Training Script
Trains a Random Forest classifier on pitch condition data
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


class ModelTrainer:
    """ML Model trainer for pitch condition prediction"""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_columns = ["humidity", "temperature", "soil_moisture", "light_intensity"]
        self.target_column = "pitch_condition"

    def load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Load training dataset"""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")

        df = pd.read_csv(dataset_path)
        print(f"✓ Dataset loaded: {len(df)} samples")
        print(f"  Features: {list(df.columns)}")
        return df

    def train(self, dataset_path: str = None) -> bool:
        """Train the ML model"""
        try:
            if dataset_path is None:
                dataset_path = Config.DATASET_PATH

            # Load dataset
            df = self.load_dataset(dataset_path)

            # Extract features and target
            X = df[self.feature_columns].values
            y = df[self.target_column].values

            print(f"\n📊 Dataset Statistics:")
            print(f"  Total samples: {len(df)}")
            print(f"  Feature shape: {X.shape}")
            print(f"  Classes: {np.unique(y)}")
            print(f"  Class distribution:\n{df[self.target_column].value_counts()}")

            # Encode target labels
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )

            print(f"\n📋 Train-Test Split:")
            print(f"  Training samples: {len(X_train)}")
            print(f"  Testing samples: {len(X_test)}")

            # Train Random Forest model
            print(f"\n🤖 Training Random Forest Model...")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )

            self.model.fit(X_train, y_train)

            # Evaluate model
            train_accuracy = self.model.score(X_train, y_train)
            test_accuracy = self.model.score(X_test, y_test)

            print(f"\n✓ Model trained successfully!")
            print(f"  Training Accuracy: {train_accuracy:.4f}")
            print(f"  Testing Accuracy: {test_accuracy:.4f}")

            # Feature importance
            print(f"\n📊 Feature Importance:")
            for feature, importance in zip(self.feature_columns, self.model.feature_importances_):
                print(f"  {feature}: {importance:.4f}")

            # Save model
            self.save_model()
            return True

        except Exception as e:
            print(f"✗ Error during training: {str(e)}")
            return False

    def save_model(self, model_path: str = None):
        """Save trained model and label encoder"""
        if model_path is None:
            model_path = Config.MODEL_PATH

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Save model and encoder
        with open(model_path, "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "label_encoder": self.label_encoder,
                    "features": self.feature_columns,
                },
                f,
            )

        print(f"✓ Model saved to {model_path}")


def main():
    """Main training function"""
    print("=" * 60)
    print("🏏 Cricket Ground ML Model Training")
    print("=" * 60)

    trainer = ModelTrainer()
    success = trainer.train()

    if success:
        print("\n" + "=" * 60)
        print("✓ Training complete! Model ready for predictions.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ Training failed. Please check the errors above.")
        print("=" * 60)


if __name__ == "__main__":
    main()
