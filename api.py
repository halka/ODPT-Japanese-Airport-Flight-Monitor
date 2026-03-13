#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional

from config import (
    HTTP_TIMEOUT_SEC,
    ODPT_BASE_URL,
    ODPT_CONSUMER_KEY,
    TARGET_AIRPORT_ODPT_ID,
    session,
)


def odpt_get(resource: str, extra_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    params = {"acl:consumerKey": ODPT_CONSUMER_KEY}
    if extra_params:
        params.update(extra_params)

    url = f"{ODPT_BASE_URL}/{resource}"
    resp = session.get(url, params=params, timeout=HTTP_TIMEOUT_SEC)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response for {resource}: {type(data)}")
    return data


def fetch_status_map() -> Dict[str, str]:
    rows = odpt_get("odpt:FlightStatus")
    result: Dict[str, str] = {}

    for row in rows:
        key = row.get("owl:sameAs")
        if not key:
            continue

        title = None
        for candidate_key in ("odpt:flightStatusTitle", "dc:title"):
            candidate = row.get(candidate_key)
            if isinstance(candidate, dict):
                title = candidate.get("ja") or candidate.get("en")
            elif isinstance(candidate, str) and candidate:
                title = candidate
            if title:
                break

        result[key] = title or key.split(":")[-1]

    return result


def fetch_arrivals() -> List[Dict[str, Any]]:
    return odpt_get(
        "odpt:FlightInformationArrival",
        {"odpt:arrivalAirport": TARGET_AIRPORT_ODPT_ID},
    )


def fetch_departures() -> List[Dict[str, Any]]:
    return odpt_get(
        "odpt:FlightInformationDeparture",
        {"odpt:departureAirport": TARGET_AIRPORT_ODPT_ID},
    )
