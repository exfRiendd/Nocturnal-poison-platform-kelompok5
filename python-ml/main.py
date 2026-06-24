from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

ACTIVITY_RMV_BASE = {
    "resting": 7,
    "light_jog": 25,
    "moderate_run": 40,
    "high_intensity_run": 55,
}
MASK_EFFICIENCY = {
    "none": 0.00,
    "cloth": 0.30,
    "medical": 0.60,
    "n95": 0.95,
}

app = FastAPI(title="PulmoGuard Lung Exposure Engine", version="1.1.0")

try:
    toxic_dose_bundle = joblib.load(MODELS_DIR / "toxic_dose_model.joblib")
    lung_impact_bundle = joblib.load(MODELS_DIR / "lung_impact_model.joblib")
    anomaly_bundle = joblib.load(MODELS_DIR / "anomaly_model.joblib")
    ANOMALY_THRESHOLD = -anomaly_bundle["model"].offset_
    MODELS_LOADED = True
    MODELS_LOAD_ERROR = None
except Exception as e:
    toxic_dose_bundle = lung_impact_bundle = anomaly_bundle = None
    ANOMALY_THRESHOLD = None
    MODELS_LOADED = False
    MODELS_LOAD_ERROR = str(e)


def envelope(data: dict, message: str = "OK", code: int = 200, status: str = "success") -> dict:
    return {
        "status": status,
        "code": code,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "service": "python-ml",
    }


ActivityIntensity = Literal["resting", "light_jog",
                            "moderate_run", "high_intensity_run"]
MaskType = Literal["none", "cloth", "medical", "n95"]


class ToxicDoseRequest(BaseModel):
    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)
    co: float = Field(..., ge=0)
    no2: float = Field(..., ge=0)
    activity_intensity: ActivityIntensity
    duration_minutes: float = Field(..., gt=0)
    mask_type: MaskType = "none"


class LungImpactRequest(BaseModel):
    cumulative_toxic_load_score: float = Field(..., ge=0, le=100)
    age: int = Field(..., ge=1, le=120)
    asthma_history: bool = False
    weight_kg: float = Field(..., gt=0)
    baseline_lung_capacity_pct: float = Field(..., gt=0)


class FullExposureRequest(BaseModel):
    session_id: Optional[int] = None
    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)
    co: float = Field(..., ge=0)
    no2: float = Field(..., ge=0)
    activity_intensity: ActivityIntensity
    duration_minutes: float = Field(..., gt=0)
    mask_type: MaskType = "none"
    age: int = Field(..., ge=1, le=120)
    asthma_history: bool = False
    weight_kg: float = Field(..., gt=0)
    baseline_lung_capacity_pct: float = Field(..., gt=0)


class AnomalyRequest(BaseModel):
    sensor_value: float
    timestamp_hour: float = Field(..., ge=0, le=24)
    rolling_mean_1h: float
    z_score: float


class BatchRequest(BaseModel):
    items: List[FullExposureRequest]


class RawIotExposureRequest(BaseModel):
    zone_id: Optional[int] = None
    citizen_id: Optional[int] = None
    device_id: Optional[str] = None
    session_id: Optional[int] = None

    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)
    co: float = Field(..., ge=0)
    no2: float = Field(..., ge=0)
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0)

    heart_rate: float = Field(..., gt=0)
    resting_heart_rate: Optional[float] = Field(
        None, gt=0, description="Opsional, dari kalibrasi awal warga. Kalau ada, dipakai formula Karvonen yang lebih akurat."
    )

    hour: float = Field(..., ge=0, le=24)

    duration_minutes: Optional[float] = Field(None, gt=0)
    session_start_iso: Optional[str] = None
    session_end_iso: Optional[str] = None

    mask_type: MaskType = "none"

    age: int = Field(..., ge=1, le=120)
    asthma_history: bool = False
    weight_kg: float = Field(..., gt=0)
    baseline_lung_capacity_pct: float = Field(..., gt=0)


class InversionContextRequest(BaseModel):
    """Hanya butuh data Device 1 -- cocok untuk dashboard monitoring per-zona,
    tidak perlu data warga sama sekali."""
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0)
    hour: float = Field(..., ge=0, le=24)


