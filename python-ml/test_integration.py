import json
import time
import datetime
import threading

import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = f"pulmoguard-bridge-{int(time.time())}"

TOPIC_DEVICE1 = "smartcity/environment/1/sensor"
TOPIC_DEVICE2 = "wearable/device_01/heartrate"

API_URL = "http://127.0.0.1:5000/predict/full-exposure-iot"

CITIZEN_PROFILE = {
    "age": 28,
    "weight_kg": 68.0,
    "asthma_history": False,
    "baseline_lung_capacity_pct": 97.5,
    "resting_heart_rate": 68.0,
}

SESSION_CONFIG = {
    "duration_minutes": 30.0,    # durasi sesi olahraga (menit)
    "mask_type": "cloth",  # "none" | "cloth" | "medical" | "n95"
    "session_id": 9901,
}

state = {
    "device1": None,
    "device2": None,
    "lock": threading.Lock(),
}


def heart_rate_to_activity_type(heart_rate: int) -> str:
    if heart_rate < 90:
        return "rest"
    elif heart_rate <= 130:
        return "walking"
    else:
        return "running"


def temperature_to_inversion_flag(temperature_c: float) -> int:
    return 1 if temperature_c < 25.0 else 0


def try_send_combined_payload():
    with state["lock"]:
        d1 = state["device1"]
        d2 = state["device2"]

    if d1 is None or d2 is None:
        missing = []
        if d1 is None:
            missing.append("Device 1 (Stasiun Udara)")
        if d2 is None:
            missing.append("Device 2 (Smartwatch)")
        print(f"  ⏳  Menunggu data dari: {', '.join(missing)}")
        return

    zone_d1 = d1.get("zone_id")
    zone_d2 = d2.get("zone_id")

    if zone_d1 != zone_d2:
        print(
            f"  ⚠️   zone_id TIDAK COCOK → D1={zone_d1}, D2={zone_d2}. Payload tidak dikirim.")
        print(f"       (Citizen sedang di zona berbeda dari stasiun udara yang dipantau)")
        return

    heart_rate = d2.get("heart_rate", 80)
    temperature = d1.get("temperature", 28.0)
    activity_label = heart_rate_to_activity_type(heart_rate)
    inversion_flag = temperature_to_inversion_flag(temperature)

    current_hour = datetime.datetime.now().hour + datetime.datetime.now().minute / 60.0

    payload = {
        # Identitas & relasi
        "zone_id": zone_d1,
        "citizen_id": d2.get("citizen_id", 12),
        "device_id": d2.get("device_id", "device_01"),
        "session_id": SESSION_CONFIG["session_id"],

        "pm25": d1.get("pm25", 0.0),
        "pm10": d1.get("pm10", 0.0),
        "co": d1.get("co",   0.0),
        "no2": d1.get("no2",  0.0),
        "temperature": temperature,
        "humidity": d1.get("humidity",   72.0),
        "wind_speed": d1.get("wind_speed",  2.5),

        "heart_rate": heart_rate,
        "resting_heart_rate": CITIZEN_PROFILE["resting_heart_rate"],

        "hour": round(current_hour, 2),

        "duration_minutes": SESSION_CONFIG["duration_minutes"],
        "mask_type": SESSION_CONFIG["mask_type"],

        "age": CITIZEN_PROFILE["age"],
        "asthma_history": CITIZEN_PROFILE["asthma_history"],
        "weight_kg": CITIZEN_PROFILE["weight_kg"],
        "baseline_lung_capacity_pct": CITIZEN_PROFILE["baseline_lung_capacity_pct"],
    }

    print("\n" + "═" * 60)
    print("      DATA GABUNGAN SIAP DIKIRIM")
    print("═" * 60)
    print(f"      Zone ID    : {zone_d1} (COCOK ✓)")
    print(
        f"      Citizen ID : {payload['citizen_id']}  |  Device: {payload['device_id']}")
    print(
        f"      Waktu Sesi : {current_hour:.1f}h  |  Durasi: {payload['duration_minutes']} menit")
    print(f"      Masker     : {payload['mask_type']}")
    print()
    print("  [Device 1 — Stasiun Udara]")
    print(f"    PM2.5     : {payload['pm25']:.2f} µg/m³")
    print(f"    PM10      : {payload['pm10']:.2f} µg/m³")
    print(f"    CO        : {payload['co']:.3f} mg/m³")
    print(f"    NO2       : {payload['no2']:.2f} µg/m³")
    print(
        f"    Suhu      : {payload['temperature']:.2f} °C  →  Inversi={inversion_flag}")
    print(
        f"    Kelembaban: {payload['humidity']:.1f}%  |  Angin: {payload['wind_speed']} m/s")
    print()
    print("  [Device 2 — Smartwatch Warga]")
    print(f"    Heart Rate: {heart_rate} bpm  →  Aktivitas: {activity_label}")
    print(
        f"    Usia: {payload['age']} th  |  BB: {payload['weight_kg']} kg  |  Asma: {payload['asthma_history']}")
    print()
    print(f"      POST → {API_URL}")
    print("─" * 60)

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        print_api_result(result, payload)

    except requests.exceptions.ConnectionError:
        print("      KONEKSI GAGAL: FastAPI tidak berjalan di port 5000.")
        print("      Pastikan server sudah aktif:  uvicorn main:app --port 5000")
    except requests.exceptions.Timeout:
        print("      TIMEOUT: FastAPI tidak merespons dalam 10 detik.")
    except requests.exceptions.HTTPError as e:
        print(f"      HTTP ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"      ERROR tak terduga: {e}")


def print_api_result(result: dict, payload: dict):
    """Tampilkan hasil respons FastAPI dengan format rapi di terminal."""
    print()
    status_icon = "✅" if result.get("status") == "success" else "⚠️"
    print(f"  {status_icon}  RESPONS FASTAPI ({result.get('code', '?')} {result.get('status', '?')})")
    print(f"      {result.get('message', '')}")
    print(f"      Timestamp: {result.get('timestamp', '-')}")
    print()

    data = result.get("data", {})
    if not data:
        print("  (Tidak ada data dalam respons)")
        return

    exposure = data.get("computed_exposure_analysis", {})
    if exposure:
        print("      ANALISIS PAPARAN POLUTAN")
        print(
            f"    Total Udara Terhirup  : {exposure.get('total_air_inhaled_liters', '-')} liter")
        print(
            f"    PM2.5 Tertahan di Paru: {exposure.get('pm25_retained_micrograms', '-')} µg")
        print(
            f"    Estimasi CO Darah     : {exposure.get('co_blood_saturation_estimation', '-')}")
        print()

    lung = data.get("lung_function_impact", {})
    if lung:
        risk_cat = lung.get("health_risk_category", "-")
        risk_icons = {"Safe": "🟢", "Moderate": "🟡",
                      "Unhealthy": "🟠", "Critical": "🔴"}
        risk_icon = risk_icons.get(risk_cat, "⚪")
        print("  🫁  DAMPAK FUNGSI PARU-PARU")
        print(
            f"    Toxic Load Score      : {lung.get('cumulative_toxic_load_score', '-'):.2f} / 100")
        print(
            f"    Penurunan Fungsi Paru : {lung.get('lung_function_temporary_drop_pct', '-'):.2f} %")
        print(
            f"    Waktu Pemulihan Alveol: {lung.get('alveoli_recovery_time_hours', '-'):.1f} jam")
        print(f"    Kategori Risiko       : {risk_icon} {risk_cat}")
        print()

    derived_activity = data.get("derived_activity_intensity")
    if derived_activity:
        print(f"  🏃  Aktivitas (Karvonen/HR): {derived_activity}")

    inversion = data.get("nocturnal_inversion_context", {})
    if inversion:
        inv_level = inversion.get("inversion_level", "-")
        inv_index = inversion.get("inversion_index", 0)
        is_inv = inversion.get("is_inversion_period", False)
        inv_icons = {"None": "🌤️", "Mild": "🌥️",
                     "Moderate": "🌫️", "Severe": "⚫"}
        inv_icon = inv_icons.get(inv_level, "❓")
        advisory = inversion.get("advisory", "")
        print("    KONTEKS INVERSI SUHU NOKTURNAL")
        print(f"    {inv_icon} Level : {inv_level}  (Indeks: {inv_index:.3f})")
        print(
            f"    Jendela Inversi : {'AKTIF ' if is_inv else 'Tidak aktif'}")
        print(f"    Advisory        : {advisory}")
        print()

    print("═" * 60)


def on_connect(client, userdata, flags, rc):
    rc_messages = {
        0: "Terhubung ",
        1: "Versi protokol ditolak",
        2: "Client ID tidak valid",
        3: "Server tidak tersedia",
        4: "Username / password salah",
        5: "Tidak diotorisasi",
    }
    print(f"\n     MQTT → {rc_messages.get(rc, f'Kode tidak dikenal ({rc})')}")
    if rc == 0:
        client.subscribe(TOPIC_DEVICE1)
        client.subscribe(TOPIC_DEVICE2)
        print(f"      Subscribe ke: {TOPIC_DEVICE1}")
        print(f"      Subscribe ke: {TOPIC_DEVICE2}\n")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"\n     MQTT terputus (kode {rc}). Mencoba reconnect...")


