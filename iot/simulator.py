#!/usr/bin/env python3
"""
Smart City IoT Simulator
Theme  : The Nocturnal Poison Trap (Thermal Inversion Phenomenon)
Author : Anggota 3 - IoT Layer

Usage:
  python simulator.py                  # Normal mode, publish every 30s
  python simulator.py --interval 5     # Faster interval
  python simulator.py --anomaly        # Force anomaly (demo S6)
  python simulator.py --host 103.147.92.134 --port 1883

Topics published:
  smartcity/env/zone/{zone_id}         -> env_sensor_readings
  smartcity/traffic/road/{road_id}     -> traffic_readings
"""

import json
import time
import random
import argparse
from datetime import datetime
import paho.mqtt.client as mqtt

# ─── Default Config ────────────────────────────────────────────
MQTT_HOST = "localhost"
MQTT_PORT = 1883
INTERVAL  = 30   # seconds

# ─── Master Data (sesuai seed.sql) ─────────────────────────────
ZONES = [
    {"id": 1, "name": "Beji"},
    {"id": 2, "name": "Lenteng Agung"},
    {"id": 3, "name": "Pasar Minggu"},
    {"id": 4, "name": "Jagakarsa"},
    {"id": 5, "name": "Pancoran Mas"},
]

ROADS = [
    {"id": 1, "name": "Jl. Margonda Raya",        "zone_id": 1},
    {"id": 2, "name": "Jl. Raya Lenteng Agung",   "zone_id": 2},
    {"id": 3, "name": "Jl. Raya Pasar Minggu",    "zone_id": 3},
    {"id": 4, "name": "Jl. Raya Bogor",            "zone_id": 5},
    {"id": 5, "name": "Jl. Kahfi 1",               "zone_id": 4},
    {"id": 6, "name": "Jl. UI Depok Internal",     "zone_id": 1},
]

# Zones 1-3 lebih dekat Jakarta → polusi lebih tinggi
ZONE_POLLUTION_MULTIPLIER = {1: 1.20, 2: 1.30, 3: 1.25, 4: 0.90, 5: 1.10}


# ─── Nocturnal Pattern Logic ────────────────────────────────────
def get_nocturnal_factor(hour: int) -> float:
    """
    Thermal inversion: lapisan inversi turun malam-subuh.
    Polutan terperangkap → AQI spike jam 03:00-05:00.

    Returns 0.0–1.0 (1.0 = kondisi paling parah).
    """
    if 3 <= hour < 6:
        return 1.0      # Puncak nocturnal trap (seed data AQI 358 jam 04:00)
    elif 22 <= hour or hour < 3:
        return 0.75     # Membangun
    elif 6 <= hour < 9:
        return 0.35     # Dispersal pagi (suhu naik, angin kencang)
    else:
        return 0.12     # Siang normal


# ─── Data Generators ────────────────────────────────────────────
def generate_env_data(zone_id: int, hour: int, anomaly: bool = False) -> dict:
    """
    Generate env sensor reading sesuai pola inversi termal.
    Anomaly mode: nilai ekstrem untuk trigger S6 demo.
    """
    now = datetime.now().isoformat()

    if anomaly:
        # Ekstrem: AQI 350-400, PM2.5 280-350 (melebihi threshold ML)
        pm25 = round(random.uniform(280, 350), 2)
        return {
            "zone_id":     zone_id,
            "pm25":        pm25,
            "pm10":        round(pm25 * 1.20, 2),
            "no2":         round(random.uniform(0.130, 0.180), 3),
            "co":          round(random.uniform(2.50, 3.20), 3),
            "o3":          round(random.uniform(0.010, 0.050), 3),
            "temperature": round(random.uniform(20.5, 22.5), 2),
            "humidity":    round(random.uniform(97.0, 99.9), 2),
            "wind_speed":  round(random.uniform(0.05, 0.15), 2),
            "aqi":         round(pm25 * 1.30 + random.uniform(0, 10), 2),
            "recorded_at": now,
        }

    factor = get_nocturnal_factor(hour)
    is_night = factor >= 0.70
    mult = ZONE_POLLUTION_MULTIPLIER.get(zone_id, 1.0)

    if is_night:
        # Inversi aktif: suhu rendah, lembab, angin nyaris nol
        temp       = round(random.uniform(20.5, 23.0), 2)
        humidity   = round(random.uniform(93.0, 99.5), 2)
        wind_speed = round(random.uniform(0.05, 0.80), 2)
        pm25_base  = random.uniform(100, 220) * factor * mult
    else:
        # Siang: suhu tinggi, angin menyebarkan polutan
        temp       = round(random.uniform(28.0, 34.0), 2)
        humidity   = round(random.uniform(50.0, 68.0), 2)
        wind_speed = round(random.uniform(2.50, 4.50), 2)
        pm25_base  = random.uniform(25, 80) * mult

    pm25 = round(pm25_base, 2)
    pm10 = round(pm25 * 1.20, 2)
    aqi  = round(pm25 * 1.30 + random.uniform(-5, 15), 2)

    return {
        "zone_id":     zone_id,
        "pm25":        pm25,
        "pm10":        pm10,
        "no2":         round(random.uniform(0.030, 0.115) * (1.5 if is_night else 1.0), 3),
        "co":          round(random.uniform(0.50, 2.10), 3),
        "o3":          round(random.uniform(0.010, 0.050), 3),
        "temperature": temp,
        "humidity":    humidity,
        "wind_speed":  wind_speed,
        "aqi":         aqi,
        "recorded_at": now,
    }


