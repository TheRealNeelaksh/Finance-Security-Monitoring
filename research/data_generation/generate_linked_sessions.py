import pandas as pd
import numpy as np
import random
from tqdm import tqdm

import os

# ==========================================
# CONFIGURATION
# ==========================================
# These match the LSTM vocabulary
ACTIONS = [
    'LOGIN', 'VIEW_BALANCE', 'VIEW_TRANSACTIONS', 
    'TRANSFER_SMALL', 'TRANSFER_LARGE', 
    'CHANGE_PASSWORD', 'ADD_RECIPIENT', 'LOGOUT'
]

# ==========================================
# 1. LOAD EXISTING LOGIN LOGS
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'phase1', 'user_logins.csv')

print("1. Loading existing user_logins.csv...")
try:
    df_logins = pd.read_csv(file_path)
except FileNotFoundError:
    print("❌ Error: user_logins.csv not found. Please run the Data Fabricator first.")
    exit()

print(f"   Found {len(df_logins)} login records.")

# ==========================================
# 2. GENERATE SEQUENCES FOR EACH LOGIN
# ==========================================
print("2. Generating session actions for each login...")

session_data = []

# We iterate through every single login in your CSV
for index, row in tqdm(df_logins.iterrows(), total=len(df_logins)):
    
    user_id = row['user_id']
    attack_type = row['attack_type'] # We check if the login itself was an attack
    
    # Start every session with LOGIN
    sequence = ['LOGIN']
    
    # --- LOGIC: LINKING LOGIN TYPE TO SESSION BEHAVIOR ---
    
    # CASE A: Known Attack Types (From Phase 1)
    if attack_type in ['Brute Force Success', 'Device Spoofing', 'Impossible Travel']:
        # If the login was suspicious, the session is likely aggressive
        # Pattern: Quick Drain or Profile Change
        if random.random() < 0.8: # 80% chance they act malicious immediately
            sequence.append('ADD_RECIPIENT')
            sequence.append('TRANSFER_LARGE')
            sequence.append('LOGOUT')
        else:
            # 20% chance they act "Sleepy" (login and wait) to hide
            sequence.append('VIEW_BALANCE')
            sequence.append('LOGOUT')
            
    # CASE B: Failed Login (Brute Force Fail)
    elif row['login_status'] == 'Failed':
        # No session happens if login failed!
        sequence = ['LOGIN_ATTEMPT_FAILED']
        
    # CASE C: Normal Login (or Vacation)
    else:
        # Generate a normal random sequence
        seq_len = random.randint(2, 6)
        for _ in range(seq_len):
            action = random.choice(['VIEW_BALANCE', 'VIEW_TRANSACTIONS', 'TRANSFER_SMALL', 'LOGOUT'])
            sequence.append(action)
            if action == 'LOGOUT':
                break

    # Save as a string representation we can parse later
    # e.g., "LOGIN,VIEW_BALANCE,LOGOUT"
    session_str = ",".join(sequence)
    
    session_data.append({
        'user_id': user_id,
        'timestamp': row['timestamp'],
        'session_sequence': session_str,
        'is_attack': row['is_attack'] # Inherit the label
    })

# ==========================================
# 3. SAVE SESSION LOGS
# ==========================================
df_sessions = pd.DataFrame(session_data)
# Filter out failed logins (no session data needed)
df_sessions = df_sessions[df_sessions['session_sequence'] != 'LOGIN_ATTEMPT_FAILED']

df_sessions.to_csv(r'.\phase1\user_sessions.csv', index=False)
print("\n✅ Session Data Generated!")
print(f"   Saved {len(df_sessions)} sessions to 'user_sessions.csv'")
print(df_sessions.head())