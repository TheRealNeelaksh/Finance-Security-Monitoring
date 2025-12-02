import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from tqdm import tqdm

import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)

# ==========================================
# CONFIGURATION
# ==========================================
NUM_USERS = 500
TOTAL_RECORDS = 20000 
START_DATE = datetime.now() - timedelta(days=90)

# Real-world locations (Lat, Lon, Country)
LOCATIONS = [
    {"country": "US", "city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"country": "US", "city": "San Francisco", "lat": 37.7749, "lon": -122.4194},
    {"country": "IN", "city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"country": "IN", "city": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    {"country": "GB", "city": "London", "lat": 51.5074, "lon": -0.1278},
    {"country": "DE", "city": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"country": "JP", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"country": "AU", "city": "Sydney", "lat": -33.8688, "lon": 151.2093}
]

# User Agents
DEVICES = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)", # Mobile
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",             # Desktop
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",       # Mac
    "Mozilla/5.0 (Linux; Android 10; SM-G960U)"              # Android
]

# ==========================================
# 1. BUILD USER PROFILES
# ==========================================
print("1. Building User Profiles...")
users = {}
for i in range(NUM_USERS):
    user_id = f"user_{i:04d}"
    home_loc = random.choice(LOCATIONS)
    
    users[user_id] = {
        "home": home_loc,
        "current_loc": home_loc,
        "device": random.choice(DEVICES),
        "behavior_mode": "normal", # normal, vacation, compromised
        "last_login": START_DATE
    }

# ==========================================
# 2. GENERATE COMPLEX LOGS
# ==========================================
print(f"2. Generating {TOTAL_RECORDS} logs with complex scenarios...")
data = []

# We simulate time passing day by day to ensure sequential logic is correct
current_sim_time = START_DATE
records_generated = 0

pbar = tqdm(total=TOTAL_RECORDS)

while records_generated < TOTAL_RECORDS:
    # Pick a random user
    user_id = f"user_{random.randint(0, NUM_USERS-1):04d}"
    profile = users[user_id]
    
    # Time logic: Advance user's time by random amount (1 hour to 3 days)
    time_jump = timedelta(hours=random.randint(1, 72))
    login_time = profile["last_login"] + time_jump
    
    # Update global time reference roughly
    if login_time > current_sim_time:
        current_sim_time = login_time

    # Default values
    lat = profile["current_loc"]["lat"]
    lon = profile["current_loc"]["lon"]
    country = profile["current_loc"]["country"]
    device = profile["device"]
    status = "Success"
    attack_label = "Normal"
    risk_score = 0.0 # Ground truth (0=Safe, 1=Fraud)
    
    # --- SCENARIO GENERATOR ---
    dice = random.random()

    # SCENARIO A: Normal Login (80%)
    if dice < 0.80:
        # Add slight GPS jitter (users don't stand still)
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)
        
        # Rare event: User buys a new phone (False Positive trap)
        if random.random() < 0.05:
            device = random.choice(DEVICES) # New device
            # Note: We do NOT label this as attack. AI must learn this is OK if location is safe.
    
    # SCENARIO B: The "Vacation" (Legitimate Travel) (10%)
    elif dice < 0.90:
        # User moves to a new country and STAYS there for a while
        if profile["behavior_mode"] != "vacation":
            new_loc = random.choice(LOCATIONS)
            profile["current_loc"] = new_loc # Update "Current" so next login is from here too
            profile["behavior_mode"] = "vacation"
        
        lat = profile["current_loc"]["lat"]
        lon = profile["current_loc"]["lon"]
        country = profile["current_loc"]["country"]
        # This is NOT an attack. It's valid travel.
        attack_label = "Vacation"
        
    # SCENARIO C: Impossible Travel Attack (3%)
    elif dice < 0.93:
        # Login from random far away place, but DO NOT update "current_loc"
        # because the real user is still at home.
        far_loc = random.choice(LOCATIONS)
        while far_loc["country"] == profile["home"]["country"]:
            far_loc = random.choice(LOCATIONS)
            
        lat = far_loc["lat"]
        lon = far_loc["lon"]
        country = far_loc["country"]
        
        # Login happens VERY soon after last login (e.g., 10 mins)
        login_time = profile["last_login"] + timedelta(minutes=random.randint(5, 30))
        attack_label = "Impossible Travel"
        risk_score = 1.0

    # SCENARIO D: Brute Force Attack (3%)
    elif dice < 0.96:
        # Generate 3-5 FAILED logs before the current log
        num_fails = random.randint(3, 6)
        for _ in range(num_fails):
            fail_time = login_time - timedelta(minutes=num_fails - _)
            data.append({
                "timestamp": fail_time,
                "user_id": user_id,
                "lat": lat, "lon": lon, "country": country,
                "device": device,
                "login_status": "Failed",
                "attack_type": "Brute Force",
                "is_attack": 1
            })
            records_generated += 1
            pbar.update(1)
            
        status = "Success" # The final breach
        attack_label = "Brute Force Success"
        risk_score = 1.0

    # SCENARIO E: Botnet / Device Spoofing (4%)
    else:
        # Correct location, but random User Agent (scripted attack)
        device = fake.user_agent() 
        attack_label = "Device Spoofing"
        risk_score = 1.0

    # Update User State
    profile["last_login"] = login_time

    # Append Main Record
    data.append({
        "timestamp": login_time,
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "country": country,
        "device": device,
        "login_status": status,
        "attack_type": attack_label,
        "is_attack": 1 if risk_score > 0 else 0
    })
    
    records_generated += 1
    pbar.update(1)

pbar.close()

# ==========================================
# 3. SAVE AND SUMMARY
# ==========================================
df = pd.DataFrame(data)
df = df.sort_values(by="timestamp")

print("\n--- DATA GENERATION COMPLETE ---")
print(f"Total Records: {len(df)}")
print("\nScenario Distribution:")
print(df["attack_type"].value_counts())

print("\nLogin Status:")
print(df["login_status"].value_counts())



# Save
df.to_csv(r"phase1\user_logins.csv", index=False)
print("\nSaved to 'user_logins.csv'. Ready for Phase 1 processing.")