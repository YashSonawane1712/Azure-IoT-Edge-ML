# Wokwi ESP32 → EdgeSense AI

This folder contains firmware for a virtual ESP32. The sketch generates simulated environmental readings, sends them to the Python telemetry receiver over HTTPS, and prints the HTTP response in the Wokwi Serial Monitor.

## Use Wokwi in the browser
1. Open https://wokwi.com/projects/new/esp32
2. Replace the default `sketch.ino` with this folder's `sketch.ino`.
3. Open `diagram.json` in the Wokwi project and replace its content with this folder's `diagram.json` if needed.
4. Add `ArduinoJson` in the Wokwi project libraries panel (or create `libraries.txt` containing `ArduinoJson`).
5. Follow the root README's “Wokwi end-to-end integration” steps to start the local receiver and ngrok tunnel.
6. Replace `SERVER_URL` with your ngrok HTTPS URL plus `/telemetry`.
7. Set `SHARED_TOKEN` to the same value as `IOT_SHARED_TOKEN` in the Python receiver terminal.
8. Start simulation; inspect Serial Monitor for `HTTP POST status: 200`.

The Wokwi public gateway supports outgoing internet requests but cannot directly reach a service running only on your laptop. A public HTTPS tunnel such as ngrok is used for this demo. Wokwi's private gateway can access `host.wokwi.internal` but requires the applicable Wokwi plan. Never use this demo's `setInsecure()` TLS setting for production.
