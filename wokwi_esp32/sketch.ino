
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==================================================
// 1. WOKWI WI-FI SETTINGS
// ==================================================
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ==================================================
// 2. FASTAPI SERVER THROUGH NGROK
// Use the current HTTPS Forwarding URL from ngrok.
// Do not include Markdown brackets or parentheses.
// ==================================================
const char* SERVER_URL =
    "https://fetch-coconut-refute.ngrok-free.dev/telemetry";

// Must match IOT_SHARED_TOKEN in the FastAPI terminal.
const char* SHARED_TOKEN =
    "EdgeSenseDemo-2026-ChangeMe-9xQ4";

unsigned long sequenceNo = 0;
unsigned long lastReconnectAttempt = 0;

// ==================================================
// 3. CONNECT TO WOKWI WI-FI
// ==================================================
bool connectWiFi() {
  Serial.println();
  Serial.println("Connecting to Wokwi-GUEST...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    return true;
  }

  Serial.println("Wi-Fi connection failed.");
  Serial.println("Check the Wokwi simulation and try again.");
  return false;
}

// ==================================================
// 4. GENERATE SIMULATED SENSOR READINGS
// These are synthetic values, not physical measurements.
// ==================================================
void generateSensorReadings(
    float &temperature,
    float &humidity,
    float &pm25,
    float &pm10,
    float &co2,
    float &voc) {

  sequenceNo++;

  // Simulate occasional pollution episodes.
  bool pollutionEpisode =
      (sequenceNo % 18 >= 10 &&
       sequenceNo % 18 <= 14);

  temperature = random(1800, 3801) / 100.0;
  humidity = random(2500, 8501) / 100.0;
  pm25 = random(800, 4501) / 100.0;

  if (pollutionEpisode) {
    pm25 += random(3500, 10001) / 100.0;
  }

  pm10 = pm25 * (random(120, 201) / 100.0);

  co2 = random(42000, 90001) / 100.0;

  if (pollutionEpisode) {
    co2 += random(30000, 70001) / 100.0;
  }

  voc = random(4000, 18001) / 100.0;

  if (pollutionEpisode) {
    voc += random(10000, 35001) / 100.0;
  }

  Serial.println("----------------------------------");
  Serial.printf("Sequence: %lu\n", sequenceNo);
  Serial.printf("Temperature: %.1f C\n", temperature);
  Serial.printf("Humidity: %.1f %%\n", humidity);
  Serial.printf("PM2.5: %.1f\n", pm25);
  Serial.printf("PM10: %.1f\n", pm10);
  Serial.printf("CO2: %.0f\n", co2);
  Serial.printf("VOC: %.1f\n", voc);
}

// ==================================================
// 5. SEND TELEMETRY TO FASTAPI THROUGH HTTPS
// ==================================================
void sendTelemetry(
    float temperature,
    float humidity,
    float pm25,
    float pm10,
    float co2,
    float voc) {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Skipping POST: Wi-Fi is disconnected.");
    return;
  }

  WiFiClientSecure client;

  // DEMO ONLY: disables TLS certificate verification.
  // Do not use this setting in production.
  client.setInsecure();

  HTTPClient https;
  https.setConnectTimeout(15000);
  https.setTimeout(15000);

  Serial.print("Connecting to server: ");
  Serial.println(SERVER_URL);

  if (!https.begin(client, SERVER_URL)) {
    Serial.println("HTTPS setup failed.");
    return;
  }

  https.addHeader("Content-Type", "application/json");
  https.addHeader("X-IOT-Token", SHARED_TOKEN);

  StaticJsonDocument<384> doc;

  doc["device_id"] = "wokwi-esp32";
  doc["sequence"] = sequenceNo;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["co2"] = co2;
  doc["voc"] = voc;

  String requestBody;
  serializeJson(doc, requestBody);

  Serial.println("Sending telemetry...");

  int httpStatus = https.POST(requestBody);

  Serial.print("HTTP POST status: ");
  Serial.println(httpStatus);

  if (httpStatus > 0) {
    String response = https.getString();

    Serial.println("Server response:");
    Serial.println(response);

    if (httpStatus == 200 || httpStatus == 201) {
      Serial.println("Telemetry accepted successfully!");
    } else {
      Serial.println("Server returned an HTTP error.");
    }
  } else {
    Serial.print("HTTPS request failed: ");
    Serial.println(https.errorToString(httpStatus));
    Serial.println(
        "Check ngrok, the FastAPI server, and the URL."
    );
  }

  https.end();
}

// ==================================================
// 6. SETUP
// ==================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  randomSeed(micros());

  Serial.println();
  Serial.println("==================================");
  Serial.println(" EdgeSense AI");
  Serial.println(" ESP32 Telemetry Demo");
  Serial.println("==================================");

  connectWiFi();
}

// ==================================================
// 7. MAIN LOOP
// ==================================================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected.");

    // Avoid repeatedly reconnecting without a pause.
    if (millis() - lastReconnectAttempt >= 5000 ||
        lastReconnectAttempt == 0) {
      lastReconnectAttempt = millis();
      connectWiFi();
    }

    delay(1000);
    return;
  }

  float temperature;
  float humidity;
  float pm25;
  float pm10;
  float co2;
  float voc;

  generateSensorReadings(
      temperature, humidity, pm25, pm10, co2, voc
  );

  sendTelemetry(
      temperature, humidity, pm25, pm10, co2, voc
  );

  delay(5000);
}
