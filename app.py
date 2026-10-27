import time
from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from src.predictor import load_model, predict_risk
from src.simulator import SensorSimulator

st.set_page_config(page_title="EdgeSense AI", page_icon="🌿", layout="wide")
st.title("🌿 EdgeSense AI — Real-Time IoT Air Quality Risk")
st.caption("Simulated sensor telemetry → local ML inference → live dashboard. Docker-ready; Azure ML model registration is optional.")

@st.cache_resource
def get_model():
    return load_model()

model, metadata = get_model()
if "simulator" not in st.session_state:
    st.session_state.simulator = SensorSimulator(seed=42)
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Simulation controls")
    interval = st.slider("Refresh interval (seconds)", 1, 5, 2)
    auto = st.toggle("Auto-refresh", value=False)
    source = st.radio("Telemetry source", ["Wokwi ESP32", "Built-in Python simulator"], index=0)
    st.write("Sensor values are simulated; they are not measurements from a physical device.")
    if st.button("Clear history"):
        st.session_state.history = []

reading = st.session_state.simulator.read()
result = predict_risk(model, reading)
reading["timestamp"] = datetime.now().strftime("%H:%M:%S")
reading["risk_label"] = result["label"]
reading["risk_probability"] = result["probability"]
st.session_state.history.append(reading)
st.session_state.history = st.session_state.history[-100:]

a,b,c,d = st.columns(4)
a.metric("PM2.5", f'{reading["pm25"]:.1f} µg/m³')
b.metric("Temperature", f'{reading["temperature"]:.1f} °C')
c.metric("Humidity", f'{reading["humidity"]:.1f}%')
d.metric("CO₂", f'{reading["co2"]:.0f} ppm')
color = {"Low":"🟢","Moderate":"🟡","High":"🔴"}.get(result["label"], "⚪")
st.subheader(f"{color} Predicted air-quality risk: {result['label']}")
st.progress(min(max(float(result["probability"]), 0.0), 1.0), text=f"Model confidence for predicted class: {result['probability']:.1%}")
st.info(result["advice"])

hist = pd.DataFrame(st.session_state.history)
left, right = st.columns(2)
with left:
    st.subheader("Live sensor readings")
    st.plotly_chart(px.line(hist, x="timestamp", y=["pm25", "co2"], markers=True, title="PM2.5 and CO₂"), use_container_width=True)
with right:
    st.subheader("Risk history")
    st.plotly_chart(px.scatter(hist, x="timestamp", y="pm25", color="risk_label", size="risk_probability",
                               title="Predicted risk by PM2.5"), use_container_width=True)
st.subheader("Latest telemetry")
show_cols = ["timestamp", "temperature", "humidity", "pm25", "pm10", "co2", "voc", "risk_label", "risk_probability"]
st.dataframe(hist[show_cols].tail(15).iloc[::-1], use_container_width=True, hide_index=True)
st.caption(f'Model: {metadata.get("model_name", "RandomForestClassifier")} | Inference runs locally in this app/container.')
if auto:
    time.sleep(interval)
    st.rerun()
