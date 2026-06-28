#include <WiFi.h>
#include <PubSubClient.h>

// ── Konfigurasi ─────────────────────────────────────────
const char* ssid     = "Wokwi-GUEST";
const char* password = "";

#define POT_HR_PIN  34  // Potensiometer → simulasi Heart Rate
#define BTN_ZONE1   18  // Tombol → Zone 1: Margonda
#define BTN_ZONE2   19  // Tombol → Zone 2: Lenteng Agung
#define BTN_ZONE3   21  // Tombol → Zone 3: Pasar Minggu
#define LED_MERAH   25  // LED merah = HR tinggi (running)
#define LED_HIJAU   26  // LED hijau = HR normal (rest/walking)

const int   CITIZEN_ID = 3;
const char* DEVICE_ID  = "device_01";

WiFiClient espClient;
PubSubClient mqtt(espClient);

int    currentZone = 1;
String zoneName    = "Margonda";

void setup() {
    Serial.begin(115200);
    delay(300);

    pinMode(BTN_ZONE1, INPUT_PULLUP);
    pinMode(BTN_ZONE2, INPUT_PULLUP);
    pinMode(BTN_ZONE3, INPUT_PULLUP);
    pinMode(LED_MERAH, OUTPUT);
    pinMode(LED_HIJAU, OUTPUT);

    Serial.println("====================================");
    Serial.println("  Device 2: Smartwatch Warga");
    Serial.println("  Simulasi Heart Rate & Lokasi");
    Serial.println("====================================");
    Serial.println("  BTN1 = Zone 1 (Margonda)");
    Serial.println("  BTN2 = Zone 2 (Lenteng Agung)");
    Serial.println("  BTN3 = Zone 3 (Pasar Minggu)");
    Serial.println("====================================\n");

    WiFi.begin(ssid, password);
    Serial.print("WiFi: Connecting");
    int t = 0;
    while (WiFi.status() != WL_CONNECTED && t < 20) {
        delay(300);
        Serial.print(".");
        t++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? " OK!" : " Timeout");

    mqtt.setServer("broker.hivemq.com", 1883);
}

void loop() {
    // Deteksi tombol zona (INPUT_PULLUP: LOW saat ditekan)
    if (digitalRead(BTN_ZONE1) == LOW) {
        currentZone = 1; zoneName = "Margonda";
        Serial.println("[LOKASI] Pindah ke Zone 1: Margonda");
        delay(300);
    }
    if (digitalRead(BTN_ZONE2) == LOW) {
        currentZone = 2; zoneName = "Lenteng Agung";
        Serial.println("[LOKASI] Pindah ke Zone 2: Lenteng Agung");
        delay(300);
    }
    if (digitalRead(BTN_ZONE3) == LOW) {
        currentZone = 3; zoneName = "Pasar Minggu";
        Serial.println("[LOKASI] Pindah ke Zone 3: Pasar Minggu");
        delay(300);
    }

    // Baca potensiometer → Heart Rate (60 - 170 bpm)
    int potValue  = analogRead(POT_HR_PIN);
    int heartRate = map(potValue, 0, 4095, 60, 170);

    // Tentukan aktivitas berdasarkan HR
    String activity;
    if (heartRate < 90) {
        activity = "rest";
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(LED_HIJAU, HIGH);
    } else if (heartRate <= 130) {
        activity = "walking";
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(LED_HIJAU, HIGH);
    } else {
        activity = "running";
        digitalWrite(LED_MERAH, HIGH);
        digitalWrite(LED_HIJAU, LOW);
    }

    Serial.printf("[WEARABLE] Zone %d (%s) | HR: %d bpm | Status: %s\n",
        currentZone, zoneName.c_str(), heartRate, activity.c_str());

    // Kirim ke MQTT
    if (!mqtt.connected()) {
        mqtt.connect("ESP32-Wearable-Citizen3");
    }
    mqtt.loop();

    String topic   = "wearable/" + String(DEVICE_ID) + "/heartrate";
    String payload = "{\"citizen_id\":"  + String(CITIZEN_ID) +
                     ",\"device_id\":\"" + String(DEVICE_ID) + "\"" +
                     ",\"heart_rate\":"  + String(heartRate) +
                     ",\"zone_id\":"     + String(currentZone) + "}";
    mqtt.publish(topic.c_str(), payload.c_str());

    delay(3000);
}
