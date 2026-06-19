#include <WiFi.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

const char* ssid     = "Wokwi-GUEST";
const char* password = "";
const int   ZONE_ID  = 1;

#define DHT_PIN  4
#define DHT_TYPE DHT22
#define LED_MERAH  25
#define LED_HIJAU  26

DHT dht(DHT_PIN, DHT_TYPE);

float hitungAQI(int jam) {
    if (jam >= 22 || jam <= 5)       return random(180, 320);
    else if (jam >= 6 && jam <= 8)   return random(90, 150);
    else                             return random(30, 80);
}

WiFiClient espClient;
PubSubClient mqtt(espClient);


void setup() {
    Serial.begin(115200);
    delay(300);

    pinMode(LED_MERAH, OUTPUT);
    pinMode(LED_HIJAU, OUTPUT);
    dht.begin();

    Serial.println("====================================");
    Serial.println("  Smart City - Nocturnal Poison Trap");
    Serial.println("  Kelompok 5 | Zone: Beji, Depok");
    Serial.println("====================================");

    Serial.print("WiFi: Connecting");
    WiFi.begin(ssid, password);
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
    if (isnan(suhu))     suhu     = 22.5;
    if (isnan(kelembab)) kelembab = 72.0;

    int   jam  = (millis() / 60000) % 24;
    float aqi  = hitungAQI(jam);
    float pm25 = aqi * 0.72;

    if (aqi > 200) {
        digitalWrite(LED_MERAH, HIGH);
        digitalWrite(LED_HIJAU, LOW);
        Serial.print("[BAHAYA] ");
    } else {
        digitalWrite(LED_MERAH, LOW);
        digitalWrite(LED_HIJAU, HIGH);
        Serial.print("[AMAN]   ");
    }

    Serial.printf("Jam %02d | PM2.5=%.1f ug/m3 | AQI=%.0f | Suhu=%.1fC | RH=%.0f%%\n",
        jam, pm25, aqi, suhu, kelembab);

    // Kirim ke MQTT
    if (!mqtt.connected()) {
        mqtt.connect("ESP32-Kelompok5");
    }
    mqtt.loop();

    String topic   = "smartcity/environment/" + String(ZONE_ID) + "/sensor";
    String payload = "{\"zone_id\":"     + String(ZONE_ID)  +
                     ",\"pm25\":"        + String(pm25)     +
                     ",\"aqi\":"         + String(aqi)      +
                     ",\"temperature\":" + String(suhu)     +
                     ",\"humidity\":"    + String(kelembab)  +
                     ",\"wind_speed\":0.5}";
    mqtt.publish(topic.c_str(), payload.c_str());

    delay(3000);
}

