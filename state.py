#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import json
import time
from typing import Any, Dict, Optional

from api import fetch_arrivals, fetch_departures, fetch_status_map
from config import MODE, STATE_FILE, TARGET_AIRPORT_CODE, TARGET_AIRPORT_ODPT_ID
from utils import as_list


def make_fingerprint(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize(kind: str, row: Dict[str, Any], status_map: Dict[str, str]) -> Dict[str, Any]:
    is_arrival = kind == "arrival"

    scheduled_key = "odpt:scheduledArrivalTime" if is_arrival else "odpt:scheduledDepartureTime"
    estimated_key = "odpt:estimatedArrivalTime" if is_arrival else "odpt:estimatedDepartureTime"
    actual_key = "odpt:actualArrivalTime" if is_arrival else "odpt:actualDepartureTime"
    gate_key = "odpt:arrivalGate" if is_arrival else "odpt:departureGate"
    terminal_key = "odpt:arrivalAirportTerminal" if is_arrival else "odpt:departureAirportTerminal"
    other_airport_key = "odpt:originAirport" if is_arrival else "odpt:destinationAirport"

    main_nums = as_list(row.get("odpt:flightNumber"))
    seen_main = set(main_nums)
    shared_nums = [x for x in as_list(row.get("odpt:sharedFlightNumber")) if x not in seen_main]
    status_id = row.get("odpt:flightStatus")

    # odpt:airline -> "odpt.Operator:JAL" -> "JAL"
    # NOTE: odpt:operator is the AIRPORT AUTHORITY (e.g. NAA), NOT the airline — do not use as fallback
    airline_raw = row.get("odpt:airline")
    airline = airline_raw.split(":")[-1] if isinstance(airline_raw, str) else None

    # odpt:flightInformationSummary / odpt:flightInformationText may be a dict {"ja": ..., "en": ...} or a string
    def _extract_text(val: Any) -> Optional[str]:
        if not val:
            return None
        if isinstance(val, dict):
            return val.get("ja") or val.get("en") or None
        return str(val) or None

    # flight_number = operating only (for ID, title, and backward compat)
    all_nums = main_nums or shared_nums
    result = {
        "id": row.get("owl:sameAs") or f"{kind}:{','.join(map(str, all_nums))}",
        "kind": kind,
        "operating_flight_number": ", ".join(str(x) for x in main_nums) if main_nums else "-",
        "codeshare_numbers": ", ".join(str(x) for x in shared_nums) if shared_nums else None,
        "flight_number": ", ".join(str(x) for x in all_nums) if all_nums else "-",
        "status_id": status_id,
        "status": status_map.get(status_id, status_id.split(":")[-1] if isinstance(status_id, str) else "-"),
        "scheduled": row.get(scheduled_key),
        "estimated": row.get(estimated_key),
        "actual": row.get(actual_key),
        "gate": row.get(gate_key),
        "terminal": row.get(terminal_key),
        "other_airport": row.get(other_airport_key),
        "airline": airline,
        "aircraft_type": row.get("odpt:aircraftType"),
        "checkin_counter": row.get("odpt:checkInCounter"),
        "baggage_claim": row.get("odpt:baggageClaim"),
        "info_summary": _extract_text(row.get("odpt:flightInformationSummary")),
        "info_text": _extract_text(row.get("odpt:flightInformationText")),
        "generated_at": row.get("dc:date"),
        "valid_until": row.get("dct:valid"),
    }

    # Ignore freshness-only changes like dc:date / dct:valid when diffing
    result["fingerprint"] = make_fingerprint({
        "operating_flight_number": result["operating_flight_number"],
        "codeshare_numbers": result["codeshare_numbers"],
        "flight_number": result["flight_number"],
        "status_id": result["status_id"],
        "scheduled": result["scheduled"],
        "estimated": result["estimated"],
        "actual": result["actual"],
        "gate": result["gate"],
        "terminal": result["terminal"],
        "other_airport": result["other_airport"],
        "aircraft_type": result["aircraft_type"],
        "checkin_counter": result["checkin_counter"],
        "baggage_claim": result["baggage_claim"],
        "info_summary": result["info_summary"],
        "estimated_history": [],
    })
    return result


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp.replace(STATE_FILE)


def build_current_state() -> Dict[str, Any]:
    status_map = fetch_status_map()

    items: Dict[str, Dict[str, Any]] = {}
    if MODE in ("arrivals", "both"):
        for row in fetch_arrivals():
            item = normalize("arrival", row, status_map)
            items[item["id"]] = item

    if MODE in ("departures", "both"):
        for row in fetch_departures():
            item = normalize("departure", row, status_map)
            items[item["id"]] = item

    return {
        "target_airport_code": TARGET_AIRPORT_CODE,
        "target_airport_odpt_id": TARGET_AIRPORT_ODPT_ID,
        "mode": MODE,
        "items": items,
        "saved_at_epoch": int(time.time()),
    }
