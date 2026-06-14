import json
import os
import random
import time
from datetime import datetime, timezone, timedelta

import paho.mqtt.client as mqtt

# Konfigurasi broker dan interval
MQTT_HOST    = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT    = int(os.getenv("MQTT_PORT", 1883))
INTERVAL_SEC = int(os.getenv("INTERVAL_SEC", 30))

# Zone yang disimulasikan (sesuai tabel zones di DB)
ZONES = {
    1: "Margonda - Depok",
    2: "Lenteng Agung",
    3: "Pasar Minggu",
    4: "Mampang Prapatan",
}

WIB = timezone(timedelta(hours=7))

# Threshold AQI
AQI_WARNING  = 150
AQI_DANGER   = 200
AQI_CRITICAL = 300


def inversion_factor(hour):
    """
    Hitung seberapa parah lapisan inversi atmosfer berdasarkan jam WIB.
    Inversi aktif jam 22:00 - 06:00, puncaknya 23:00 - 04:00.
    Return 0.0 (normal) sampai 1.0 (inversi penuh).
    """
    if hour >= 23 or hour <= 4:
        return 1.0
    elif hour == 22:
        return 0.5
    elif hour in (5, 6):
        return max(0.0, 1.0 - (hour - 4) * 0.5)
    return 0.0


def generate_reading(zone_id, now):
    factor = inversion_factor(now.hour)

    # PM2.5 meningkat drastis saat inversi (polutan terperangkap di bawah)
    pm25 = round(random.uniform(20, 50) + random.uniform(60, 230) * factor, 2)
    pm10 = round(pm25 * random.uniform(1.4, 1.8), 2)

    no2 = round(random.uniform(0.02, 0.06) + random.uniform(0.03, 0.12) * factor, 3)
    co  = round(random.uniform(0.5, 2.0) + random.uniform(1.0, 4.5) * factor, 3)

    # O3 justru lebih tinggi siang (proses fotokimia)
    o3 = round(random.uniform(0.01, 0.08) * (1 - factor * 0.6), 3)

    # Suhu turun, kelembapan naik, angin melemah saat inversi
    temperature = round(random.uniform(26, 32) - random.uniform(3, 6) * factor, 2)
    humidity    = round(min(random.uniform(60, 70) + random.uniform(10, 20) * factor, 99.9), 2)
    wind_speed  = round(max(random.uniform(1.5, 4.0) * (1 - factor * 0.85), 0.1), 2)

    # AQI sederhana berbasis PM2.5 sebagai polutan dominan
    aqi = round(pm25 * 1.5 + no2 * 200 + co * 10, 2)

    return {
        "zone_id":          zone_id,
        "pm25":             pm25,
        "pm10":             pm10,
        "no2":              no2,
        "co":               co,
        "o3":               o3,
        "temperature":      temperature,
        "humidity":         humidity,
        "wind_speed":       wind_speed,
        "aqi":              aqi,
        "recorded_at":      now.isoformat(),
        "inversion_active": factor > 0.5,
    }


def get_severity(aqi):
    if aqi >= AQI_CRITICAL:
        return "critical"
    if aqi >= AQI_DANGER:
        return "high"
    if aqi >= AQI_WARNING:
        return "medium"
    return "low"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Terhubung ke broker {MQTT_HOST}:{MQTT_PORT}")
    else:
        print(f"Gagal konek, kode: {rc}")


def on_disconnect(client, userdata, rc, properties=None, reason=None):
    print(f"Terputus dari broker (rc={rc}). Mencoba reconnect...")


def main():
    print(f"IoT Simulator - Nocturnal Poison Platform")
    print(f"Broker: {MQTT_HOST}:{MQTT_PORT} | Interval: {INTERVAL_SEC}s")
    print(f"Zones: {list(ZONES.values())}\n")

    try:
        client = mqtt.Client(
            client_id="nocturnal-simulator",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
    except AttributeError:
        # paho-mqtt < 2.0
        client = mqtt.Client(client_id="nocturnal-simulator")
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"Tidak bisa konek: {e}. Retry in 5s...")
        time.sleep(5)
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

    client.loop_start()
    print("Mulai publish... (Ctrl+C untuk stop)\n")

    try:
        while True:
            now = datetime.now(WIB)

            for zone_id, zone_name in ZONES.items():
                data = generate_reading(zone_id, now)

                # Publish data sensor reguler (Skenario S1)
                topic   = f"smartcity/environment/{zone_id}/sensor"
                payload = json.dumps(data)
                client.publish(topic, payload, qos=1)

                inv_status = "INVERSI ON" if data["inversion_active"] else "normal"
                print(f"[{now.strftime('%H:%M:%S')}] {zone_name} | "
                      f"PM2.5={data['pm25']:6.1f} AQI={data['aqi']:6.1f} | {inv_status}")

                # Publish anomaly event kalau AQI tinggi (Skenario S6)
                severity = get_severity(data["aqi"])
                if severity in ("high", "critical"):
                    anomaly = {
                        "zone_id":    zone_id,
                        "alert_type": "pm25_spike",
                        "severity":   severity,
                        "aqi":        data["aqi"],
                        "pm25":       data["pm25"],
                        "message":    (
                            f"PM2.5={data['pm25']} ug/m3, AQI={data['aqi']}. "
                            f"Lapisan inversi aktif - hindari aktivitas luar ruangan."
                        ),
                        "recorded_at": data["recorded_at"],
                    }
                    client.publish(
                        f"smartcity/environment/{zone_id}/anomaly",
                        json.dumps(anomaly),
                        qos=2,
                    )
                    print(f"  >> ANOMALY [{severity.upper()}] dikirim ke broker")

            print()
            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\nSimulator dihentikan.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()