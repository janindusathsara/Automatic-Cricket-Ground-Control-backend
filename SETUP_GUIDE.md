# 🚀 Quick Setup Guide

Follow these steps to get your Cricket Ground Automation Backend running.

---

## Step 1: Install Dependencies

```bash
cd "c:\Users\User\Desktop\Cricket Ground\Automatic-Cricket-Ground-Control-backend"

# Activate virtual environment
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 firebase-admin-6.2.0 ...
```

---

## Step 2: Configure Environment Variables

### Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project → **Project Settings** → **Service Accounts**
3. Click "Generate New Private Key"
4. Save the JSON file
5. Copy values from JSON to `.env` file:

```
FIREBASE_PROJECT_ID=xxx
FIREBASE_PRIVATE_KEY_ID=xxx
FIREBASE_PRIVATE_KEY=xxx
FIREBASE_CLIENT_EMAIL=xxx
FIREBASE_CLIENT_ID=xxx
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

### Get Weather API Key

1. Go to [WeatherAPI.com](https://www.weatherapi.com/) (free tier available)
2. Create account and get API key
3. Add to `.env`:

```
WEATHER_API_KEY=your_api_key_here
WEATHER_API_PROVIDER=weatherapi
WEATHER_API_CITY=London
```

### Create .env File

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
# Use VS Code: Ctrl+O and open .env
```

**Your .env should look like:**
```env
FIREBASE_PROJECT_ID=my-cricket-ground
FIREBASE_PRIVATE_KEY_ID=abcd1234
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvg...=\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@my-cricket-ground.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_DATABASE_URL=https://my-cricket-ground.firebaseio.com

WEATHER_API_KEY=abc123xyz789
WEATHER_API_PROVIDER=weatherapi
WEATHER_API_CITY=London

APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

MODEL_PATH=data/model.pkl
DATASET_PATH=data/sample_dataset.csv
```

---

## Step 3: Train the ML Model

```bash
python ml_training.py
```

**What happens:**
- Loads sample dataset (51 samples)
- Trains Random Forest classifier
- Shows accuracy metrics (~95%)
- Saves model to `data/model.pkl`

**Output:**
```
============================================================
🏏 Cricket Ground ML Model Training
============================================================
✓ Dataset loaded: 51 samples
  Features: ['humidity', 'temperature', 'soil_moisture', 'light_intensity', 'pitch_condition']

📊 Dataset Statistics:
  Total samples: 51
  Feature shape: (51, 4)
  Classes: ['Balanced Pitch' 'Dry Pitch' 'Wet Pitch']
  
✓ Model trained successfully!
  Training Accuracy: 0.9800
  Testing Accuracy: 0.9500
  
✓ Model saved to data/model.pkl
```

---

## Step 4: Run the Backend Server

```bash
python main.py
```

**Output:**
```
============================================================
🏏 Cricket Ground Automation Backend
============================================================
Environment: development
Host: 0.0.0.0:8000
Debug: True
============================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
```

---

## Step 5: Test the API

### Option A: Using Browser

1. Open http://localhost:8000/docs
2. Try endpoints in Swagger UI

### Option B: Using cURL

```bash
# Test health
curl http://localhost:8000/health

# Get weather
curl http://localhost:8000/weather/current

# Get sensors
curl http://localhost:8000/sensors/latest

# Make prediction (paste as one line)
curl -X POST http://localhost:8000/ml/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"humidity\": 60, \"temperature\": 22, \"soil_moisture\": 65, \"light_intensity\": 450}"

# Run full pipeline
curl -X POST http://localhost:8000/ml/run-full-pipeline
```

### Option C: Using Python

```python
import requests
import json

# Test full pipeline
response = requests.post('http://localhost:8000/ml/run-full-pipeline')
print(json.dumps(response.json(), indent=2))
```

---

## 🎯 Next: Setup Firebase Database

### Create Database Structure

In Firebase Console → Realtime Database → Create structure:

