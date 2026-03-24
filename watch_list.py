#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from threading import Lock

_WATCH_FILE = Path("data/watch_list.json")
_lock = Lock()


def _load() -> set[str]:
    if not _WATCH_FILE.exists():
        return set()
    with _WATCH_FILE.open("r", encoding="utf-8") as f:
        return set(json.load(f).get("flights", []))


def _save(flights: set[str]) -> None:
    _WATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = _WATCH_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump({"flights": sorted(flights)}, f, ensure_ascii=False)
    tmp.replace(_WATCH_FILE)


def get() -> set[str]:
    with _lock:
        return _load()


def add(flight: str) -> bool:
    """Add a flight number. Returns True if newly added, False if already present."""
    with _lock:
        flights = _load()
        if flight in flights:
            return False
        flights.add(flight)
        _save(flights)
        return True


def remove(flight: str) -> bool:
    """Remove a flight number. Returns True if removed, False if not found."""
    with _lock:
        flights = _load()
        if flight not in flights:
            return False
        flights.discard(flight)
        _save(flights)
        return True
