import numpy as np
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SEED = 42

# Mapping konstanta sesuai Section 6.6 (Catatan implementasi)
ACTIVITY_RMV_BASE = {
    "resting": 7,
    "light_jog": 25,
    "moderate_run": 40,
    "high_intensity_run": 55,
}
ACTIVITY_WEIGHTS = {
    "resting": 0.10,
    "light_jog": 0.25,
    "moderate_run": 0.40,
    "high_intensity_run": 0.25,
}

MASK_EFFICIENCY = {
    "none": 0.00,
    "cloth": 0.30,
    "medical": 0.60,
    "n95": 0.95,
}
MASK_WEIGHTS = {
    "none": 0.30,
    "cloth": 0.25,
    "medical": 0.20,
    "n95": 0.25,
}


def _weighted_choice(rng: np.random.Generator, mapping: dict, weights: dict, n: int):
    keys = list(mapping.keys())
    probs = np.array([weights[k] for k in keys])
    probs = probs / probs.sum()
    return rng.choice(keys, size=n, p=probs)


# 1. TOXIC DOSE ESTIMATOR DATASET
def generate_toxic_dose_dataset(n: int, rng: np.random.Generator) -> pd.DataFrame:
    activity = _weighted_choice(rng, ACTIVITY_RMV_BASE, ACTIVITY_WEIGHTS, n)
    mask_type = _weighted_choice(rng, MASK_EFFICIENCY, MASK_WEIGHTS, n)

    rmv_base = np.array([ACTIVITY_RMV_BASE[a] for a in activity], dtype=float)
    rmv_liters_per_min = np.clip(
        rmv_base + rng.normal(0, rmv_base * 0.08, n), 3, 70)

    mask_efficiency = np.array([MASK_EFFICIENCY[m]
                               for m in mask_type], dtype=float)

    duration_minutes = np.clip(
        rng.gamma(shape=3.0, scale=15.0, size=n), 10, 150)

    # Konsentrasi polutan (skala realistis kualitas udara outdoor)
    pm25 = np.clip(rng.lognormal(mean=np.log(35), sigma=0.6, size=n), 5, 300)
    pm10 = np.clip(pm25 * rng.uniform(1.3, 2.0, n) +
                   rng.normal(0, 5, n), pm25, 500)
    co = np.clip(rng.lognormal(mean=np.log(2.5), sigma=0.7, size=n), 0.2, 20)
    no2 = np.clip(rng.lognormal(mean=np.log(30), sigma=0.6, size=n), 2, 200)

    total_air_inhaled_liters = rmv_liters_per_min * duration_minutes
    filt = 1 - mask_efficiency

    # pm2.5 retained (µg): konsentrasi µg/m3 -> µg/L (/1000) * volume udara terhirup (L)
    pm25_retained_micrograms = (pm25 / 1000) * total_air_inhaled_liters * filt
    pm25_retained_micrograms = np.round(pm25_retained_micrograms, 2)

    # CO retained (mg) -> dikonversi jadi estimasi kenaikan %HbCO (synthetic scaling)
    co_inhaled_mg = (co * 1.145 / 1000) * total_air_inhaled_liters * filt
    co_blood_saturation_estimate = np.clip(
        co_inhaled_mg * 0.08 + rng.normal(0, 0.08, n), 0, 12
    )
    co_blood_saturation_estimate = np.round(co_blood_saturation_estimate, 2)

    # Cumulative toxic load score (0-100), mengikuti formula dasar D = ΣC×RMV×t×(1-mask)
    raw_dose = (
        (0.45 * pm25 + 0.22 * pm10 + 9.0 * co + 0.55 * no2)
        * rmv_liters_per_min
        * duration_minutes
        * filt
        / 1_000_000
    )
    cumulative_toxic_load_score = 100 * (1 - np.exp(-raw_dose * 8))
    cumulative_toxic_load_score = np.clip(
        cumulative_toxic_load_score + rng.normal(0, 2.5, n), 0, 100
    )
    cumulative_toxic_load_score = np.round(cumulative_toxic_load_score, 2)

    df = pd.DataFrame(
        {
            "activity_intensity": activity,  # metadata, bukan fitur model
            "mask_type": mask_type,  # metadata, bukan fitur model
            "pm25": np.round(pm25, 2),
            "pm10": np.round(pm10, 2),
            "co": np.round(co, 2),
            "no2": np.round(no2, 2),
            "rmv_liters_per_min": np.round(rmv_liters_per_min, 2),
            "duration_minutes": np.round(duration_minutes, 1),
            "mask_efficiency": mask_efficiency,
            "cumulative_toxic_load_score": cumulative_toxic_load_score,
            "pm25_retained_micrograms": pm25_retained_micrograms,
            "co_blood_saturation_estimate": co_blood_saturation_estimate,
        }
    )
    return df

# 2. LUNG FUNCTION IMPACT MODEL DATASET


