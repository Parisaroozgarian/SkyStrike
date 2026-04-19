bashcat > README.md << 'EOF'
# SkyStrike ✈️

A professional aviation cybersecurity threat simulation platform built for studying and demonstrating real-world cyber attack vectors on aircraft systems.

## Overview

SkyStrike simulates cyber attacks on aviation systems including ADS-B transponders, flight control systems, and communications — and demonstrates how defense systems detect and respond to them in real time.

## Features

- **Fleet Management** — Monitor multiple aircraft simultaneously
- **Attack Simulation** — GPS spoofing, ADS-B manipulation, MITM attacks, control freezing, message injection
- **Defense Systems** — Intrusion detection, data validation, encryption monitoring
- **Threat Intelligence Feed** — Real-time log of all attack and defense events
- **Analytics Dashboard** — Fleet-wide uptime, threat levels, system availability

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Architecture:** REST API with real-time polling

## Getting Started

### Prerequisites
- Python 3.11+

### Installation

```bash
git clone https://github.com/Parisaroozgarian/SkyStrike.git
cd SkyStrike
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-sqlalchemy gunicorn psycopg2-binary email-validator
python main.py
```

Then open your browser and navigate to the local development URL shown in your terminal.

## Architecture

### How it works

**1. Browser (top layer)**
Flask serves `index_professional.html` on startup. The page loads the CSS for styling and `simulator_professional.js` which runs in the background — every 2 seconds it calls the API to refresh the dashboard with live data.

**2. Flask app — `app_professional.py`**
The heart of the server. It starts up, registers all the routes, adds security headers to every response, and manages your session (which aircraft you're currently viewing).

**3. API routes — `api/routes.py`**
Every button click in the UI sends an HTTP request here. For example, clicking "GPS Spoof" sends a POST to `/api/simulate_attack`. The routes validate the input, then call the right service.

**4. Services — business logic**
- `attack_service.py` — modifies aircraft data to simulate attacks (changes GPS coordinates, freezes controls, injects fake messages)
- `defense_service.py` — detects attacks, triggers defense responses, and resets systems
- `validators.py` — ensures no bad data gets through before any action runs

**5. Models — `models.py`**
Holds the `fleet_manager` which keeps 3 aircraft in memory (AAL123, UAL456, DLH789), each with ADS-B, flight control, and communications systems. All services read and write to this.

**6. Logging — `logging_config.py`**
Every action — attacks, defenses, user selections — gets logged here for the audit trail visible in the Threat Intelligence Feed.

### Full flow of a single attack
User clicks "GPS Spoof" button
→ simulator.js sends POST /api/simulate_attack
→ routes.py validates the request
→ attack_service.py modifies aircraft GPS data in models.py
→ threat log entry created
→ defense_service.py auto-responds
→ JSON sent back to browser
→ dashboard updates live

## Project Structure
SkyStrike/
├── api/              # REST API routes
├── services/         # Attack and defense logic
├── static/           # CSS and JavaScript
├── templates/        # HTML pages
├── utils/            # Validators and logging
├── models.py         # Data models
├── config.py         # App configuration
└── main.py           # Entry point

## Attack Vectors Simulated

| System | Attack Types |
|--------|-------------|
| ADS-B Transponder | GPS Spoof, Altitude Spoof, MITM, Replay |
| Flight Control | Jam, Freeze, MITM, Replay |
| Communications | Message Injection, Jamming, MITM, Replay |

## License

MIT License
EOF