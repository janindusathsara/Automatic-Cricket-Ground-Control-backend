"""
Script to send prediction data to Firebase Realtime Database
"""

import sys
from datetime import datetime
from services.prediction_service import pitch_predictor
from services.weather_service import weather_service
from sensor_service import sensor_service
from utils.firebase_helper import FirebaseHelper

def send_prediction_to_firebase():
    """Generate prediction and send to Firebase"""
    
    # Initialize Firebase
    try:
        FirebaseHelper.initialize()
        print("+ Firebase connection established")
    except Exception as e:
        print(f"- Firebase connection failed: {str(e)}")
        return False
    
    # Read data
    sensor_data = sensor_service.get_latest_sensor_data()
    weather_data = weather_service.get_current_weather()
    
    sensor_features = sensor_service.extract_ml_features(sensor_data)
    weather_features = weather_service.extract_ml_features(weather_data)

    print(f"\n[DATA] Input Sensor Data:")
    print(f"  Temperature: {sensor_features.get('temperature')}°C")
    print(f"  Humidity: {sensor_features.get('humidity')}%")
    print(f"  Light: {sensor_features.get('light')} lux")
    print(f"  Rain: {sensor_features.get('rain')}")
    print(f"  Soil Moisture: {sensor_features.get('soilMoisture')}%")
    
    print(f"\n[WEATHER] Input Weather Data:")
    print(f"  Wind: {weather_features.get('wind_kph')} km/h")
    print(f"  Cloud: {weather_features.get('cloud')}%")
    print(f"  Precipitation: {weather_features.get('precip_mm')} mm")
    print(f"  Pressure: {weather_features.get('pressure_mb')} mb")
    print(f"  Dewpoint: {weather_features.get('dewpoint_c')}°C")
    print(f"  UV: {weather_features.get('uv')}")

    # Make prediction
    print(f"\n[ML] Generating prediction...")
    prediction_result = pitch_predictor.predict(
        temperature=sensor_features.get('temperature', 25.0),
        humidity=sensor_features.get('humidity', 65.0),
        light=sensor_features.get('light', 700.0),
        rain=sensor_features.get('rain', 0),
        soilMoisture=sensor_features.get('soilMoisture', 45.0),
        wind_kph=weather_features.get('wind_kph', 0.0),
        cloud=weather_features.get('cloud', 0.0),
        precip_mm=weather_features.get('precip_mm', 0.0),
        pressure_mb=weather_features.get('pressure_mb', 1013.0),
        dewpoint_c=weather_features.get('dewpoint_c', 15.0),
        uv=weather_features.get('uv', 5.0)
    )
    
    if not prediction_result.get("success"):
        print(f"- Prediction failed: {prediction_result.get('error')}")
        return False
    
    # Prepare Firebase payload
    firebase_payload = {
        "pitch_type": prediction_result.get("pitch_type"),
        "bounce": prediction_result.get("bounce"),
        "spin": prediction_result.get("spin"),
        "seam_movement": prediction_result.get("seam_movement"),
        "confidence": prediction_result.get("confidence"),
        "generated_at": FirebaseHelper.get_server_timestamp()
    }
    
    print(f"\n[RESULT] Prediction Result:")
    print(f"  Pitch Type: {firebase_payload['pitch_type']}")
    print(f"  Bounce: {firebase_payload['bounce']}")
    print(f"  Spin: {firebase_payload['spin']}")
    print(f"  Seam Movement: {firebase_payload['seam_movement']}")
    print(f"  Confidence: {firebase_payload['confidence']:.2%}")
    
    # Send to Firebase
    print(f"\n[UPLOAD] Sending to Firebase...")
    success = FirebaseHelper.write("cricket_ground/prediction", firebase_payload)
    
    if success:
        print(f"+ Successfully sent prediction to Firebase!")
        print(f"  Path: cricket_ground/prediction")
        return True
    else:
        print(f"- Failed to send prediction to Firebase")
        return False

if __name__ == "__main__":
    success = send_prediction_to_firebase()
    sys.exit(0 if success else 1)
