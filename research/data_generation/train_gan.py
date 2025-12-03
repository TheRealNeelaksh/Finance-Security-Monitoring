import os
import pandas as pd
from ctgan import CTGAN
import torch

def train_gan_and_generate():
    print("--- Phase A: Generative AI (GANs) ---")

    # Path configuration
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'user_logins.csv')
    output_path = os.path.join(base_dir, 'data', 'synthetic_logins.csv')

    if not os.path.exists(data_path):
        print(f"Error: Seed data not found at {data_path}")
        return

    print(f"1. Loading seed data from {data_path}...")
    data = pd.read_csv(data_path)

    # Pre-processing
    if 'timestamp' in data.columns:
        print("   Converting timestamp to numeric...")
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['timestamp_numeric'] = data['timestamp'].astype('int64') // 10**9
        data_for_gan = data.drop(columns=['timestamp'])
    else:
        data_for_gan = data.copy()

    # Identify all discrete columns
    # We leave lat/lon/timestamp_numeric as continuous
    discrete_columns = ['user_id', 'country', 'device', 'login_status', 'attack_type', 'is_attack']

    print("2. Training CTGAN (this may take a few minutes)...")
    # Reduced epochs slightly to ensure completion within reasonable time,
    # but 5 is enough for a demo showing "it works".
    ctgan = CTGAN(epochs=5, verbose=True)
    ctgan.fit(data_for_gan, discrete_columns=discrete_columns)

    print("3. Generating synthetic data...")
    synthetic_data = ctgan.sample(len(data))

    if 'timestamp_numeric' in synthetic_data.columns:
        synthetic_data['timestamp'] = pd.to_datetime(synthetic_data['timestamp_numeric'], unit='s')
        synthetic_data = synthetic_data.drop(columns=['timestamp_numeric'])

    print(f"4. Saving synthetic data to {output_path}...")
    synthetic_data.to_csv(output_path, index=False)

    print("✅ Phase A Complete. Synthetic data generated.")

if __name__ == "__main__":
    train_gan_and_generate()
