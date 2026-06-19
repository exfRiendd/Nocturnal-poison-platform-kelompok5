import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime, timezone, timedelta

# Konfigurasi dari tim IoT
BROKER_HOST = "localhost"
BROKER_PORT = 1883
DEVICE_ID = "wearable-001"
ZONE_ID = 1
TOPIC = f"wearable/{DEVICE_ID}/heartrate"
wib = timezone(timedelta(hours=7))

client = mqtt.Client(client_id=f"sim_{DEVICE_ID}")
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

print("⌚ Memulai Simulasi Smartwatch (Otomatis)")
print("Skenario: Istirahat -> Jalan -> Lari -> Istirahat")

# Skenario sesuai kontrak: (Nama, Min HR, Max HR, Jumlah Kirim)
scenario_phases = [
    ("REST", 70, 85, 3),      # < 90
    ("WALKING", 95, 120, 3),  # 90 - 129
    ("RUNNING", 135, 145, 3), # >= 130
    ("REST", 70, 85, 3)       # < 90 (Stop Sesi)
]

try:
    while True:
        for phase_name, min_hr, max_hr, ticks in scenario_phases:
            print(f"\n---> Fase: {phase_name} <---")
            for _ in range(ticks):
                hr = random.randint(min_hr, max_hr)
                payload = {
                    "device_id": DEVICE_ID,
                    "zone_id": ZONE_ID,
                    "heart_rate": hr,
                    "recorded_at": datetime.now(wib).replace(microsecond=0).isoformat()
                }
                client.publish(TOPIC, json.dumps(payload))

                icon = "🚶" if phase_name == "WALKING" else "🏃" if phase_name == "RUNNING" else "🧘"
                print(f"{icon} HR: {hr} bpm | Topic: {TOPIC}")
                time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()