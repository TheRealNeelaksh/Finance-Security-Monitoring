import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import warnings

# Suppress the warnings about Sklearn versions
warnings.filterwarnings("ignore", category=UserWarning)

class AIEngine:
    def __init__(self):
        self.scaler = None
        self.model_iforest = None
        self.model_autoencoder = None
        self.model_lstm = None
        self.network_scores = {}
        
        self.ARTIFACTS_DIR = os.path.join(os.getcwd(), "ml_artifacts")

    def load_models(self):
        print(f"⏳ Loading AI Models from {self.ARTIFACTS_DIR}...")
        try:
            # 1. Load Scaler
            self.scaler = joblib.load(os.path.join(self.ARTIFACTS_DIR, "scaler.pkl"))
            
            # 2. Load Isolation Forest
            self.model_iforest = joblib.load(os.path.join(self.ARTIFACTS_DIR, "model_isolation_forest.pkl"))
            
            # 3. Load Deep Learning Models (TensorFlow/Keras)
            # compile=False is CRITICAL for version compatibility
            self.model_autoencoder = tf.keras.models.load_model(
                os.path.join(self.ARTIFACTS_DIR, "model_autoencoder.h5"), 
                compile=False
            )
            self.model_lstm = tf.keras.models.load_model(
                os.path.join(self.ARTIFACTS_DIR, "model_lstm.h5"), 
                compile=False
            )
            print(f"🕵️ LSTM Expected Input Shape: {self.model_lstm.input_shape}")
            
            # 4. Load Network Scores (CSV)
            csv_path = os.path.join(self.ARTIFACTS_DIR, "network_risk_scores.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                
                # --- FIX: Using the correct column name 'network_risk_score' ---
                self.network_scores = dict(zip(df['user_id'].astype(str), df['network_risk_score']))
            
            print("✅ AI Engine Online: All models loaded.")
        except Exception as e:
            print(f"❌ Critical Error Loading Models: {e}")

    def predict(self, user_id: str, features: list, sequence_data: list):
        # --- Preprocessing ---
        features_arr = np.array(features).reshape(1, -1)
        scaled_features = self.scaler.transform(features_arr)
        
        # --- Model A1: Isolation Forest ---
        iso_pred = self.model_iforest.predict(scaled_features)
        score_iso = 1.0 if iso_pred[0] == -1 else 0.0
        
        # --- Model A2: Autoencoder ---
        reconstructed = self.model_autoencoder.predict(scaled_features, verbose=0)
        mse = np.mean(np.power(scaled_features - reconstructed, 2), axis=1)
        score_ae = min(float(mse[0]) * 10, 1.0) 
        
        # --- Model B: LSTM ---
        # FIX: Handle 1D Sequence of Integers for Embedding Layer
        seq_arr = np.array(sequence_data)
        
        # If data is [[1], [2]...], flatten it to [1, 2...]
        if seq_arr.ndim == 2 and seq_arr.shape[1] == 1:
             seq_arr = seq_arr.flatten()
             
        # Ensure exactly 10 items
        if len(seq_arr) < 10:
            seq_arr = np.pad(seq_arr, (10 - len(seq_arr), 0), 'constant')
        
        seq_arr = seq_arr[-10:] # Take last 10
        
        # Reshape to (1, 10) - Correct shape for Embedding Layer!
        lstm_input = seq_arr.reshape(1, 10)
        
        lstm_pred = self.model_lstm.predict(lstm_input, verbose=0)
        score_lstm = float(lstm_pred[0][0])
        
        # --- Model C: Network Lookup ---
        score_network = self.network_scores.get(str(user_id), 0.0)
        
        return {
            "iso": score_iso,
            "ae": score_ae,
            "lstm": score_lstm,
            "network": score_network
        }

ai_engine = AIEngine()