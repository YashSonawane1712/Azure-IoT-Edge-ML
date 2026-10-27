"""Console-only sensor stream; run after training to see repeated local predictions."""
import time
from src.predictor import load_model, predict_risk
from src.simulator import SensorSimulator

model, _ = load_model()
sensor = SensorSimulator()
print("Streaming simulated sensor data. Press Ctrl+C to stop.\n")
try:
    while True:
        row = sensor.read()
        out = predict_risk(model, row)
        print(f'PM2.5={row["pm25"]:6.1f} | PM10={row["pm10"]:6.1f} | CO2={row["co2"]:6.0f} | '
              f'VOC={row["voc"]:6.1f} -> {out["label"]:8s} ({out["probability"]:.0%})')
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopped.")
