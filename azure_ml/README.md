# Optional Azure Machine Learning model registration

The local project works without Azure credentials. To demonstrate model management in Azure ML:

1. Create an Azure Machine Learning workspace in the Azure portal (requires an Azure subscription and possibly billing).
2. Install Azure CLI and sign in: `az login`
3. From the project root activate your virtual environment and run:
   `pip install -r requirements-azure.txt`
4. In PowerShell set your real workspace values:
   ```powershell
   $env:AZURE_SUBSCRIPTION_ID="your-subscription-guid"
   $env:AZURE_RESOURCE_GROUP="your-resource-group"
   $env:AZURE_ML_WORKSPACE="your-workspace-name"
   ```
5. Train the model if needed: `python -m src.train_model`
6. Register it: `python azure_ml/register_model.py`

This registers a versioned model artifact in Azure ML. The dashboard still runs inference locally in the Docker container (edge-style); it does not require a cloud request per prediction. Do not paste credentials into source files or commit them to Git.
