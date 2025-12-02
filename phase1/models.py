from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense
import tensorflow as tf

def create_autoencoder(input_dim):
    # Same architecture as phase1_train_models.ipynb
    autoencoder = Sequential([
        Input(shape=(input_dim,)),
        Dense(8, activation='relu'),
        Dense(4, activation='relu'),
        Dense(2, activation='relu'),
        Dense(4, activation='relu'),
        Dense(8, activation='relu'),
        Dense(input_dim, activation='sigmoid')
    ])
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder
