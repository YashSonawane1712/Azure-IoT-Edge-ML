# EdgeSense AI — Real-Time ML with Azure ML & IoT Edge

**AIEC Mini Project | Environment monitoring using simulated IoT sensors**

## What it does
- Generates simulated temperature, humidity, PM2.5, PM10, CO₂ and VOC readings.
- Creates a reproducible synthetic dataset and trains a Random Forest classifier.
- Evaluates it on a held-out test set and saves the model + metadata.
- Runs predictions locally (edge-style) and shows a live Streamlit dashboard.
- Packages the dashboard and model workflow in Docker.
- Includes an optional Azure ML SDK v2 script to register/version the model in a real Azure ML workspace.

> **Honest limitation:** no physical sensor is connected. The dataset and labels are synthetic and intended to demonstrate the pipeline. This is not an official AQI calculation or a validated health/safety device. Accuracy printed by training is agreement with the synthetic labelling rule, not real-world performance.

## Architecture
```text
Simulated IoT sensors (Python)
          |
          v
Telemetry: temperature, humidity, PM2.5, PM10, CO2, VOC
          |
          v
Local ML inference (scikit-learn Random Forest)
          |
          +----> Risk label + confidence + advice
          |
          v
Streamlit dashboard / charts / history

Training artifact --optional--> Azure ML model registry
Dashboard + Python runtime --Docker--> localhost:8501
```

## Option A — Run in VS Code on Windows (recommended first)

### 1. Install prerequisites
- Python 3.11 (recommended)
- VS Code and the Python extension
- Optional for container deployment: Docker Desktop, started and running

Open the extracted project folder in VS Code: **File → Open Folder**.

### 2. Create a virtual environment
Open VS Code Terminal → PowerShell, then run these commands from the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Train and evaluate the model
```powershell
python -m src.train_model
```
Expected outputs:
- `data/synthetic_sensor_data.csv`
- `artifacts/air_quality_risk_model.joblib`
- `artifacts/metadata.json`
- `artifacts/evaluation.json`

The command prints held-out test accuracy and a classification report. Exact metrics may vary by dependency/platform version.

### 4. Run a terminal sensor simulation
In the same terminal:
```powershell
python simulate_stream.py
```
You should see changing sensor readings and predicted risk labels. Stop with **Ctrl+C**.

### 5. Launch the dashboard
Stop the terminal simulator with Ctrl+C, then run:
```powershell
streamlit run app.py
```
Open the local URL printed by Streamlit, usually `http://localhost:8501`. The dashboard produces one reading per refresh; enable Auto-refresh in the sidebar for a continuous stream. To stop, press Ctrl+C.

## Option B — Docker deployment

Install Docker Desktop, start it, and verify:
```powershell
docker --version
docker compose version
docker info
```
From the project root:
```powershell
docker compose up --build
```
Open `http://localhost:8501`. Docker trains the model during image build, then starts the dashboard. Stop with **Ctrl+C**. To run in the background:
```powershell
docker compose up --build -d
docker compose logs -f
docker compose down
```
If port 8501 is occupied, edit `compose.yaml` to `"8502:8501"` and open `http://localhost:8502`.

## Azure ML model management (optional; requires Azure account/workspace)
The project runs locally without Azure. To register a versioned model in Azure ML:
1. Create an Azure ML workspace in Azure Portal.
2. Install Azure CLI, sign in with `az login`, and ensure your user has access to the workspace.
3. In the active virtual environment run `pip install -r requirements-azure.txt`.
4. Follow `azure_ml/README.md` to set the three workspace environment variables.
5. Run `python -m src.train_model` then `python azure_ml/register_model.py`.
6. In Azure ML Studio, open **Models** and verify `edgesense-air-quality-risk` and its version.

This script registers the artifact; it does not provision an Azure workspace or deploy a managed online endpoint. A real Azure workspace, permissions, and potentially paid Azure resources are required.

## Sensor / IoT simulation options
1. **Python simulator (included):** quickest, no extra hardware/software, suitable for tomorrow's submission.
2. **Wokwi:** browser-based ESP32/Arduino simulator. Useful if you want a virtual microcontroller to publish mock sensor readings; requires extra integration code.
3. **Node-RED:** visual flow-based IoT simulation and MQTT dashboards; useful for showing sensor messages.
4. **MQTT Mosquitto:** broker for a publish/subscribe demo; can connect a simulated Python sensor publisher to a subscriber.
5. **Azure IoT Edge:** more realistic edge deployment, but requires additional setup and compatible Linux/container environment. This submission's Docker container demonstrates local edge inference; it is not itself an Azure IoT Edge module.

For the deadline, use the included Python simulator + dashboard + Docker. Mention Wokwi/Node-RED as alternatives only if you actually demonstrate them.

