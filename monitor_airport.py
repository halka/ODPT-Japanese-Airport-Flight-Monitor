#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

import requests

from config import MODE, POLL_INTERVAL_SEC, STATE_FILE, TARGET_AIRPORT_CODE
from diff import diff_states
from discord_notifier import format_embed, post_discord
from state import build_current_state, load_state, save_state


def run_once() -> int:
    current = build_current_state()
    previous = load_state()

    if not previous:
        save_state(current)
        print(f"Initialized state for {TARGET_AIRPORT_CODE}. No notification sent on first run.")
        return 0

    events = diff_states(previous, current)
    if not events:
        save_state(current)
        print(f"No changes for {TARGET_AIRPORT_CODE}.")
        return 0

    for event_type, item, old_item in events:
        embed = format_embed(event_type, item, old_item)
        post_discord([embed])
        time.sleep(0.4)

    save_state(current)
    print(f"Sent {len(events)} notification(s) for {TARGET_AIRPORT_CODE}.")
    return 0


def main() -> int:
    run_forever = os.getenv("RUN_FOREVER", "1") == "1"

    if not run_forever:
        return run_once()

    print(
        f"Starting monitor for {TARGET_AIRPORT_CODE} "
        f"(mode={MODE}, interval={POLL_INTERVAL_SEC}s, state={STATE_FILE})"
    )

    while True:
        try:
            run_once()
        except requests.HTTPError as e:
            print(f"HTTP error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    raise SystemExit(main())