def _require_models_loaded():
    if not MODELS_LOADED:
        raise HTTPException(
            status_code=503, detail=f"Model belum berhasil di-load: {MODELS_LOAD_ERROR}")


def _run_toxic_dose(req: ToxicDoseRequest) -> dict:
    rmv = ACTIVITY_RMV_BASE[req.activity_intensity]
    mask_eff = MASK_EFFICIENCY[req.mask_type]

    X = pd.DataFrame([{
        "pm25": req.pm25,
        "pm10": req.pm10,
        "co": req.co,
        "no2": req.no2,
        "rmv_liters_per_min": rmv,
        "duration_minutes": req.duration_minutes,
        "mask_efficiency": mask_eff,
    }])[toxic_dose_bundle["feature_cols"]]

    pred = toxic_dose_bundle["model"].predict(X)[0]
    result = dict(zip(toxic_dose_bundle["target_cols"], [
                  round(float(v), 2) for v in pred]))

    result["total_air_inhaled_liters"] = round(rmv * req.duration_minutes, 1)
    result["rmv_liters_per_min"] = rmv
    result["mask_efficiency"] = mask_eff
    return result


def _run_lung_impact(req: LungImpactRequest) -> dict:
    X = pd.DataFrame([{
        "cumulative_toxic_load_score": req.cumulative_toxic_load_score,
        "age": req.age,
        "asthma_history": int(req.asthma_history),
        "weight_kg": req.weight_kg,
        "baseline_lung_capacity_pct": req.baseline_lung_capacity_pct,
    }])[lung_impact_bundle["feature_cols"]]

    reg_pred = lung_impact_bundle["regressor"].predict(X)[0]
    clf_pred = lung_impact_bundle["classifier"].predict(X)[0]

    result = dict(zip(lung_impact_bundle["reg_target_cols"], [
                  round(float(v), 2) for v in reg_pred]))
    result["health_risk_category"] = clf_pred
    return result


def hr_to_activity_intensity(
    heart_rate: float, age: int, resting_heart_rate: Optional[float] = None
) -> ActivityIntensity:
    hr_max = max(220 - age, 1)
    if resting_heart_rate and resting_heart_rate > 0 and hr_max > resting_heart_rate:
        pct = (heart_rate - resting_heart_rate) / (hr_max - resting_heart_rate)
    else:
        pct = heart_rate / hr_max
    pct = max(0.0, pct)

    if pct < 0.50:
        return "resting"
    elif pct < 0.65:
        return "light_jog"
    elif pct < 0.80:
        return "moderate_run"
    else:
        return "high_intensity_run"


def compute_inversion_index(
    temperature_c: float, humidity_pct: float, wind_speed_ms: float, hour: float
) -> dict:
    hour_factor = 0.5 * (1 + np.cos(2 * np.pi * (hour - 3) / 24))
    wind_factor = float(np.clip(1 - wind_speed_ms / 8.0, 0, 1))
    humidity_factor = float(np.clip((humidity_pct - 40) / 60, 0, 1))
    temp_factor = float(np.clip((25 - temperature_c) / 15, 0, 1))

    inversion_index = float(np.clip(
        0.45 * hour_factor + 0.25 * wind_factor +
        0.15 * humidity_factor + 0.15 * temp_factor,
        0, 1,
    ))

    if inversion_index >= 0.70:
        level = "Severe"
    elif inversion_index >= 0.45:
        level = "Moderate"
    elif inversion_index >= 0.25:
        level = "Mild"
    else:
        level = "None"

    return {
        "inversion_index": round(inversion_index, 3),
        "inversion_level": level,
        "is_inversion_period": bool(inversion_index >= 0.45),
    }

# Endpoints


@app.get("/health")
def health():
    return envelope(
        data={
            "models_loaded": MODELS_LOADED,
            "load_error": MODELS_LOAD_ERROR,
            "toxic_dose_model": toxic_dose_bundle is not None,
            "lung_impact_model": lung_impact_bundle is not None,
            "anomaly_model": anomaly_bundle is not None,
        },
        message="Python ML service is running",
    )


