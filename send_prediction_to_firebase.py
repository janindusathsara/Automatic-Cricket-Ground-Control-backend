"""
Script to send prediction data to Firebase Realtime Database
"""

import sys
from datetime import datetime
from ml_prediction import pitch_predictor
from firebase_config import FirebaseDB

def send_prediction_to_firebase():
    """Generate prediction and send to Firebase"""
    
    # Initialize Firebase
    try:
        db = FirebaseDB.get_db()
        print("✓ Firebase connection established")
    except Exception as e:
        print(f"✗ Firebase connection failed: {str(e)}")
        return False
    
    # Create sample prediction data (you can modify these values)
    sample_data = {
        "humidity": 65.5,
        "temperature": 28.3,
        "soil_moisture": 45.2,
        "light_intensity": 850.0
    }
    
    print(f"\n📊 Input Sensor Data:")
    print(f"  Humidity: {sample_data['humidity']}%")
    print(f"  Temperature: {sample_data['temperature']}°C")
    print(f"  Soil Moisture: {sample_data['soil_moisture']}%")
    print(f"  Light Intensity: {sample_data['light_intensity']} lux")
    
    # Make prediction
    print(f"\n🤖 Generating prediction...")
    prediction_result = pitch_predictor.predict(
        humidity=sample_data['humidity'],
        temperature=sample_data['temperature'],
        soil_moisture=sample_data['soil_moisture'],
        light_intensity=sample_data['light_intensity']
    )
    
    if not prediction_result.get("success"):
        print(f"✗ Prediction failed: {prediction_result.get('error')}")
        return False
    
    # Prepare Firebase payload
    firebase_payload = {
        "prediction": prediction_result.get("prediction"),
        "confidence": prediction_result.get("confidence"),
        "all_predictions": prediction_result.get("all_predictions"),
        "sensor_data": sample_data,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n🎯 Prediction Result:")
    print(f"  Pitch Condition: {firebase_payload['prediction']}")
    print(f"  Confidence: {firebase_payload['confidence']:.2%}")
    print(f"  All Predictions: {firebase_payload['all_predictions']}")
    
    # Send to Firebase
    print(f"\n📤 Sending to Firebase...")
    success = FirebaseDB.write("cricket_ground/ml/latest_prediction", firebase_payload)
    
    if success:
        print(f"✓ Successfully sent prediction to Firebase!")
        print(f"  Path: cricket_ground/ml/latest_prediction")
        return True
    else:
        print(f"✗ Failed to send prediction to Firebase")
        return False

if __name__ == "__main__":
    success = send_prediction_to_firebase()
    sys.exit(0 if success else 1)
