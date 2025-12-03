import os
import sys
import numpy as np
import pandas as pd
import shap
import joblib
import tensorflow as tf
import matplotlib.pyplot as plt

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase1.feature_engine import preprocess_data
from phase1.models import get_autoencoder_model

def run_explainability():
    print("--- Phase C: Explainable AI (XAI) ---")

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(os.path.dirname(base_dir), 'backend', 'ml_artifacts')
    output_dir = os.path.join(base_dir, 'output')

    iso_model_path = os.path.join(backend_dir, 'model_isolation_forest.pkl')
    ae_model_path = os.path.join(backend_dir, 'model_autoencoder_federated.h5')

    # Check if models exist
    if not os.path.exists(iso_model_path):
        print(f"Error: Isolation Forest model not found at {iso_model_path}")
        return
    if not os.path.exists(ae_model_path):
        print(f"Error: Federated Autoencoder model not found at {ae_model_path}")
        return

    # Load models
    print("1. Loading models...")
    iso_forest = joblib.load(iso_model_path)

    try:
        # Reconstruct model and load weights
        # We need input_dim. Based on feature_engine, we have 4 features.
        features = ['velocity_kmh', 'time_diff_hours', 'device_trust_score', 'hour_of_day']
        autoencoder = get_autoencoder_model(len(features))

        # Load weights
        autoencoder.load_weights(ae_model_path)
        print("   Autoencoder weights loaded successfully.")
    except Exception as e:
        print(f"Error loading Keras model weights: {e}")
        # If loading weights fails, we might try full load again or abort
        return

    # Load sample data for explanation
    data_path = os.path.join(base_dir, 'data', 'synthetic_logins.csv')
    if not os.path.exists(data_path):
        print("Synthetic data not found, falling back to seed data.")
        data_path = os.path.join(base_dir, 'data', 'user_logins.csv')

    print(f"2. Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    df = preprocess_data(df)

    # Handle NaNs
    df[features] = df[features].fillna(0)

    X = df[features].values

    # We need a background dataset for SHAP (small sample)
    background_data = X[:100]
    # Test sample
    test_sample = X[100:105]

    print("3. Generating Explanations...")

    # A. SHAP for Isolation Forest
    print("   Explaining Isolation Forest...")
    explainer_iso = shap.TreeExplainer(iso_forest)
    shap_values_iso = explainer_iso.shap_values(test_sample)

    plt.figure()
    shap.summary_plot(shap_values_iso, test_sample, feature_names=features, show=False)
    iso_plot_path = os.path.join(output_dir, 'shap_isolation_forest.png')
    plt.savefig(iso_plot_path)
    plt.close()
    print(f"   Saved Isolation Forest explanation to {iso_plot_path}")

    # B. SHAP for Autoencoder
    print("   Explaining Autoencoder (this may take a moment)...")

    def model_loss_wrapper(data):
        reconstructions = autoencoder.predict(data, verbose=0)
        # MSE per sample
        mse = np.mean(np.power(data - reconstructions, 2), axis=1)
        return mse

    # KernelExplainer
    explainer_ae = shap.KernelExplainer(model_loss_wrapper, background_data[:20])
    shap_values_ae = explainer_ae.shap_values(test_sample)

    plt.figure()
    shap.summary_plot(shap_values_ae, test_sample, feature_names=features, show=False)
    ae_plot_path = os.path.join(output_dir, 'shap_autoencoder.png')
    plt.savefig(ae_plot_path)
    plt.close()
    print(f"   Saved Autoencoder explanation to {ae_plot_path}")

    print("✅ Phase C Complete. Explainability artifacts generated.")

if __name__ == "__main__":
    run_explainability()
