// =========================================
// WOKWI DEVICE 2 (ZONE 2 - Lenteng Agung)
// =========================================
#include <WiFi.h>
#include <DHT.h>
#include <PubSubClient.h>

// ── Konfigurasi ─────────────────────────────────────────
const char* ssid     = "Wokwi-GUEST";
const char* password = "";

#define ZONE_ID    2   // Stasiun 2 (Lenteng Agung)
#define DHT_PIN    4
#define DHT_TYPE   DHT22
#define LED_MERAH  25
#define LED_HIJAU  26
#define POT_PIN    34  // Potensiometer → simulasi tingkat polusi

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient mqtt(espClient);

void setup() {
    Serial.begin(115200);
    delay(300);

    pinMode(LED_MERAH, OUTPUT);
    pinMode(LED_HIJAU, OUTPUT);
    dht.begin();

    Serial.println("====================================");
    Serial.println("  Device 2: Stasiun Udara Utara");
    Serial.println("  Zone 2 - Lenteng Agung");
    Serial.println("====================================");

    WiFi.begin(ssid, password);
    Serial.print("WiFi: Connecting");
    int t = 0;
    while (WiFi.status() != WL_CONNECTED && t < 20) {
        delay(300);
        Serial.print(".");
        t++;
    }
    Serial.println(WiFi.status() == WL_CONNECTED ? " OK!" : " Timeout");
    Serial.println("Mulai kirim data sensor...\n");

    mqtt.setServer("broker.hivemq.com", 1883);
}

void loop() {
    float suhu     = dht.readTemperature();
    float kelembab = dht.readHumidity();
    if (isnan(suhu))     suhu     = 28.0;
    if (isnan(kelembab)) kelembab = 72.0;

    int   potValue = analogRead(POT_PIN);
    float pm25     = map(potValue, 0, 4095, 0, 300);

    float pm10 = pm25 * 1.5;    
    float co   = pm25 * 0.02;   
    float no2  = pm25 * 0.6;    
    float aqi  = pm25 / 0.72;   

    if (pm25 > 150) {
        digitalWrite(LED_MERAH, HIGH);
        digitalWrite(LED_HIJAU, LOW);
        Serial.print("[BAHAYA] ");
    } else {
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(LED_HIJAU, HIGH);
        Serial.print("[AMAN]   ");
    }

    Serial.printf("PM2.5=%.1f | AQI=%.0f | PM10=%.1f | CO=%.2f | NO2=%.1f | Suhu=%.1fC | RH=%.0f%%\n",
        pm25, aqi, pm10, co, no2, suhu, kelembab);

    if (!mqtt.connected()) {
        mqtt.connect("ESP32-AirStation-Zone2"); // MQTT Client ID harus unik
    }
    mqtt.loop();

    String topic   = "smartcity/environment/" + String(ZONE_ID) + "/sensor";
    String payload = "{\"zone_id\":"      + String(ZONE_ID)      +
                     ",\"pm25\":"         + String(pm25, 2)       +
                     ",\"pm10\":"         + String(pm10, 2)       +
                     ",\"co\":"           + String(co, 3)         +
                     ",\"no2\":"          + String(no2, 2)        +
                     ",\"aqi\":"          + String(aqi, 2)        +
                     ",\"temperature\":"  + String(suhu, 2)       +
                     ",\"humidity\":"     + String(kelembab, 2)   +
                     ",\"wind_speed\":2.5}";
    mqtt.publish(topic.c_str(), payload.c_str());

    delay(5000);
}
