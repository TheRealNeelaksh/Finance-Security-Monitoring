import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase1.feature_engine import preprocess_data
from phase1.models import get_autoencoder_model

def run_inference():
    print("--- Inference Engine: Fraud Risk Scoring ---")

    # Path Setup
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(os.path.dirname(base_dir), 'backend', 'ml_artifacts')
    data_path = os.path.join(base_dir, 'data', 'user_logins.csv') # Use original data for "real" prediction
    model_path = os.path.join(backend_dir, 'model_autoencoder_federated.h5')
    output_path = os.path.join(base_dir, 'output', 'scored_transactions.csv')

    # 1. Load Model
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    print(f"1. Loading Federated Autoencoder from {model_path}...")

    # Reconstruct model and load weights (safer than load_model for custom envs)
    # Features used: velocity_kmh, time_diff_hours, device_trust_score, hour_of_day
    input_dim = 4
    autoencoder = get_autoencoder_model(input_dim)
    try:
        autoencoder.load_weights(model_path)
    except Exception as e:
        print(f"Error loading weights: {e}")
        return

    # 2. Load & Preprocess Data
    print(f"2. Loading data from {data_path}...")
    original_df = pd.read_csv(data_path)

    # We work on a copy for preprocessing to keep original data clean for the report
    df_proc = original_df.copy()
    df_proc = preprocess_data(df_proc)

    features = ['velocity_kmh', 'time_diff_hours', 'device_trust_score', 'hour_of_day']
    # Handle NaNs
    df_proc[features] = df_proc[features].fillna(0)

    X = df_proc[features].values
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Predict (Calculate Risk Score)
    print("3. Running inference...")
    reconstructions = autoencoder.predict(X_scaled, verbose=0)
    # MSE is our "Risk Score" - higher means more anomalous
    mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)

    # 4. Thresholding (Dynamic 95th percentile for this batch)
    # In production, this threshold would be fixed/loaded from an artifact.
    threshold = np.percentile(mse, 95)
    print(f"   Calculated Anomaly Threshold (95th percentile): {threshold:.5f}")

    # 5. Compile Results
    # We attach scores to the original dataframe
    # Note: df_proc was sorted by user/time in preprocess_data, so we must match indices carefully.
    # preprocess_data does: df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)
    # So we should use df_proc as the base for the report to ensure alignment.

    results_df = df_proc.copy()
    results_df['risk_score'] = mse
    results_df['predicted_fraud'] = (mse > threshold).astype(int)

    # Select relevant columns for the report
    output_columns = [
        'timestamp', 'user_id', 'country', 'device',
        'velocity_kmh', 'time_diff_hours', 'device_trust_score',
        'risk_score', 'predicted_fraud', 'is_attack'
    ]
    # Keep is_attack if it exists for validation comparison
    cols_to_save = [c for c in output_columns if c in results_df.columns]
    results_df = results_df[cols_to_save]

    # 6. Save
    print(f"4. Saving scored data to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results_df.to_csv(output_path, index=False)

    # Show sample
    print("\n--- Inference Sample ---")
    print(results_df.head())
    print("\n✅ Inference Complete.")

if __name__ == "__main__":
    run_inference()
