import json
import time
import paho.mqtt.client as mqtt

# Konfigurasi Wokwi (Sumber Data)
WOKWI_BROKER = "broker.hivemq.com"
WOKWI_PORT = 1883
WOKWI_TOPIC_ENV = "smartcity/environment/+/sensor"
WOKWI_TOPIC_HR = "wearable/+/heartrate"

import os

# Konfigurasi Lokal (Tujuan Data)
LOCAL_BROKER = os.environ.get("MQTT_HOST", "mosquitto")
LOCAL_PORT = int(os.environ.get("MQTT_PORT", 1883))

# Threshold
AQI_DANGER = 200

# paho-mqtt v2.0+ requires CallbackAPIVersion
try:
    from paho.mqtt.enums import CallbackAPIVersion
    client_wokwi = mqtt.Client(CallbackAPIVersion.VERSION1, "Bridge-Wokwi-Subscriber")
    client_local  = mqtt.Client(CallbackAPIVersion.VERSION1, "Bridge-Local-Publisher")
except ImportError:
    # paho-mqtt v1.x fallback
    client_wokwi = mqtt.Client("Bridge-Wokwi-Subscriber")
    client_local  = mqtt.Client("Bridge-Local-Publisher")


def on_wokwi_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[WOKWI] Berhasil konek ke {WOKWI_BROKER}. Menunggu data dari Wokwi...")
        client.subscribe(WOKWI_TOPIC_ENV)
        client.subscribe(WOKWI_TOPIC_HR)
    else:
        print(f"[WOKWI] Gagal konek, kode: {rc}")

def on_local_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[LOKAL] Berhasil konek ke Docker {LOCAL_BROKER}")
    else:
        print(f"[LOKAL] Gagal konek ke Docker, kode: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        topic = msg.topic
        
        # JIKA DATA SENSOR LINGKUNGAN
        if "smartcity/environment" in topic:
            zone_id = data.get("zone_id", 1)
            aqi = data.get("aqi", 0)
            
            print(f"\n[DATA MASUK] Wokwi Zone {zone_id} | AQI: {aqi}")

            local_sensor_topic = f"smartcity/environment/{zone_id}/sensor"
            client_local.publish(local_sensor_topic, payload)
            print(f" └─> Forwarded ke lokal: {local_sensor_topic}")

            if aqi > AQI_DANGER:
                anomaly_topic = f"smartcity/environment/{zone_id}/anomaly"
                anomaly_payload = {
                    "zone_id": zone_id,
                    "anomaly_type": "NOCTURNAL_INVERSION",
                    "severity": "CRITICAL" if aqi > 300 else "HIGH",
                    "trigger_value": aqi,
                    "description": f"Bahaya! AQI {aqi} terdeteksi. Warga dilarang beraktivitas di luar."
                }
                client_local.publish(anomaly_topic, json.dumps(anomaly_payload))
                print(f" └─> ⚠️ ALERT: Anomali dikirim ke {anomaly_topic}")
                
        # JIKA DATA DETAK JANTUNG (WEARABLE)
        elif "wearable" in topic:
            device_id = data.get("device_id", "unknown")
            hr = data.get("heart_rate", 0)
            
            print(f"\n[DATA JANTUNG] Wokwi Device {device_id} | HR: {hr} bpm")
            client_local.publish(topic, payload)
            print(f" └─> Forwarded ke lokal: {topic}")

    except Exception as e:
        print(f"Error parsing message: {e}")

def main():
    print("=======================================")
    print(" IoT Bridge: Wokwi (HiveMQ) -> Docker ")
    print("=======================================")
    
    # Setup Callbacks
    client_wokwi.on_connect = on_wokwi_connect
    client_wokwi.on_message = on_message
    client_local.on_connect = on_local_connect

    try:
        # Konek ke Docker Lokal dulu
        print(f"Menghubungkan ke Docker Lokal ({LOCAL_BROKER})...")
        client_local.connect(LOCAL_BROKER, LOCAL_PORT, 60)
        client_local.loop_start()

        # Konek ke Wokwi HiveMQ
        print(f"Menghubungkan ke Wokwi HiveMQ ({WOKWI_BROKER})...")
        client_wokwi.connect(WOKWI_BROKER, WOKWI_PORT, 60)
        
        # Blocking loop untuk dengerin Wokwi terus
        client_wokwi.loop_forever()

    except KeyboardInterrupt:
        print("\nMematikan bridge...")
        client_local.loop_stop()
        client_wokwi.disconnect()
        client_local.disconnect()
    except Exception as e:
        print(f"\nGagal jalan: {e}")
        print("PASTIKAN DOCKER SUDAH NYALA (docker compose up -d)")

if __name__ == "__main__":
    main()