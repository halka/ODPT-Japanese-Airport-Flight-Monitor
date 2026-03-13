#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from datetime import datetime, timezone

import requests

from config import MODE, POLL_INTERVAL_SEC, STARTUP_LOGO_URL, STARTUP_NOTICE, STATE_FILE, TARGET_AIRPORT_CODE
from diff import diff_states
from discord_notifier import format_embed, post_discord
from state import build_current_state, load_state, save_state, archive_state_snapshot


class ISO8601Formatter(logging.Formatter):
    """Logging formatter that emits UTC ISO8601 timestamps with trailing Z."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _setup_logging() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    handler.setFormatter(ISO8601Formatter(fmt))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def _post_startup_notice(run_forever: bool) -> None:
    """Send a one-time startup message to Discord (best-effort)."""
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    embed = {
        "title": "Airport Monitor started",
        "description": f"Monitoring airport {TARGET_AIRPORT_CODE}",
        "color": 0x2ECC71,  # green
        "fields": [
            {"name": "Mode", "value": MODE, "inline": True},
            {"name": "Interval", "value": f"{POLL_INTERVAL_SEC}s", "inline": True},
            {"name": "Run mode", "value": "daemon" if run_forever else "one-shot", "inline": True},
            {"name": "State file", "value": str(STATE_FILE), "inline": False},
        ],
        "footer": {"text": f"Started at {ts}"},
    }
    if STARTUP_LOGO_URL:
        embed["thumbnail"] = {"url": STARTUP_LOGO_URL}
    try:
        post_discord([embed])
    except Exception as e:
        logging.warning("Failed to post startup notice: %s", e)


def run_once() -> int:
    current = build_current_state()
    previous = load_state()

    if not previous:
        save_state(current)
        # Archive on first run
        try:
            archive_state_snapshot(current)
        except Exception:
            logging.exception("Failed to archive initial state snapshot")
        logging.info(
            "Initialized state for %s. No notification sent on first run.",
            TARGET_AIRPORT_CODE,
        )
        return 0

    events = diff_states(previous, current)
    if not events:
        save_state(current)
        logging.info("No changes for %s.", TARGET_AIRPORT_CODE)
        return 0

    for event_type, item, old_item in events:
        embed = format_embed(event_type, item, old_item)
        post_discord([embed])
        time.sleep(0.4)

    save_state(current)
    # Archive snapshot only when there were changes
    try:
        archive_state_snapshot(current)
    except Exception:
        logging.exception("Failed to archive state snapshot after change")
    logging.info("Sent %d notification(s) for %s.", len(events), TARGET_AIRPORT_CODE)
    return 0


def main() -> int:
    _setup_logging()
    run_forever = os.getenv("RUN_FOREVER", "1") == "1"

    # Optionally post a startup notice once per process start
    if STARTUP_NOTICE:
        _post_startup_notice(run_forever)

    if not run_forever:
        return run_once()

    logging.info(
        "Starting monitor for %s (mode=%s, interval=%ss, state=%s)",
        TARGET_AIRPORT_CODE,
        MODE,
        POLL_INTERVAL_SEC,
        STATE_FILE,
    )

    while True:
        try:
            run_once()
        except requests.HTTPError:
            logging.exception("HTTP error during polling")
        except Exception:
            logging.exception("Unexpected error during polling")

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    raise SystemExit(main())
