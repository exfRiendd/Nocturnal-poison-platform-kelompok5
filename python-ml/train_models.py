from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
    IsolationForest,
)
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42


# ---------------------------------------------------------------------------
# 1. TOXIC DOSE ESTIMATOR
# ---------------------------------------------------------------------------
def train_toxic_dose_model():
    print("=" * 60)
    print("1. TOXIC DOSE ESTIMATOR (Random Forest Regressor)")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "toxic_dose_dataset.csv")

    feature_cols = ["pm25", "pm10", "co", "no2",
                    "rmv_liters_per_min", "duration_minutes", "mask_efficiency"]
    target_cols = ["cumulative_toxic_load_score",
                   "pm25_retained_micrograms", "co_blood_saturation_estimate"]

    X = df[feature_cols]
    y = df[target_cols]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED)

    model = RandomForestRegressor(
        n_estimators=100, max_depth=8, random_state=SEED, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    for i, col in enumerate(target_cols):
        mae = mean_absolute_error(y_test[col], y_pred[:, i])
        r2 = r2_score(y_test[col], y_pred[:, i])
        print(f"  {col:<35} MAE={mae:6.2f}  R2={r2:.3f}")

    joblib.dump(
        {"model": model, "feature_cols": feature_cols, "target_cols": target_cols},
        MODELS_DIR / "toxic_dose_model.joblib",
    )
    print("  Tersimpan -> models/toxic_dose_model.joblib\n")


# ---------------------------------------------------------------------------
# 2. LUNG FUNCTION IMPACT MODEL
# ---------------------------------------------------------------------------
def train_lung_impact_model():
    print("=" * 60)
    print("2. LUNG FUNCTION IMPACT MODEL (Gradient Boosting)")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "lung_impact_dataset.csv")

    feature_cols = ["cumulative_toxic_load_score", "age",
                    "asthma_history", "weight_kg", "baseline_lung_capacity_pct"]
    reg_target_cols = ["lung_function_temporary_drop_pct",
                       "alveoli_recovery_time_hours"]
    clf_target_col = "health_risk_category"

    X = df[feature_cols]
    y_reg = df[reg_target_cols]
    y_clf = df[clf_target_col]

    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=SEED, stratify=y_clf
    )

    reg_model = MultiOutputRegressor(
        GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05, random_state=SEED)
    )
    reg_model.fit(X_train, y_reg_train)
    y_reg_pred = reg_model.predict(X_test)
    for i, col in enumerate(reg_target_cols):
        mae = mean_absolute_error(y_reg_test[col], y_reg_pred[:, i])
        r2 = r2_score(y_reg_test[col], y_reg_pred[:, i])
        print(f"  {col:<35} MAE={mae:6.2f}  R2={r2:.3f}")

    clf_model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05, random_state=SEED)
    clf_model.fit(X_train, y_clf_train)
    y_clf_pred = clf_model.predict(X_test)
    acc = accuracy_score(y_clf_test, y_clf_pred)
    print(f"\n  health_risk_category accuracy = {acc:.3f}")
    print(classification_report(y_clf_test, y_clf_pred, zero_division=0))

    joblib.dump(
        {
            "regressor": reg_model,
            "classifier": clf_model,
            "feature_cols": feature_cols,
            "reg_target_cols": reg_target_cols,
            "clf_target_col": clf_target_col,
            "clf_classes": sorted(y_clf.unique().tolist()),
        },
        MODELS_DIR / "lung_impact_model.joblib",
    )
    print("  Tersimpan -> models/lung_impact_model.joblib\n")


# ---------------------------------------------------------------------------
# 3. SENSOR ANOMALY DETECTOR
# ---------------------------------------------------------------------------
def train_anomaly_model():
    print("=" * 60)
    print("3. SENSOR ANOMALY DETECTOR (Isolation Forest)")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "anomaly_dataset.csv")

    feature_cols = ["sensor_value", "timestamp_hour",
                    "rolling_mean_1h", "z_score"]
    X = df[feature_cols]

    model = IsolationForest(
        n_estimators=200, contamination=0.045, random_state=SEED, n_jobs=-1)
    model.fit(X)

    pred = model.predict(X)
    predicted_anomaly = pred == -1
    actual_anomaly = df["is_anomaly"].astype(bool)
    overlap = (predicted_anomaly & actual_anomaly).sum()

    print(f"  Total anomali asli (label)   : {actual_anomaly.sum()}")
    print(f"  Total anomali terdeteksi     : {predicted_anomaly.sum()}")
    print(f"  Overlap (terdeteksi & benar) : {overlap}")
    print(
        f"  Recall thd anomali asli      : {overlap / actual_anomaly.sum():.3f}")

    joblib.dump({"model": model, "feature_cols": feature_cols},
                MODELS_DIR / "anomaly_model.joblib")
    print("  Tersimpan -> models/anomaly_model.joblib\n")


def main():
    train_toxic_dose_model()
    train_lung_impact_model()
    train_anomaly_model()
    print("=" * 60)
    print("Semua model selesai dilatih & tersimpan di models/")
    print("=" * 60)


if __name__ == "__main__":
    main()
