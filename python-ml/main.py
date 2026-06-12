from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="Pollution ML Service", version="1.0.0")

# Load semua model saat startup
aqi_regressor = joblib.load("models/aqi_regressor.pkl")
aqi_classifier = joblib.load("models/aqi_classifier.pkl")
anomaly_detector = joblib.load("models/anomaly_detector.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

# Schema input


class PollutionInput(BaseModel):
    pm25: float
    pm10: float
    co: float
    no2: float
    temperature: float
    humidity: float
    wind_speed: float
    temperature_inversion: int


def to_features(data: PollutionInput):
    return np.array([[
        data.pm25, data.pm10, data.co, data.no2,
        data.temperature, data.humidity,
        data.wind_speed, data.temperature_inversion
    ]])

# Endpoint 1: Prediksi AQI (angka)


@app.post("/predict/aqi")
def predict_aqi(data: PollutionInput):
    features = to_features(data)
    aqi_value = round(float(aqi_regressor.predict(features)[0]))
    return {"aqi": aqi_value}

# Endpoint 2: Klasifikasi Kategori AQI


@app.post("/predict/category")
def predict_category(data: PollutionInput):
    features = to_features(data)
    encoded = aqi_classifier.predict(features)[0]
    category = label_encoder.inverse_transform([encoded])[0]
    return {"aqi_category": category}

# Endpoint 3: Deteksi Anomali


@app.post("/predict/anomaly")
def predict_anomaly(data: PollutionInput):
    features = to_features(data)
    raw = anomaly_detector.predict(features)[0]
    is_anomaly = int(raw == -1)
    return {"is_anomaly": is_anomaly}

# Endpoint 4: Prediksi Lengkap (semua sekaligus)


@app.post("/predict/full")
def predict_full(data: PollutionInput):
    features = to_features(data)

    aqi_value = round(float(aqi_regressor.predict(features)[0]))
    encoded = aqi_classifier.predict(features)[0]
    category = label_encoder.inverse_transform([encoded])[0]
    raw = anomaly_detector.predict(features)[0]
    is_anomaly = int(raw == -1)

    return {
        "aqi": aqi_value,
        "aqi_category": category,
        "is_anomaly": is_anomaly
    }

# Health Check


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": 3}
