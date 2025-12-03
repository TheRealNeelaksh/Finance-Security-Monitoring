import pandas as pd
import numpy as np
from geopy.distance import geodesic

def get_geo_dist(row):
    """Calculates geodesic distance between current and previous coordinates."""
    if pd.isna(row['prev_lat']) or pd.isna(row['prev_lon']):
        return 0.0
    try:
        # geodesic expects (lat, lon) tuples
        return geodesic((row['prev_lat'], row['prev_lon']), (row['lat'], row['lon'])).km
    except:
        return 0.0

def preprocess_data(df):
    """
    Applies feature engineering to the raw login dataframe.
    Calculates: time_diff_hours, dist_km, velocity_kmh, device_trust_score, hour_of_day.
    """
    # Ensure timestamp is datetime and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)

    # A. Time Diff
    df['prev_time'] = df.groupby('user_id')['timestamp'].shift(1)
    df['time_diff_hours'] = (df['timestamp'] - df['prev_time']).dt.total_seconds() / 3600
    df['time_diff_hours'] = df['time_diff_hours'].fillna(0)

    # B. Distance & Velocity
    df['prev_lat'] = df.groupby('user_id')['lat'].shift(1)
    df['prev_lon'] = df.groupby('user_id')['lon'].shift(1)

    # Apply geodesic distance calculation
    # Using simple apply instead of progress_apply for script compatibility
    df['dist_km'] = df.apply(get_geo_dist, axis=1)

    # Avoid division by zero by adding a small epsilon
    df['velocity_kmh'] = df['dist_km'] / (df['time_diff_hours'] + 0.1)

    # C. Device Frequency & Trust Score
    device_counts = df.groupby(['user_id', 'device']).size().reset_index(name='count')
    total_counts = df.groupby('user_id').size().reset_index(name='total')
    device_stats = pd.merge(device_counts, total_counts, on='user_id')
    device_stats['device_trust_score'] = device_stats['count'] / device_stats['total']

    # Merge trust score back to original dataframe
    df = pd.merge(df, device_stats[['user_id', 'device', 'device_trust_score']],
                  on=['user_id', 'device'], how='left')

    # D. Temporal Features
    df['hour_of_day'] = df['timestamp'].dt.hour

    # Fill any remaining NaNs if necessary (though logic above handles most)
    df = df.fillna(0)

    return df
