import argparse
import json
import random
import sys
import time
from datetime import datetime
import requests

# Hardcoded Configuration
API_URL = "https://secure-watch-ai.vercel.app/api/login"

TEST_USERS = [
    {"username": "alice", "password": "password123"},
    {"username": "bob", "password": "password123"},
    {"username": "charlie", "password": "password123"},
    {"username": "dave", "password": "password123"},
    {"username": "eve", "password": "password123"},
    {"username": "frank", "password": "password123"},
    {"username": "grace", "password": "password123"},
    {"username": "heidi", "password": "password123"},
]

# Mapping cities to IPs for "geoposition-based" logic
GEO_IPS = {
    "New York": "192.168.1.101",
    "London": "192.168.1.102",
    "Tokyo": "192.168.1.103",
    "Paris": "192.168.1.104",
    "Sydney": "192.168.1.105",
    "Berlin": "192.168.1.106",
    "Beijing": "192.168.1.107",
    "Moscow": "192.168.1.108",
    "Brazil": "192.168.1.109",
    "Cairo": "192.168.1.110"
}
GEO_KEYS = list(GEO_IPS.keys())

def get_timestamp():
    return datetime.now().isoformat() + "Z"

def send_event(payload):
    try:
        print(f"Sending event: {json.dumps(payload)}")
        response = requests.post(API_URL, json=payload, timeout=5)
        print(f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending request: {e}")

def mode_normal(count, **kwargs):
    print(f"Starting NORMAL simulation (count={count})...")
    for _ in range(count):
        user = random.choice(TEST_USERS)
        loc = random.choice(GEO_KEYS)
        ip = GEO_IPS[loc]

        payload = {
            "username": user["username"],
            "password": user["password"],
            "ip": ip,
            "timestamp": get_timestamp(),
            "mode": "normal"
        }
        send_event(payload)
        time.sleep(random.uniform(0.5, 2.0))

def mode_impossible_travel(user_arg, **kwargs):
    # If user not specified, pick random
    if user_arg:
        user = next((u for u in TEST_USERS if u["username"] == user_arg), {"username": user_arg, "password": "password123"})
    else:
        user = random.choice(TEST_USERS)

    print(f"Starting IMPOSSIBLE TRAVEL simulation for user {user['username']}...")

    # Login 1: Location A
    loc1 = "New York"
    ip1 = GEO_IPS[loc1]

    # Login 2: Location B (distant)
    loc2 = "Tokyo"
    ip2 = GEO_IPS[loc2]

    payload1 = {
        "username": user["username"],
        "password": user["password"],
        "ip": ip1,
        "timestamp": get_timestamp(),
        "mode": "impossible_travel"
    }
    send_event(payload1)

    # Rapid succession
    print("sleeping briefly...")
    time.sleep(1)

    payload2 = {
        "username": user["username"],
        "password": user["password"],
        "ip": ip2,
        "timestamp": get_timestamp(),
        "mode": "impossible_travel"
    }
    send_event(payload2)

def mode_bot_script(user_arg, rate, **kwargs):
    # High frequency attempts
    if user_arg:
        user = next((u for u in TEST_USERS if u["username"] == user_arg), {"username": user_arg, "password": "password123"})
    else:
        user = random.choice(TEST_USERS)

    count = rate if rate else 20
    print(f"Starting BOT SCRIPT simulation for user {user['username']} (count={count})...")

    for _ in range(count):
        loc = random.choice(GEO_KEYS)
        ip = GEO_IPS[loc]

        payload = {
            "username": user["username"],
            "password": user["password"],
            "ip": ip,
            "timestamp": get_timestamp(),
            "mode": "bot_script"
        }
        send_event(payload)
        time.sleep(0.1) # Rapid

def mode_fraud_ring(group_size, **kwargs):
    size = group_size if group_size else 5
    print(f"Starting FRAUD RING simulation (group_size={size})...")

    # Same IP, different users
    loc = random.choice(GEO_KEYS)
    target_ip = GEO_IPS[loc]
    print(f"Target Shared IP: {target_ip} ({loc})")

    # Ensure we have enough users or reuse
    users_to_use = []
    while len(users_to_use) < size:
        users_to_use.extend(TEST_USERS)
    users_to_use = users_to_use[:size]

    for user in users_to_use:
        payload = {
            "username": user["username"],
            "password": user["password"],
            "ip": target_ip,
            "timestamp": get_timestamp(),
            "mode": "fraud_ring"
        }
        send_event(payload)
        time.sleep(0.2)

def main():
    parser = argparse.ArgumentParser(description="Login Simulator for Secure Watch AI")
    parser.add_argument("--mode", required=True, choices=["normal", "impossible_travel", "bot_script", "fraud_ring"], help="Simulation mode")
    parser.add_argument("--count", type=int, default=1, help="Number of requests for normal mode")
    parser.add_argument("--user", type=str, help="Specific username for impossible_travel or bot_script")
    parser.add_argument("--rate", type=int, default=20, help="Number of requests for bot_script")
    parser.add_argument("--group-size", type=int, default=5, help="Number of users for fraud_ring")

    args = parser.parse_args()

    try:
        if args.mode == "normal":
            mode_normal(count=args.count)
        elif args.mode == "impossible_travel":
            mode_impossible_travel(user_arg=args.user)
        elif args.mode == "bot_script":
            mode_bot_script(user_arg=args.user, rate=args.rate)
        elif args.mode == "fraud_ring":
            mode_fraud_ring(group_size=args.group_size)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
