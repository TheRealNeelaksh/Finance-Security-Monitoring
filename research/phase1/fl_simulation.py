import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
import flwr as fl
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Add the parent directory to sys.path to import modules locally in this process
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase1.feature_engine import preprocess_data
from phase1.models import get_autoencoder_model

def load_data():
    """Loads and preprocesses data for FL."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'synthetic_logins.csv')

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found at {data_path}. Run train_gan.py first.")

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    # Preprocess
    df = preprocess_data(df)

    # Prepare features
    features = ['velocity_kmh', 'time_diff_hours', 'device_trust_score', 'hour_of_day']
    # Handle NaNs just in case
    df[features] = df[features].fillna(0)

    X = df[features].values
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler

class AutoencoderClient(fl.client.NumPyClient):
    def __init__(self, x_train, x_val):
        self.x_train = x_train
        self.x_val = x_val
        self.model = get_autoencoder_model(x_train.shape[1])

    def get_parameters(self, config):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        # Train the model
        history = self.model.fit(
            self.x_train, self.x_train,
            epochs=5,
            batch_size=32,
            validation_data=(self.x_val, self.x_val),
            verbose=0
        )
        return self.model.get_weights(), len(self.x_train), {"loss": history.history["loss"][-1]}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss = self.model.evaluate(self.x_val, self.x_val, verbose=0)
        return loss, len(self.x_val), {"loss": loss}

# Extending Strategy to save weights
class SaveModelStrategy(fl.server.strategy.FedAvg):
    def aggregate_fit(self, server_round, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)

        if aggregated_parameters is not None:
            # Convert parameters to weights
            weights = fl.common.parameters_to_ndarrays(aggregated_parameters)

            print(f"Saving global model weights for round {server_round}...")

            # Assuming input_dim is 4 based on our features
            dummy_model = get_autoencoder_model(4)
            dummy_model.set_weights(weights)

            # Save to correct path
            # We use absolute path to be safe inside Ray workers if this runs there (though strategy runs on driver usually)
            save_path = os.path.abspath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                '..', 'backend', 'ml_artifacts', 'model_autoencoder_federated.h5'
            ))

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            dummy_model.save(save_path)
            print(f"Model saved to {save_path}")

        return aggregated_parameters, aggregated_metrics

if __name__ == "__main__":
    print("--- Phase B: Federated Learning (FL) Simulation ---")

    # 1. Load Data
    X_scaled, _ = load_data()

    # 2. Partition Data
    partitions = np.array_split(X_scaled, 3)
    print(f"Data partitioned into 3 clients with shapes: {[p.shape for p in partitions]}")

    def client_fn(cid: str):
        # Ray imports check
        # Inside the worker process, we might need to re-import if pickling failed,
        # but the module error happens BEFORE this function is called, during unpickling of the function itself.

        idx = int(cid)
        x_part = partitions[idx]
        x_train, x_val = train_test_split(x_part, test_size=0.2, random_state=42)
        return AutoencoderClient(x_train, x_val)

    # 3. Strategy
    strategy = SaveModelStrategy(
        fraction_fit=1.0,
        min_fit_clients=3,
        min_available_clients=3,
    )

    # 4. Start Simulation with Environment Setup
    print("Starting FL Simulation...")

    # We construct the PYTHONPATH to include the 'research' directory
    # so that 'import phase1.models' works inside Ray workers
    research_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    fl.simulation.start_simulation(
        client_fn=client_fn,
        num_clients=3,
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
        ray_init_args={
            "runtime_env": {
                "env_vars": {"PYTHONPATH": research_path}
            },
            "include_dashboard": False
        }
    )

    print("FL Simulation Complete.")
