# Login Simulator

This tool simulates various login scenarios to test the `Secure Watch AI` backend.

## Requirements

- Python 3.x
- `requests` library

```bash
pip install requests
```

## Usage

Run the script from the root directory or inside `tools/`:

```bash
python tools/login_simulator.py --mode <MODE> [OPTIONS]
```

### Modes

#### 1. Normal
Simulates valid, random user logins.

```bash
# Send 10 normal login requests
python tools/login_simulator.py --mode normal --count 10
```

#### 2. Impossible Travel
Simulates a user logging in from two distant locations (e.g., NY and Tokyo) in rapid succession.

```bash
# Simulate for a random user
python tools/login_simulator.py --mode impossible_travel

# Simulate for a specific user
python tools/login_simulator.py --mode impossible_travel --user alice
```

#### 3. Bot Script
Simulates a brute-force or high-frequency login attempt by a single user rotating IPs.

```bash
# Send 20 requests for user 'alice'
python tools/login_simulator.py --mode bot_script --user alice --rate 20
```

#### 4. Fraud Ring
Simulates multiple different users logging in from the same IP address in a short time window.

```bash
# Simulate 8 users from same IP
python tools/login_simulator.py --mode fraud_ring --group-size 8
```
