"""
Register the locally trained model in Azure Machine Learning (SDK v2).
Prerequisites:
  1) Azure subscription and an Azure ML workspace already created.
  2) `az login` completed, and your account has permission to the workspace.
  3) pip install -r requirements-azure.txt
Set environment variables AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_ML_WORKSPACE.
"""
import os
from pathlib import Path
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential

ROOT = Path(__file__).resolve().parents[1]
model_path = ROOT / "artifacts" / "air_quality_risk_model.joblib"
if not model_path.exists():
    raise SystemExit("Model not found. Run `python -m src.train_model` first.")

required = ["AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP", "AZURE_ML_WORKSPACE"]
missing = [key for key in required if not os.getenv(key)]
if missing:
    raise SystemExit("Set these environment variables first: " + ", ".join(missing))

client = MLClient(
    DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AZURE_ML_WORKSPACE"],
)
registered = client.models.create_or_update(Model(
    path=str(model_path),
    name="edgesense-air-quality-risk",
    description="Random Forest risk classifier trained on synthetic IoT air sensor data for a student edge demo.",
    type="custom_model",
    tags={"project":"AIEC-mini-project", "inference":"local-edge", "data":"synthetic"}
))
print(f"Registered Azure ML model: {registered.name}, version={registered.version}")
