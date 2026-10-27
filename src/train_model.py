from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "data"
FEATURES = ["temperature", "humidity", "pm25", "pm10", "co2", "voc"]

def make_dataset(n=5000, seed=21):
    rng = np.random.default_rng(seed)
    temperature = rng.uniform(10, 42, n)
    humidity = rng.uniform(15, 95, n)
    pm25 = rng.gamma(2.2, 18, n).clip(1, 220)
    pm10 = (pm25 * rng.uniform(1.15, 2.3, n)).clip(2, 400)
    co2 = rng.normal(650, 260, n).clip(350, 2200)
    voc = rng.gamma(2.5, 55, n).clip(5, 900)
    # Transparent synthetic labels for a classroom demonstration, not official AQI.
    score = (pm25 * 0.55) + (pm10 * 0.12) + (co2 - 400) * 0.025 + voc * 0.06
    labels = np.where(score < 55, "Low", np.where(score < 105, "Moderate", "High"))
    return pd.DataFrame({"temperature":temperature, "humidity":humidity, "pm25":pm25,
                         "pm10":pm10, "co2":co2, "voc":voc, "risk_label":labels})

def main():
    ARTIFACTS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    df = make_dataset()
    csv_path = DATA / "synthetic_sensor_data.csv"
    df.to_csv(csv_path, index=False)
    X, y = df[FEATURES], df["risk_label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = Pipeline([("scale", StandardScaler()),
                      ("classifier", RandomForestClassifier(n_estimators=180, max_depth=14,
                                                           class_weight="balanced", random_state=42, n_jobs=-1))])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    joblib.dump(model, ARTIFACTS / "air_quality_risk_model.joblib")
    metadata = {
        "model_name":"edgesense-air-quality-risk",
        "version":"1.0.0",
        "features":FEATURES,
        "classes":[str(x) for x in model.classes_],
        "test_accuracy":round(float(acc), 4),
        "dataset":"synthetic classroom sensor data",
        "important_note":"Synthetic labels demonstrate the pipeline; this is not a certified AQI model."
    }
    (ARTIFACTS / "metadata.json").write_text(json.dumps(metadata, indent=2))
    report = classification_report(y_test, pred, output_dict=True, zero_division=0)
    (ARTIFACTS / "evaluation.json").write_text(json.dumps({
        "accuracy":float(acc), "classification_report":report,
        "confusion_matrix":confusion_matrix(y_test, pred, labels=list(model.classes_)).tolist(),
        "class_order":[str(x) for x in model.classes_]
    }, indent=2))
    print(f"Dataset: {csv_path}")
    print(f"Model saved: {ARTIFACTS / 'air_quality_risk_model.joblib'}")
    print(f"Test accuracy on synthetic held-out data: {acc:.3f}")
    print(classification_report(y_test, pred, zero_division=0))
    print("IMPORTANT: high test performance only measures agreement with the synthetic labelling rule.")

if __name__ == "__main__":
    main()