## Suggested demo sequence (3–5 minutes)
1. Explain the problem: detect rising environmental pollution risk from incoming sensor telemetry.
2. Show `src/simulator.py` and `src/train_model.py`.
3. Run `python -m src.train_model` and show generated model/evaluation files.
4. Run `python simulate_stream.py` to show changing readings and predictions.
5. Open the Streamlit dashboard and explain the metrics/charts/history.
6. Show `Dockerfile` and run `docker compose up --build`.
7. If Azure is configured, show the registered model in Azure ML Studio. If not, clearly state Azure registration is an optional cloud step and demonstrate the local pipeline.

## Troubleshooting
- **`python` not found:** install Python 3.11 and tick “Add Python to PATH”; reopen VS Code.
- **Activation denied:** use the `Set-ExecutionPolicy -Scope Process ...` command above.
- **`ModuleNotFoundError`:** confirm `.venv` is activated and run `pip install -r requirements.txt`.
- **Model missing:** run `python -m src.train_model` from project root.
- **Docker command fails:** start Docker Desktop and wait until it says it is running.
- **Azure authentication failure:** run `az login`; verify subscription, workspace, resource group, and RBAC permissions.


## Wokwi end-to-end integration (ESP32 → Python ML → dashboard)

This adds a browser-simulated ESP32 which sends simulated sensor readings to your local Python receiver. The receiver saves the latest message; Streamlit reads it and runs the existing Random Forest model. For Wokwi's public gateway, your laptop receiver needs a temporary public HTTPS URL.

### A. Start the Python receiver
Open a **new VS Code terminal** in the project root, activate `.venv`, and run:

```powershell
$env:IOT_SHARED_TOKEN="change-this-demo-token"
uvicorn iot_receiver.server:app --host 0.0.0.0 --port 8000
```

Keep this terminal running. Test locally in another terminal:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```
Expected response: `status : ok`.

### B. Expose the receiver through HTTPS using ngrok
Install ngrok from https://ngrok.com/download and sign in / configure its auth token according to the official instructions. In a **second terminal**, run:

```powershell
ngrok http 8000
```

Copy the HTTPS forwarding address displayed, for example `https://example-name.ngrok-free.app` (your address will be different). Do not copy the example. Your endpoint will be:
`https://YOUR-ACTUAL-NGROK-HOST/telemetry`

The free ngrok account may require sign-in/auth-token setup. Keep the ngrok terminal running. Do not expose sensitive data. The demo token is only a basic classroom safeguard, not production-grade security.

### C. Create the Wokwi ESP32 project
1. Open https://wokwi.com/projects/new/esp32.
2. Replace `sketch.ino` with `wokwi_esp32/sketch.ino` from this project.
3. Replace the diagram content with `wokwi_esp32/diagram.json` if required.
4. Add `ArduinoJson` using Wokwi's Library Manager. If the project editor supports `libraries.txt`, use the included file.
5. In `sketch.ino`, change:
   `https://REPLACE-WITH-YOUR-NGROK-DOMAIN/telemetry`
   to your actual ngrok HTTPS URL ending in `/telemetry`.
6. Keep `SHARED_TOKEN` exactly the same as `IOT_SHARED_TOKEN` in the receiver terminal.
7. Start simulation and open the Serial Monitor. It should connect to `Wokwi-GUEST` and print `HTTP POST status: 200` when the message is accepted.

### D. Start the dashboard
In a **third terminal**, activate `.venv` and run:
```powershell
streamlit run app.py
```
Open http://localhost:8501. In the sidebar choose **Wokwi ESP32** and enable **Auto-refresh**. As Wokwi sends readings every three seconds, the dashboard will read the latest message and run local ML inference. The receiver writes the latest message to `data/latest_wokwi.json` and appends every accepted message to `data/wokwi_telemetry.csv` for data collection.

### E. Test the receiver without Wokwi (optional)
With the receiver running, use PowerShell:
```powershell
$headers = @{ "X-IOT-Token" = "change-this-demo-token" }
$body = @{
  device_id="manual-test"; sequence=1
  temperature=27.5; humidity=55
  pm25=75; pm10=120; co2=1100; voc=220
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/telemetry" -Method Post -Headers $headers -ContentType "application/json" -Body $body
```
The dashboard should then show the latest manual-test telemetry if the receiver has written the file.

### Run order for the demo
1. Train the model once: `python -m src.train_model`
2. Start receiver: `uvicorn iot_receiver.server:app --host 0.0.0.0 --port 8000`
3. Start tunnel: `ngrok http 8000`
4. Start Wokwi simulation (after editing the endpoint/token).
5. Start dashboard: `streamlit run app.py`, select Wokwi ESP32, turn on Auto-refresh.

Keep all four processes (receiver, ngrok, Wokwi, Streamlit) running during the demo. Docker deployment of the dashboard is a separate demo path; the host-file telemetry bridge described here is intended for local VS Code execution.