@app.post("/predict/toxic-dose")
def predict_toxic_dose(req: ToxicDoseRequest):
    _require_models_loaded()
    return envelope(data=_run_toxic_dose(req), message="Toxic dose computed")


@app.post("/predict/lung-impact")
def predict_lung_impact(req: LungImpactRequest):
    _require_models_loaded()
    return envelope(data=_run_lung_impact(req), message="Lung impact computed")


@app.post("/predict/full-exposure")
def predict_full_exposure(req: FullExposureRequest):
    _require_models_loaded()

    toxic_result = _run_toxic_dose(ToxicDoseRequest(
        pm25=req.pm25, pm10=req.pm10, co=req.co, no2=req.no2,
        activity_intensity=req.activity_intensity,
        duration_minutes=req.duration_minutes,
        mask_type=req.mask_type,
    ))

    lung_result = _run_lung_impact(LungImpactRequest(
        cumulative_toxic_load_score=toxic_result["cumulative_toxic_load_score"],
        age=req.age,
        asthma_history=req.asthma_history,
        weight_kg=req.weight_kg,
        baseline_lung_capacity_pct=req.baseline_lung_capacity_pct,
    ))

    data = {
        "session_id": req.session_id,
        "computed_exposure_analysis": {
            "total_air_inhaled_liters": toxic_result["total_air_inhaled_liters"],
            "pm25_retained_micrograms": toxic_result["pm25_retained_micrograms"],
            "co_blood_saturation_estimation": f"+{toxic_result['co_blood_saturation_estimate']}% HbCO increase",
        },
        "lung_function_impact": {
            "cumulative_toxic_load_score": toxic_result["cumulative_toxic_load_score"],
            "lung_function_temporary_drop_pct": lung_result["lung_function_temporary_drop_pct"],
            "alveoli_recovery_time_hours": lung_result["alveoli_recovery_time_hours"],
            "health_risk_category": lung_result["health_risk_category"],
        },
    }
    return envelope(data=data, message="Exposure analysis computed")


@app.post("/predict/full-exposure-iot")
def predict_full_exposure_iot(req: RawIotExposureRequest):
    _require_models_loaded()

    duration_minutes = req.duration_minutes
    if duration_minutes is None:
        if req.session_start_iso and req.session_end_iso:
            # [FIX #5] Sebelumnya datetime.fromisoformat() dipanggil tanpa
            # try/except -> kalau formatnya tidak valid (atau salah satu
            # naive & yang lain timezone-aware), exception ini TIDAK
            # tertangkap dan klien menerima 500 Internal Server Error yang
            # tidak informatif, bukan 422 yang jelas. Selain itu, kalau
            # session_end_iso lebih awal dari session_start_iso (data
            # rusak), delta negatif sebelumnya diam-diam dipaksa jadi 1
            # menit oleh max(..., 1) tanpa peringatan apapun.
            try:
                start = datetime.fromisoformat(req.session_start_iso)
                end = datetime.fromisoformat(req.session_end_iso)
                delta_minutes = (end - start).total_seconds() / 60
            except (TypeError, ValueError) as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Format session_start_iso/session_end_iso tidak valid: {e}",
                )
            if delta_minutes <= 0:
                raise HTTPException(
                    status_code=422,
                    detail="session_end_iso harus setelah session_start_iso",
                )
            duration_minutes = max(delta_minutes, 1)
        else:
            raise HTTPException(
                status_code=422,
                detail="duration_minutes wajib diisi, atau kirim session_start_iso & session_end_iso",
            )

    activity_intensity = hr_to_activity_intensity(
        heart_rate=req.heart_rate, age=req.age, resting_heart_rate=req.resting_heart_rate
    )

    full_req = FullExposureRequest(
        session_id=req.session_id,
        pm25=req.pm25, pm10=req.pm10, co=req.co, no2=req.no2,
        activity_intensity=activity_intensity,
        duration_minutes=duration_minutes,
        mask_type=req.mask_type,
        age=req.age,
        asthma_history=req.asthma_history,
        weight_kg=req.weight_kg,
        baseline_lung_capacity_pct=req.baseline_lung_capacity_pct,
    )
    base_result = predict_full_exposure(full_req)["data"]

    inversion = compute_inversion_index(
        temperature_c=req.temperature, humidity_pct=req.humidity,
        wind_speed_ms=req.wind_speed, hour=req.hour,
    )

    base_result["derived_activity_intensity"] = activity_intensity
    base_result["nocturnal_inversion_context"] = {
        **inversion,
        "zone_id": req.zone_id,
        "citizen_id": req.citizen_id,
        "device_id": req.device_id,
        "advisory": (
            "PERINGATAN: paparan terjadi pada jendela waktu dengan estimasi inversi "
            "suhu tinggi -- polutan permukaan cenderung terjebak & tidak terdispersi."
            if inversion["is_inversion_period"] else
            "Kondisi atmosfer relatif normal, dispersi polutan tidak terhambat secara signifikan."
        ),
    }
    return envelope(data=base_result, message="Exposure analysis (raw IoT input) computed")


