from pathlib import Path
import json
import joblib

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "artifacts" / "air_quality_risk_model.joblib"
META_PATH = ROOT / "artifacts" / "metadata.json"

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model missing. Run: python -m src.train_model")
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}
    return model, metadata

def predict_risk(model, reading):
    features = ["temperature", "humidity", "pm25", "pm10", "co2", "voc"]
    row = [[float(reading[name]) for name in features]]
    label = str(model.predict(row)[0])
    probability = 1.0
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(row)[0]
        classes = list(model.classes_)
        probability = float(probs[classes.index(label)])
    advice = {
        "Low":"Conditions look relatively low-risk in this simulated reading. Continue monitoring.",
        "Moderate":"Consider improving ventilation and checking the sensor trend.",
        "High":"High simulated pollution risk. Check ventilation and investigate possible pollution sources."
    }.get(label, "Continue monitoring the sensor readings.")
    return {"label": label, "probability": probability, "advice": advice}