def on_message(client, userdata, msg):
    topic = msg.topic
    raw = msg.payload.decode("utf-8", errors="replace")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"     Gagal parse JSON dari [{topic}]: {e}")
        print(f"      Raw: {raw}")
        return

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if topic == TOPIC_DEVICE1:
        print(
            f"\n[{timestamp}]   Device 1 (Stasiun Udara) — Zone {data.get('zone_id', '?')}")
        print(f"    PM2.5={data.get('pm25', '?'):.2f}  PM10={data.get('pm10', '?'):.2f}"
              f"  CO={data.get('co', '?'):.3f}  NO2={data.get('no2', '?'):.2f}")
        print(f"    Suhu={data.get('temperature', '?'):.1f}°C"
              f"  RH={data.get('humidity', '?'):.0f}%"
              f"  Angin={data.get('wind_speed', '?')}m/s")
        with state["lock"]:
            state["device1"] = data

    elif topic == TOPIC_DEVICE2:
        hr = data.get("heart_rate", 0)
        activity = heart_rate_to_activity_type(hr)
        print(f"\n[{timestamp}]   Device 2 (Smartwatch) — Citizen {data.get('citizen_id', '?')}"
              f" @ Zone {data.get('zone_id', '?')}")
        print(f"    HR={hr} bpm  →  Aktivitas: {activity}")
        with state["lock"]:
            state["device2"] = data

    try_send_combined_payload()


# ENTRY POINT
def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   PulmoGuard — MQTT ↔ FastAPI Integration Bridge         ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print(f"║  Broker  : {MQTT_BROKER}:{MQTT_PORT:<36}║")
    print(f"║  API     : {API_URL:<47}║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Profil Warga (dummy):")
    for k, v in CITIZEN_PROFILE.items():
        print(f"    {k:<30} : {v}")
    print()
    print("  Konfigurasi Sesi:")
    for k, v in SESSION_CONFIG.items():
        print(f"    {k:<30} : {v}")
    print()
    print("  Tekan Ctrl+C untuk berhenti.\n")
    print("─" * 60)

    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    print(f"  Menghubungkan ke {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n     Dihentikan oleh pengguna. Sampai jumpa!\n")
        client.disconnect()


if __name__ == "__main__":
    main()
