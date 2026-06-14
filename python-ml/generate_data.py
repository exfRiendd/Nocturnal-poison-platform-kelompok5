import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
N = 10000

# Generate timestamp mulai 1 tahun lalu, interval 1 jam
start_date = datetime.now() - timedelta(hours=N)
timestamps = [start_date + timedelta(hours=i) for i in range(N)]

# Lokasi sensor (5 titik di kota)
locations = ["Pusat_Kota", "Industri_Barat",
             "Perumahan_Utara", "Jalan_Raya_Timur", "Taman_Selatan"]
location_col = np.random.choice(locations, size=N)

# Jam dan musim mempengaruhi polusi (lebih realistis)
hours = np.array([t.hour for t in timestamps])
is_rush_hour = ((hours >= 7) & (hours <= 9)) | ((hours >= 16) & (hours <= 19))
is_night = (hours >= 22) | (hours <= 5)

# 1. PM2.5 (µg/m³) — Basis distribusi normal yang diperlebar
pm25_base = np.random.normal(50, 35, N)
pm25_base += is_rush_hour * np.random.uniform(10, 30, N)
pm25_base -= is_night * np.random.uniform(5, 15, N)
pm25 = np.clip(pm25_base, 5, 350).round(2)

# 2. Kondisi inversi suhu (polusi terperangkap) — mempengaruhi PM2.5 awal
temperature_inversion = np.random.choice([0, 1], size=N, p=[0.85, 0.15])
pm25 = np.where(temperature_inversion == 1, pm25 *
                np.random.uniform(1.5, 2.5, N), pm25).round(2)

# 3. Event Ekstrim (Kebakaran Hutan/Asap Industri Berat) sebesar 3% dari total data
extreme_event = np.random.choice([0, 1], size=N, p=[0.97, 0.03])
pm25 = np.where(extreme_event == 1, np.random.uniform(
    220, 350, N), pm25).round(2)
pm25 = np.clip(pm25, 5, 350)  # Kunci batas atas PM2.5 di angka 350

# 4. HITUNG PM10 SEKARANG (Setelah PM2.5 final didapatkan agar logis secara fisis)
pm10 = np.clip(pm25 * np.random.uniform(1.3, 2.0, N) +
               np.random.normal(10, 5, N), 10, 500).round(2)

# 5. Sinkronisasi Gas Beracun Lain (CO dan NO2) akibat Rush Hour & Event Ekstrim
co = np.clip(np.random.normal(1.2, 0.5, N) + is_rush_hour * 0.8, 0.1, 10)
co = np.where(extreme_event == 1, np.clip(co * 2.5, 0.1, 10), co).round(3)

no2 = np.clip(np.random.normal(40, 15, N) + is_rush_hour * 20, 5, 200)
no2 = np.where(extreme_event == 1, np.clip(no2 * 2.0, 5, 200), no2).round(2)

# Faktor Meteorologi
temperature = np.clip(np.random.normal(28, 5, N), 18, 40).round(1)
humidity = np.clip(np.random.normal(70, 15, N), 30, 100).round(1)
wind_speed = np.clip(np.random.exponential(2, N), 0, 15).round(2)

# Fungsi Hitung AQI berdasar PM2.5 Final


def calculate_aqi(pm25_val):
    if pm25_val <= 12:
        return round((50/12) * pm25_val)
    elif pm25_val <= 35.4:
        return round(50 + (50/23.4) * (pm25_val - 12))
    elif pm25_val <= 55.4:
        return round(100 + (50/20) * (pm25_val - 35.4))
    elif pm25_val <= 150.4:
        return round(150 + (50/95) * (pm25_val - 55.4))
    else:
        return round(200 + (100/149.6) * (pm25_val - 150.4))


aqi = np.array([calculate_aqi(v) for v in pm25])
aqi = np.clip(aqi, 0, 500)

# Pelabelan Kategori


def aqi_category(aqi_val):
    if aqi_val <= 50:
        return "Baik"
    elif aqi_val <= 100:
        return "Sedang"
    elif aqi_val <= 150:
        return "Tidak Sehat untuk Sensitif"
    elif aqi_val <= 200:
        return "Tidak Sehat"
    elif aqi_val <= 300:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"


aqi_label = [aqi_category(v) for v in aqi]

# Label Anomali
is_anomaly = ((pm25 > 150) | (temperature_inversion == 1)).astype(int)

# Susun ke DataFrame
df = pd.DataFrame({
    "timestamp": timestamps,
    "location": location_col,
    "pm25": pm25,
    "pm10": pm10,
    "co": co,
    "no2": no2,
    "temperature": temperature,
    "humidity": humidity,
    "wind_speed": wind_speed,
    "temperature_inversion": temperature_inversion,
    "aqi": aqi,
    "aqi_category": aqi_label,
    "is_anomaly": is_anomaly
})

# Simpan Dataset
output_path = "data/pollution_data.csv"
df.to_csv(output_path, index=False)

print(f"Dataset berhasil dibuat: {output_path}")
print(f"Total baris: {len(df)}")
print(f"\nDistribusi AQI Category Baru:")
print(df["aqi_category"].value_counts())
print(
    f"\nJumlah anomali: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