def generate_lung_impact_dataset(toxic_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(toxic_df)
    toxic_load_score = toxic_df["cumulative_toxic_load_score"].to_numpy()

    age = np.clip(rng.normal(32, 9, n), 16, 70).round(0)
    asthma_history = rng.choice([0, 1], size=n, p=[0.85, 0.15])
    weight_kg = np.clip(rng.normal(65, 12, n), 40, 120).round(1)
    baseline_lung_capacity_pct = np.clip(
        rng.normal(95, 8, n), 60, 115).round(1)

    age_factor = np.clip(1 + (age - 30) * 0.01, 0.7, 1.5)
    asthma_factor = np.where(asthma_history == 1, 1.6, 1.0)
    baseline_factor = np.clip(
        1 + (100 - baseline_lung_capacity_pct) * 0.012, 0.6, 1.8)

    lung_function_temporary_drop_pct = (
        toxic_load_score * 0.055 * age_factor * asthma_factor * baseline_factor
        + rng.normal(0, 1.2, n)
    )
    lung_function_temporary_drop_pct = np.clip(
        lung_function_temporary_drop_pct, 0, 40).round(2)

    alveoli_recovery_time_hours = (
        lung_function_temporary_drop_pct * 3.2 * (1 + 0.15 * asthma_factor)
        + (age - 16) * 0.05
        + rng.normal(0, 3, n)
    )
    alveoli_recovery_time_hours = np.clip(
        alveoli_recovery_time_hours, 1, 120).round(1)

    # Skor komposit utk kategori risiko (+noise biar boundary nggak terlalu tegas)
    composite = (
        toxic_load_score * 0.5
        + lung_function_temporary_drop_pct * 2.2
        + rng.normal(0, 4, n)
    )

    def categorize(score):
        if score < 18:
            return "Safe"
        elif score < 38:
            return "Moderate"
        elif score < 58:
            return "Unhealthy"
        else:
            return "Critical"

    health_risk_category = np.array([categorize(s) for s in composite])

    df = pd.DataFrame(
        {
            "cumulative_toxic_load_score": toxic_load_score,
            "age": age.astype(int),
            "asthma_history": asthma_history.astype(int),
            "weight_kg": weight_kg,
            "baseline_lung_capacity_pct": baseline_lung_capacity_pct,
            "lung_function_temporary_drop_pct": lung_function_temporary_drop_pct,
            "alveoli_recovery_time_hours": alveoli_recovery_time_hours,
            "health_risk_category": health_risk_category,
        }
    )
    return df

# 3. SENSOR ANOMALY DETECTOR DATASET


def generate_anomaly_dataset(n_zones: int, readings_per_zone: int, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for zone_id in range(n_zones):
        base_level = rng.uniform(15, 60)
        start_hour = rng.integers(0, 24)
        values, hours, is_anom_flags = [], [], []

        for t in range(readings_per_zone):
            hour = (start_hour + t * 5 / 60) % 24
            diurnal = 10 * np.exp(-((hour - 7) ** 2) / 8) + \
                12 * np.exp(-((hour - 18) ** 2) / 8)
            value = base_level + diurnal + rng.normal(0, 4)

            is_anomaly = False
            if rng.random() < 0.04:  # ~4% anomali (sensor rusak / lonjakan ekstrem)
                if rng.random() < 0.5:
                    value = value * rng.uniform(3.5, 8.0)
                else:
                    value = max(0.5, value * rng.uniform(0.01, 0.1))
                is_anomaly = True

            value = max(0.1, value)
            values.append(value)
            hours.append(hour)
            is_anom_flags.append(is_anomaly)

        zone_df = pd.DataFrame(
            {"zone_id": zone_id, "sensor_value": values,
                "timestamp_hour": hours, "is_anomaly": is_anom_flags}
        )
        zone_df["rolling_mean_1h"] = zone_df["sensor_value"].rolling(
            window=12, min_periods=1).mean()
        rolling_std = zone_df["sensor_value"].rolling(
            window=12, min_periods=1).std().fillna(0)
        zone_df["z_score"] = (zone_df["sensor_value"] -
                              zone_df["rolling_mean_1h"]) / (rolling_std + 1e-3)
        rows.append(zone_df)

    df = pd.concat(rows, ignore_index=True)
    df["sensor_value"] = df["sensor_value"].round(2)
    df["timestamp_hour"] = df["timestamp_hour"].round(2)
    df["rolling_mean_1h"] = df["rolling_mean_1h"].round(2)
    df["z_score"] = df["z_score"].round(3)
    return df[["sensor_value", "timestamp_hour", "rolling_mean_1h", "z_score", "is_anomaly", "zone_id"]]


# ---------------------------------------------------------------------------
def main():
    rng = np.random.default_rng(SEED)

    print("Generating toxic_dose_dataset.csv ...")
    toxic_df = generate_toxic_dose_dataset(n=5500, rng=rng)
    toxic_df.to_csv(OUTPUT_DIR / "toxic_dose_dataset.csv", index=False)
    print(f"  -> {len(toxic_df)} rows")

    print("\nGenerating lung_impact_dataset.csv ...")
    lung_df = generate_lung_impact_dataset(toxic_df, rng=rng)
    lung_df.to_csv(OUTPUT_DIR / "lung_impact_dataset.csv", index=False)
    print(f"  -> {len(lung_df)} rows")
    print("  Distribusi health_risk_category:")
    print(lung_df["health_risk_category"].value_counts(
        normalize=True).round(3))

    print("\nGenerating anomaly_dataset.csv ...")
    anomaly_df = generate_anomaly_dataset(
        n_zones=25, readings_per_zone=220, rng=rng)
    anomaly_df.to_csv(OUTPUT_DIR / "anomaly_dataset.csv", index=False)
    print(f"  -> {len(anomaly_df)} rows")
    print(f"  Proporsi anomali: {anomaly_df['is_anomaly'].mean():.3%}")

    print("\nSelesai. File tersimpan di:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