```json
{
  "cricket_ground": {
    "sensors": {
      "humidity": 60,
      "temperature": 22,
      "soil_moisture": 65,
      "light_intensity": 450,
      "timestamp": "2024-01-01T12:00:00"
    },
    "weather": {
      "current": {
        "temperature": 22.5,
        "humidity": 65,
        "condition": "Partly Cloudy"
      }
    },
    "ml": {
      "pitch_report": {
        "prediction": "Balanced Pitch",
        "confidence": 0.87
      }
    }
  }
}
```

### Set Security Rules

In Firebase Console → Realtime Database → Rules:

```json
{
  "rules": {
    "cricket_ground": {
      ".read": true,
      ".write": true
    }
  }
}
```

⚠️ **For Production**: Use authentication and proper permissions

---

## ✅ Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` shows fastapi, firebase-admin, etc.)
- [ ] `.env` file created and filled with credentials
- [ ] Firebase connection working
- [ ] Weather API key valid
- [ ] ML model trained (`data/model.pkl` exists)
- [ ] Backend server running on http://localhost:8000
- [ ] Can access http://localhost:8000/docs
- [ ] Can call `/health` endpoint
- [ ] Can call `/ml/model-info` endpoint

---

## 🆘 Common Issues & Fixes

### Issue: "Module not found: firebase_admin"
```bash
pip install firebase-admin
```

### Issue: "Model file not found"
```bash
python ml_training.py
```

### Issue: "Firebase initialization failed"
- Check `.env` file exists
- Verify Firebase credentials are correct
- Test network connection to Firebase

### Issue: "Weather API Error"
- Verify `WEATHER_API_KEY` is correct
- Check `WEATHER_API_CITY` spelling
- Ensure API key is active (check WeatherAPI.com dashboard)

### Issue: Port 8000 already in use
```bash
# Change PORT in .env
PORT=8001

# Or kill the process using port 8000
# (on PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

## 📚 Project Structure After Setup

```
backend/
├── main.py                    ✓ FastAPI app
├── config.py                  ✓ Configuration
├── firebase_config.py         ✓ Firebase init
├── weather_service.py         ✓ Weather API
├── sensor_service.py          ✓ Sensors
├── ml_training.py             ✓ Training script
├── ml_prediction.py           ✓ Predictions
├── routes/                    ✓ API endpoints
│   ├── weather.py
│   ├── sensors.py
│   └── ml.py
├── data/                      ✓ Data directory
│   ├── sample_dataset.csv     ✓ Training data
│   └── model.pkl              ✓ Trained model
├── .env                       ✓ Your secrets (DON'T COMMIT)
├── .env.example               ✓ Template
├── requirements.txt           ✓ Dependencies
├── README.md                  ✓ Full docs
└── SETUP_GUIDE.md             ✓ This file
```

---

## 🎓 Understanding the Data Flow

```
┌─────────────────┐
│  Weather API    │  ← Real-time weather data
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   FastAPI App   │◄─────┤  Firebase RTDB   │
└────────┬────────┘      │  (Sensors)       │
         │               └──────────────────┘
         │
         ▼
┌─────────────────┐
│  ML Model       │      Random Forest Classifier
│  (sklearn)      │      Input: humidity, temp, moisture, light
└────────┬────────┘      Output: Pitch Condition + Confidence
         │
         ▼
┌─────────────────┐
│  Prediction     │      Example: "Balanced Pitch" (0.87)
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  Firebase RTDB   │
│  /ml/pitch_report│
└──────────────────┘
```

---

## 🚀 You're All Set!

Your backend is ready to:
- ✅ Fetch live weather data
- ✅ Read sensor data from Firebase
- ✅ Predict pitch conditions using ML
- ✅ Store predictions in Firebase

**Next Steps:**
1. Build a frontend to display predictions
2. Setup automated sensor data collection
3. Create a mobile app to monitor conditions
4. Deploy to cloud (AWS/GCP/Azure)

---

**Happy Coding! 🏏**
