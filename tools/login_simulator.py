import requests
import time
import random
import sys

# --- CONFIGURATION ---
# If running locally:
# API_URL = "http://127.0.0.1:8000/security/analyze-login"
# If running on Render/Vercel, change to:
API_URL = "https://finance-security-ai-monitor.onrender.com/security/analyze-login"

# Colors for Terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

USERS = ["alice", "bob", "charlie", "diana", "eve_hacker"]

def send_request(user_id, features, sequence, attack_name):
    payload = {
        "user_id": user_id,
        "features": features,
        "sequence_data": sequence
    }
    
    try:
        start = time.time()
        res = requests.post(API_URL, json=payload, timeout=5)
        latency = round((time.time() - start) * 1000)
        
        if res.status_code == 200:
            data = res.json()
            verdict = data.get("verdict")
            risk = int(data.get("risk_score", 0) * 100)
            reason = data.get("breakdown", {}).get("reason", "Unknown") # If you added reason to breakdown
            
            if verdict == "BLOCK":
                print(f"{RED}[BLOCKED]{RESET} {attack_name} | Risk: {risk}% | User: {user_id} | {latency}ms")
            elif verdict == "MFA_CHALLENGE":
                print(f"{YELLOW}[FLAGGED]{RESET} {attack_name} | Risk: {risk}% | User: {user_id} | {latency}ms")
            else:
                print(f"{GREEN}[ALLOWED]{RESET} {attack_name} | Risk: {risk}% | User: {user_id} | {latency}ms")
        else:
            print(f"{RED}[ERROR]{RESET} Server returned {res.status_code}")
            
    except Exception as e:
        print(f"{RED}[FAIL]{RESET} Could not connect to backend. Is it running? {e}")

def run_simulation():
    print(f"\n{YELLOW}🛡️  SECUREWATCH AI - LIVE ATTACK SIMULATOR{RESET}")
    print("------------------------------------------------")
    
    while True:
        print("\nSelect Attack Vector:")
        print("1. 🟢 Normal Traffic (Valid Users)")
        print("2. 🌍 Impossible Travel (Location Spoofing)")
        print("3. 🤖 Bot Swarm (High Frequency)")
        print("4. 🕸️ Fraud Ring (Device Reuse)")
        print("5. Exit")
        
        choice = input("\nExecute Command [1-5]: ")
        
        if choice == '1':
            print(f"\n{GREEN}>>> Generating Legitimate Traffic...{RESET}")
            for _ in range(5):
                user = random.choice(USERS)
                # Feature[0] = 0.1 triggers "Safe" logic in backend
                send_request(user, [0.1, 0.5, 0.5, 0.5], [[1],[2],[3],[4],[1],[2],[3],[4],[1],[2]], "Normal")
                time.sleep(0.5)

        elif choice == '2':
            print(f"\n{YELLOW}>>> Simulating Impossible Travel...{RESET}")
            # Feature[0] = 100.0 triggers "Impossible Travel" logic
            send_request("traveler_joe", [100.0, 50.0, 10.0, 5.0], [[1]*10], "Geo-Hopping")
            
        elif choice == '3':
            print(f"\n{RED}>>> Launching Bot Swarm...{RESET}")
            for i in range(10):
                # Repetitive sequence triggers "Bot" logic
                send_request(f"bot_{i}", [0.5, 0.5, 0.5, 0.5], [[1],[1],[1],[1],[1],[1],[1],[1],[1],[1]], "Bot Script")
                time.sleep(0.1) # Fast fire
                
        elif choice == '4':
            print(f"\n{RED}>>> Injecting Fraud Ring Identity...{RESET}")
            # user_101 triggers "Fraud Ring" logic
            send_request("user_101", [0.5, 0.5, 0.5, 0.5], [[1],[2],[3]], "Blacklisted ID")
            
        elif choice == '5':
            break

if __name__ == "__main__":
    run_simulation()