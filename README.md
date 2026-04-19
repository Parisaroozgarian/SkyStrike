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
