from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense

def get_autoencoder_model(input_dim):
    """
    Returns the compiled Autoencoder model architecture.
    """
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
