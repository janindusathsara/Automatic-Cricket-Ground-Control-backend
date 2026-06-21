# Cricket Ground Automation System - Backend

A production-ready FastAPI backend for automated cricket ground management using multi-output ML-powered pitch condition prediction.

**Technology Stack:**
- FastAPI (Web Framework)
- Firebase Realtime Database (Data Storage)
- scikit-learn (ML Model)
- WeatherAPI / OpenWeatherMap (Weather Data)
- Python 3.8+

---

## + Features

+ **Live Weather Integration** - Real-time weather data from external APIs
+ **Firebase RTDB Integration** - Read/write sensor and prediction data
+ **Multi-Output ML Pitch Prediction** - Predicts pitch type, bounce, spin, and seam movement
+ **Full Pipeline** - Automated weather + sensor + prediction workflow
+ **RESTful API** - Clean, documented endpoints
+ **Modular Architecture** - Easy to extend and maintain
+ **Error Handling** - Comprehensive exception handling with fallback rules
+ **Production-Ready** - Environment-based configuration

---

## Folder Structure

```
Automatic-Cricket-Ground-Control-backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration management
├── firebase_config.py         # Firebase initialization wrapper
├── weather_service.py         # Backward compatibility wrapper
├── sensor_service.py          # Firebase sensor reading
├── ml_training.py             # ML model training script
├── ml_prediction.py           # Backward compatibility wrapper
├── send_prediction_to_firebase.py # Script for testing predictions
│
├── services/
│   ├── __init__.py
│   ├── prediction_service.py  # Core ML prediction logic
│   └── weather_service.py     # Weather fetching logic
│
├── routes/
│   ├── __init__.py
│   ├── weather.py             # Weather endpoints
│   ├── sensors.py             # Sensor endpoints
│   └── ml.py                  # ML prediction endpoints
│
├── utils/
│   ├── __init__.py
│   └── firebase_helper.py     # Core Firebase operations
│
├── data/
│   ├── sample_dataset.csv     # Training dataset (11 features, 4 targets)
│   └── model.pkl              # Trained model (auto-generated)
│
├── .env.example               # Environment template
├── .env                       # Local environment (git-ignored)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Quick Start

### 1. Install Dependencies

```bash
# Activate your Python virtual environment
.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Copy `.env.example` to `.env` and fill in your credentials.

### 3. Train the ML Model

```bash
python ml_training.py
```

This will load the 11-feature dataset, train multi-output Random Forest classifiers, and save the model to `data/model.pkl`.

### 4. Run the Backend Server

```bash
python main.py
```

Server runs at: **http://localhost:8000**

---

## Firebase Database Structure

```
cricket_ground/
├── data/                    # Written by Labview/Arduino sensors
│   ├── temperature          # float (°C)
│   ├── humidity             # float (%)
│   ├── light                # float (lumens)
│   ├── rain                 # boolean (true/false)
│   └── soilMoisture         # float (%)
│
├── weather/                 # Written by backend (WeatherAPI)
│   ├── wind_kph             # float
│   ├── cloud                # float (%)
│   ├── precip_mm            # float
│   ├── pressure_mb          # float
│   ├── dewpoint_c           # float
│   ├── uv                   # float
│   ├── last_updated         # string
│   └── timestamp            # string (ISO 8601)
│
└── prediction/              # Written by backend (ML pipeline)
    ├── pitch_type            # string
    ├── bounce                # string
    ├── spin                  # string
    ├── seam_movement         # string
    ├── confidence            # float (0-1)
    └── generated_at          # string (ISO 8601 UTC)
```

---

## API Endpoints

### Run Full Pipeline

```bash
POST /ml/run-full-pipeline
```

This endpoint:
1. Fetches current weather from Weather API
2. Reads sensor data from Firebase
3. Combines 11 features and runs ML prediction
4. Writes results to Firebase under `cricket_ground/prediction`
5. Stores weather to `cricket_ground/weather`

**Example Response:**
```json
{
  "success": true,
  "prediction": {
    "pitch_type": "Balanced",
    "bounce": "Medium",
    "spin": "Moderate",
    "seam_movement": "Moderate",
    "confidence": 0.95
  },
  "sensor_data": {
    "temperature": 25.0,
    "humidity": 65.0,
    "light": 700.0,
    "rain": false,
    "soilMoisture": 45.0,
    "timestamp": "2024-01-01T12:00:00"
  },
  "weather_data": {
    "wind_kph": 10.5,
    "cloud": 20.0,
    "precip_mm": 0.0,
    "pressure_mb": 1013.0,
    "dewpoint_c": 15.0,
    "uv": 5.0
  },
  "firebase_written": true,
  "timestamp": "2024-01-01T12:00:05"
}
```

---

## ML Model Details

The system uses a Multi-Output Random Forest Classifier predicting 4 targets simultaneously based on 11 input features.

**Features (Inputs):**
`temperature`, `humidity`, `light`, `rain`, `soilMoisture`, `wind_kph`, `cloud`, `precip_mm`, `pressure_mb`, `dewpoint_c`, `uv`

**Targets (Outputs):**
1. **Pitch Type**: Batting Friendly, Bowling Friendly, Balanced, Spin Friendly, Pace Friendly
2. **Bounce**: Low, Medium, High, High & Consistent, Variable
3. **Spin**: Very Low, Low, Moderate, High
4. **Seam Movement**: Low, Moderate, High

If the model is unavailable, the backend automatically uses a **Rule-Based Fallback Engine** built on cricketing domain knowledge.

### Step 5: Test the Full Automation Pipeline

Now that your server is running, you can test the entire pipeline (which grabs the weather, reads sensors from Firebase, runs the ML model, and pushes the result back to Firebase).

Open a new, separate terminal window in your project folder and run your test script:

```bash
python test_full_pipeline.py
```

This script will test all edge cases (dry weather, extreme rain) and ensure your multi-output model is predicting the pitch condition correctly.

If you just want to run a quick test that pushes a single prediction to your Firebase database, you can run:

```bash
python send_prediction_to_firebase.py
```