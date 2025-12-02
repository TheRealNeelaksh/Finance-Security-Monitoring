import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from geopy.distance import geodesic
import joblib

class FeatureEngine:
    def __init__(self, scaler=None):
        self.scaler = scaler if scaler else MinMaxScaler()
        self.features = ['velocity_kmh', 'time_diff_hours', 'device_trust_score', 'hour_of_day']

    def preprocess(self, df):
        # Convert timestamp
        if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        df = df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)

        # A. Time Diff
        df['prev_time'] = df.groupby('user_id')['timestamp'].shift(1)
        df['time_diff_hours'] = (df['timestamp'] - df['prev_time']).dt.total_seconds() / 3600
        df['time_diff_hours'] = df['time_diff_hours'].fillna(0)

        # B. Distance & Velocity
        df['prev_lat'] = df.groupby('user_id')['lat'].shift(1)
        df['prev_lon'] = df.groupby('user_id')['lon'].shift(1)

        def get_geo_dist(row):
            if pd.isna(row['prev_lat']): return 0.0
            try:
                return geodesic((row['prev_lat'], row['prev_lon']), (row['lat'], row['lon'])).km
            except:
                return 0.0

        # Note: In the original notebook, progress_apply was used. Standard apply is safer for scripts.
        df['dist_km'] = df.apply(get_geo_dist, axis=1)
        df['velocity_kmh'] = df['dist_km'] / (df['time_diff_hours'] + 0.1)

        # C. Device Frequency
        device_counts = df.groupby(['user_id', 'device']).size().reset_index(name='count')
        total_counts = df.groupby('user_id').size().reset_index(name='total')
        device_stats = pd.merge(device_counts, total_counts, on='user_id')
        device_stats['device_trust_score'] = device_stats['count'] / device_stats['total']

        df = pd.merge(df, device_stats[['user_id', 'device', 'device_trust_score']],
                      on=['user_id', 'device'], how='left')

        df['hour_of_day'] = df['timestamp'].dt.hour

        # Fill any remaining NaNs (e.g. from joins)
        df = df.fillna(0)

        return df

    def fit_transform(self, df):
        df = self.preprocess(df)
        X = df[self.features]
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, df

    def transform(self, df):
        df = self.preprocess(df)
        X = df[self.features]
        X_scaled = self.scaler.transform(X)
        return X_scaled, df