def generate_traffic_data(road_id: int, zone_id: int, hour: int) -> dict:
    """
    Generate traffic reading sesuai pola jam sibuk Depok-Jakarta.
    Rush hour pagi 06-09, sore 17-19.
    """
    now = datetime.now().isoformat()

    is_rush  = (6 <= hour < 9) or (17 <= hour < 20)
    is_night = hour < 5 or hour >= 22

    if is_rush:
        density  = round(random.uniform(75, 95), 2)
        speed    = round(random.uniform(10, 22), 2)
        vehicles = random.randint(700, 1150)
        incident = random.random() < 0.15   # 15% chance
    elif is_night:
        density  = round(random.uniform(12, 35), 2)
        speed    = round(random.uniform(55, 78), 2)
        vehicles = random.randint(25, 140)
        incident = random.random() < 0.03
    else:
        density  = round(random.uniform(15, 35), 2)
        speed    = round(random.uniform(55, 78), 2)
        vehicles = random.randint(25, 140)
        incident = random.random() < 0.03

    return {
        "road_id":          road_id,
        "zone_id":          zone_id,
        "vehicle_density":  density,
        "avg_speed_kmh":    speed,
        "total_vehicles":   vehicles,
        "incident_flag":    incident,
        "recorded_at":      now,
    }


# ─── MQTT Callbacks ─────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    codes = {0: "OK", 1: "Wrong protocol", 2: "Bad client ID",
             3: "Server unavailable", 4: "Bad credentials", 5: "Not authorized"}
    if rc == 0:
        print(f"[MQTT] ✅ Connected to {userdata['host']}:{userdata['port']}")
    else:
        print(f"[MQTT] ❌ Connection failed: {codes.get(rc, rc)}")


# ─── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Smart City IoT Simulator — Nocturnal Poison Trap"
    )
    parser.add_argument("--host",     default=MQTT_HOST, help="MQTT broker host")
    parser.add_argument("--port",     type=int, default=MQTT_PORT)
    parser.add_argument("--interval", type=int, default=INTERVAL, help="Seconds between publishes")
    parser.add_argument("--anomaly",  action="store_true", help="Force anomaly mode (demo S6)")
    args = parser.parse_args()

    client = mqtt.Client(
        client_id="smartcity-nocturnal-simulator",
        userdata={"host": args.host, "port": args.port}
    )
    client.on_connect = on_connect

    print("=" * 60)
    print("  🌆 Smart City IoT Simulator")
    print("  🌫  Theme: The Nocturnal Poison Trap")
    print("=" * 60)
    if args.anomaly:
        print("  ⚠️  ANOMALY MODE — Extreme values for S6 demo")
    print(f"  Host: {args.host}:{args.port} | Interval: {args.interval}s")
    print(f"  Zones: {len(ZONES)} | Roads: {len(ROADS)}")
    print("=" * 60)

    try:
        client.connect(args.host, args.port, keepalive=60)
        client.loop_start()
        time.sleep(1)  # wait for connection

        cycle = 0
        while True:
            cycle += 1
            hour   = datetime.now().hour
            factor = get_nocturnal_factor(hour)

            if args.anomaly:
                mode = "⚠️  ANOMALY"
            elif factor >= 0.70:
                mode = "🌙 NOCTURNAL TRAP"
            elif factor >= 0.35:
                mode = "🌅 DISPERSAL"
            else:
                mode = "☀️  NORMAL"

            print(f"\n[Cycle {cycle}] {datetime.now().strftime('%H:%M:%S')} | {mode}")
            print("─" * 60)

            # ── Publish ENV data ──────────────────────────────────
            for zone in ZONES:
                data    = generate_env_data(zone["id"], hour, args.anomaly)
                topic   = f"smartcity/env/zone/{zone['id']}"
                payload = json.dumps(data)
                result  = client.publish(topic, payload, qos=1)

                flag = "⚠️" if data["aqi"] > 200 else "✅"
                print(f"  {flag} [ENV] Zone {zone['id']} {zone['name']:<20} "
                      f"AQI={data['aqi']:6.1f} | PM2.5={data['pm25']:6.1f} | "
                      f"Wind={data['wind_speed']:4.2f}m/s | Hum={data['humidity']:5.1f}%")

            # ── Publish TRAFFIC data ──────────────────────────────
            for road in ROADS:
                data    = generate_traffic_data(road["id"], road["zone_id"], hour)
                topic   = f"smartcity/traffic/road/{road['id']}"
                payload = json.dumps(data)
                client.publish(topic, payload, qos=1)

                inc = "🚨" if data["incident_flag"] else "  "
                print(f"  {inc} [TRF] Road {road['id']} {road['name']:<30} "
                      f"Density={data['vehicle_density']:5.1f} | "
                      f"Speed={data['avg_speed_kmh']:5.1f}km/h | "
                      f"Vehicles={data['total_vehicles']}")

            print(f"\n  ⏱  Next publish in {args.interval}s... (Ctrl+C to stop)")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n[SIMULATOR] Stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[SIMULATOR] Disconnected.")


if __name__ == "__main__":
    main()