import json, os, csv
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "data" / "latest_wokwi.json"
CSV_LOG = ROOT / "data" / "wokwi_telemetry.csv"
TOKEN = os.getenv("IOT_SHARED_TOKEN", "change-this-demo-token")

app = FastAPI(title="EdgeSense IoT Telemetry Receiver", version="1.0.0")

class Telemetry(BaseModel):
    temperature: float = Field(ge=-40, le=100)
    humidity: float = Field(ge=0, le=100)
    pm25: float = Field(ge=0, le=2000)
    pm10: float = Field(ge=0, le=3000)
    co2: float = Field(ge=0, le=10000)
    voc: float = Field(ge=0, le=10000)
    device_id: str = "wokwi-esp32"
    sequence: int = 0

@app.get("/")
def root():
    return {"service": "EdgeSense IoT receiver", "status": "ok", "post_to": "/telemetry"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/telemetry")
def telemetry(payload: Telemetry, x_iot_token: str = Header(default="")):
    if x_iot_token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid X-IOT-Token")
    record = payload.model_dump()
    record["received_at"] = datetime.now(timezone.utc).isoformat()
    LATEST.parent.mkdir(parents=True, exist_ok=True)
    LATEST.write_text(json.dumps(record, indent=2), encoding="utf-8")
    # Append every accepted Wokwi message to a CSV for project data collection.
    CSV_LOG.parent.mkdir(parents=True, exist_ok=True)
    fields = ["received_at", "device_id", "sequence", "temperature", "humidity", "pm25", "pm10", "co2", "voc"]
    write_header = not CSV_LOG.exists() or CSV_LOG.stat().st_size == 0
    with CSV_LOG.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow({key: record.get(key) for key in fields})
    return {"accepted": True, "device_id": record["device_id"], "sequence": record["sequence"]}
