import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_absolute_error, r2_score,
    classification_report,
    confusion_matrix
)

# Setup
os.makedirs("models", exist_ok=True)
df = pd.read_csv("data/pollution_data.csv")

FEATURES = ["pm25", "pm10", "co", "no2", "temperature",
            "humidity", "wind_speed", "temperature_inversion"]
X = df[FEATURES]

# MODEL 1 — Prediksi AQI (Regresi)
print("=" * 50)
print(" Training Model 1: AQI Regressor...")

y1 = df["aqi"]
X1_train, X1_test, y1_train, y1_test = train_test_split(
    X, y1, test_size=0.2, random_state=42)

model1 = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model1.fit(X1_train, y1_train)

y1_pred = model1.predict(X1_test)
print(f"  MAE  : {mean_absolute_error(y1_test, y1_pred):.2f}")
print(f"  R²   : {r2_score(y1_test, y1_pred):.4f}")

joblib.dump(model1, "models/aqi_regressor.pkl")
print("   Saved: models/aqi_regressor.pkl")

# MODEL 2 — Klasifikasi Kategori AQI
print("\n" + "=" * 50)
print(" Training Model 2: AQI Category Classifier...")

y2_raw = df["aqi_category"]
le = LabelEncoder()
y2 = le.fit_transform(y2_raw)

# simpan encoder untuk decode nanti
joblib.dump(le, "models/label_encoder.pkl")

X2_train, X2_test, y2_train, y2_test = train_test_split(
    X, y2, test_size=0.2, random_state=42)

model2 = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model2.fit(X2_train, y2_train)

y2_pred = model2.predict(X2_test)
print(f"\n  Classification Report:")
print(classification_report(y2_test, y2_pred, target_names=le.classes_))

joblib.dump(model2, "models/aqi_classifier.pkl")
print("   Saved: models/aqi_classifier.pkl")

# MODEL 3 — Deteksi Anomali (Isolation Forest)
print("\n" + "=" * 50)
print(" Training Model 3: Anomaly Detector...")

# Isolation Forest: -1 = anomali, 1 = normal → konversi ke 0/1
model3 = IsolationForest(contamination=0.15, random_state=42, n_jobs=-1)
model3.fit(X)

preds_raw = model3.predict(X)
preds = (preds_raw == -1).astype(int)  # 1 = anomali

actual = df["is_anomaly"].values
correct = (preds == actual).sum()
print(f"  Akurasi deteksi : {correct/len(actual)*100:.2f}%")
print(f"  Anomali terdeteksi: {preds.sum()} dari {actual.sum()} aktual")

joblib.dump(model3, "models/anomaly_detector.pkl")
print("   Saved: models/anomaly_detector.pkl")

# SUMMARY
print("\n" + "=" * 50)
print("  Semua model berhasil ditraining dan disimpan!")
print("  models/aqi_regressor.pkl")
print("  models/aqi_classifier.pkl")
print("  models/anomaly_detector.pkl")
print("  models/label_encoder.pkl")
