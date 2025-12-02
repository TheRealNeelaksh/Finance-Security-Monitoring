import pandas as pd
from ctgan import CTGAN
import torch
import os
from datetime import datetime, timedelta

def train_gan_and_generate():
    print("1. Loading Real Data...")
    file_path = 'phase1/user_logins.csv'

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found. Please run the original datagen or ensure the file exists.")

    df = pd.read_csv(file_path)

    # Preprocessing for GAN
    # We drop high cardinality columns like timestamp (we'll simulate it back later)
    # We keep user_id out for now and regenerate it, as GANs struggle with unique IDs
    data_for_gan = df[['lat', 'lon', 'country', 'device', 'login_status', 'attack_type', 'is_attack']]

    discrete_columns = ['country', 'device', 'login_status', 'attack_type', 'is_attack']

    print("2. Training CTGAN (this may take a while)...")
    # Epochs set to 10 for demonstration speed.
    # In a real scenario, we would use more epochs (e.g. 300).
    ctgan = CTGAN(epochs=10, verbose=True)
    ctgan.fit(data_for_gan, discrete_columns)

    print("3. Generating Synthetic Data...")
    synthetic_data = ctgan.sample(len(df))

    # Post-processing: Add fake User IDs and Timestamps to match schema
    synthetic_data['user_id'] = [f"user_{i%500:04d}" for i in range(len(synthetic_data))]

    start_time = datetime.now()
    # Create timestamps that look sequential
    synthetic_data['timestamp'] = [start_time - timedelta(minutes=i*5) for i in range(len(synthetic_data))]

    # Sort by timestamp ascending to mimic logs
    synthetic_data = synthetic_data.sort_values(by='timestamp').reset_index(drop=True)

    # Save
    output_path = 'phase1/synthetic_logins.csv'
    synthetic_data.to_csv(output_path, index=False)
    print(f"✅ Synthetic data saved to {output_path}")
    print(synthetic_data.head())

if __name__ == "__main__":
    train_gan_and_generate()