@app.post("/context/inversion-index")
def inversion_index_endpoint(req: InversionContextRequest):
    """
    Indeks inversi murni dari data Device 1 (zona) -- tidak butuh data warga
    sama sekali. Cocok dipanggil terus-menerus untuk dashboard monitoring
    per-zona (misalnya tiap kali Device 1 mengirim reading baru).
    """
    data = compute_inversion_index(
        temperature_c=req.temperature, humidity_pct=req.humidity,
        wind_speed_ms=req.wind_speed, hour=req.hour,
    )
    return envelope(data=data, message="Inversion index computed")


@app.post("/detect/anomaly")
def detect_anomaly(req: AnomalyRequest):
    _require_models_loaded()

    X = pd.DataFrame([{
        "sensor_value": req.sensor_value,
        "timestamp_hour": req.timestamp_hour,
        "rolling_mean_1h": req.rolling_mean_1h,
        "z_score": req.z_score,
    }])[anomaly_bundle["feature_cols"]]

    model = anomaly_bundle["model"]
    raw_score = -model.score_samples(X)[0]
    is_anomaly = bool(raw_score >= ANOMALY_THRESHOLD)

    if not is_anomaly:
        severity = "Normal"
    elif raw_score < ANOMALY_THRESHOLD + 0.05:
        severity = "Low"
    elif raw_score < ANOMALY_THRESHOLD + 0.10:
        severity = "Medium"
    elif raw_score < ANOMALY_THRESHOLD + 0.15:
        severity = "High"
    else:
        severity = "Critical"

    result = {
        "is_anomaly": is_anomaly,
        "anomaly_score": round(float(raw_score), 4),
        "severity": severity,
    }
    return envelope(data=result, message="Anomaly detection computed")


@app.get("/model/feature-importance")
def feature_importance():
    _require_models_loaded()

    toxic_importance = dict(zip(
        toxic_dose_bundle["feature_cols"],
        [round(float(v), 4)
         for v in toxic_dose_bundle["model"].feature_importances_],
    ))

    lung_reg_estimators = lung_impact_bundle["regressor"].estimators_
    lung_reg_importance_arr = np.mean(
        [est.feature_importances_ for est in lung_reg_estimators], axis=0)
    lung_reg_importance = dict(zip(
        lung_impact_bundle["feature_cols"], [
            round(float(v), 4) for v in lung_reg_importance_arr]
    ))

    lung_clf_importance = dict(zip(
        lung_impact_bundle["feature_cols"],
        [round(float(v), 4)
         for v in lung_impact_bundle["classifier"].feature_importances_],
    ))

    data = {
        "toxic_dose_estimator": toxic_importance,
        "lung_impact_regressor": lung_reg_importance,
        "lung_impact_classifier": lung_clf_importance,
        "anomaly_detector": "Isolation Forest tidak punya feature_importances_ bawaan di scikit-learn",
    }
    return envelope(data=data, message="Feature importance retrieved")


@app.post("/predict/batch")
def predict_batch(req: BatchRequest):
    _require_models_loaded()

    results = [predict_full_exposure(item)["data"] for item in req.items]
    return envelope(data={"count": len(results), "results": results}, message="Batch prediction computed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
