#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ODPT_BASE_URL = os.getenv("ODPT_BASE_URL", "https://api.odpt.org/api/v4")
ODPT_CONSUMER_KEY = os.environ["ODPT_CONSUMER_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# 3-letter IATA airport code only. Example: HKD
AIRPORT = os.getenv("AIRPORT", "HKD").strip().upper()

# arrivals / departures / both
MODE = os.getenv("MODE", "both").strip().lower()

# Set to 1 to notify when a flight disappears from the feed
NOTIFY_REMOVED = os.getenv("NOTIFY_REMOVED", "0") == "1"

# Number of columns for Discord alert embeds (1-10)
DISCORD_ALERT_COLUMN_NUM = int(os.getenv("DISCORD_ALERT_COLUMN_NUM", "3"))

# Optional for Forum / Media channel thread posting
DISCORD_THREAD_ID = os.getenv("DISCORD_THREAD_ID", "").strip()

STATE_FILE = Path(os.getenv("STATE_FILE", f"data/state_{AIRPORT.lower()}.json"))
HTTP_TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "180"))

# Load airline mapping from external JSON
AIRLINE_MAPPING_FILE = Path(__file__).parent / "airline_mapping.json"
AIRLINE_MAP = {}
if AIRLINE_MAPPING_FILE.exists():
    try:
        with AIRLINE_MAPPING_FILE.open("r", encoding="utf-8") as f:
            AIRLINE_MAP = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load airline mapping: {e}", file=sys.stderr)

# Load airport mapping from external JSON
AIRPORT_MAPPING_FILE = Path(__file__).parent / "airport_mapping.json"
AIRPORT_MAP = {}
if AIRPORT_MAPPING_FILE.exists():
    try:
        with AIRPORT_MAPPING_FILE.open("r", encoding="utf-8") as f:
            AIRPORT_MAP = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load airport mapping: {e}", file=sys.stderr)

session = requests.Session()
session.headers.update({
    "User-Agent": "airport-flight-monitor/1.2"
})


def validate_airport_code(code: str) -> str:
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise ValueError(f"AIRPORT must be exactly 3 uppercase letters, got: {code!r}")
    return code


def airport_odpt_id(code: str) -> str:
    return f"odpt.Airport:{validate_airport_code(code)}"


TARGET_AIRPORT_CODE = validate_airport_code(AIRPORT)
TARGET_AIRPORT_ODPT_ID = airport_odpt_id(TARGET_AIRPORT_CODE)
