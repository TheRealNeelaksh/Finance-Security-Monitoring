import shap
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
import matplotlib.pyplot as plt
from phase1.models import create_autoencoder
from phase1.feature_engine import FeatureEngine
import os

# Disable eager execution for SHAP DeepExplainer compatibility in some versions,
# but for KernelExplainer it's fine. We'll use KernelExplainer for agnostic support.
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def explain_fraud_prediction():
    print("1. Loading Models & Data...")

    # Load Feature Engine
    engine = FeatureEngine()

    # Load Data (Use synthetic or real, let's use synthetic to be consistent with pipeline)
    df = pd.read_csv('phase1/synthetic_logins.csv')
    X_scaled, df_processed = engine.fit_transform(df)

    # Load Isolation Forest (Baseline)
    # If not found, we handle gracefully. It should be there from original repo or we might need to train one.
    # The original repo had `phase1/model_isolation_forest.pkl`.
    if os.path.exists('phase1/model_isolation_forest.pkl'):
        iso_forest = joblib.load('phase1/model_isolation_forest.pkl')
    else:
        print("⚠️  Isolation Forest model not found. Training a temporary one for demo.")
        from sklearn.ensemble import IsolationForest
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        iso_forest.fit(X_scaled)

    # Load Federated Autoencoder
    # We need to re-create the architecture and load weights because we saved as .h5
    input_dim = X_scaled.shape[1]
    autoencoder = create_autoencoder(input_dim)
    if os.path.exists('phase1/model_autoencoder_federated.h5'):
        autoencoder.load_weights('phase1/model_autoencoder_federated.h5')
    else:
        print("⚠️  Federated Autoencoder not found. Please run FL simulation first.")
        return

    # ==========================================
    # 2. SELECT A "FRAUD" INSTANCE TO EXPLAIN
    # ==========================================
    # Let's pick a data point that the Autoencoder finds anomalous (high reconstruction error)
    reconstructions = autoencoder.predict(X_scaled)
    mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)

    # Pick the index with highest error
    anomaly_idx = np.argmax(mse)
    instance = X_scaled[anomaly_idx].reshape(1, -1)

    print(f"2. Explaining Anomaly at Index {anomaly_idx}...")
    print(f"   Reconstruction Error (MSE): {mse[anomaly_idx]:.4f}")

    feature_names = engine.features

    # ==========================================
    # 3. SHAP for ISOLATION FOREST (TreeExplainer)
    # ==========================================
    print("\n--- SHAP for Isolation Forest ---")
    explainer_iso = shap.TreeExplainer(iso_forest)
    shap_values_iso = explainer_iso.shap_values(instance)

    print("   Feature contributions to Anomaly Score:")
    # shap_values might be a list if check_additivity is on, usually it's array for IF
    vals = shap_values_iso[0] if isinstance(shap_values_iso, list) else shap_values_iso

    for i, feature in enumerate(feature_names):
        print(f"   {feature}: {vals[0][i]:.4f}")

    # ==========================================
    # 4. SHAP for AUTOENCODER (KernelExplainer)
    # ==========================================
    print("\n--- SHAP for Federated Autoencoder ---")
    # We use KernelExplainer as it's model-agnostic and works well for black-box NN functions.
    # We explain the MSE loss function, not the raw output

    def model_loss(data):
        # Returns MSE for each sample
        recon = autoencoder.predict(data, verbose=0)
        return np.mean(np.power(data - recon, 2), axis=1)

    # Use a small background dataset for reference (e.g., median values)
    background = shap.kmeans(X_scaled, 10)
    explainer_ae = shap.KernelExplainer(model_loss, background)

    shap_values_ae = explainer_ae.shap_values(instance)

    print("   Feature contributions to Reconstruction Error (Risk):")
    for i, feature in enumerate(feature_names):
        print(f"   {feature}: {shap_values_ae[0][i]:.4f}")

    # ==========================================
    # 5. VISUALIZATION
    # ==========================================
    print("\n5. Generating Plots...")
    # Force Plot for AE
    shap.initjs()
    plot = shap.force_plot(explainer_ae.expected_value, shap_values_ae[0], instance[0], feature_names=feature_names, matplotlib=True, show=False)
    plt.savefig('phase2/shap_explanation_force_plot.png')
    print("✅ Saved 'phase2/shap_explanation_force_plot.png'")

if __name__ == "__main__":
    explain_fraud_prediction()
