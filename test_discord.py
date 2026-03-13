#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real data is used to test Discord notifications.
API data is fetched and all items are sent as "added" events.
Since this will send real notifications to the Discord Webhook, be cautious when running on production channels.
"""

import sys
import time

from api import fetch_arrivals, fetch_departures, fetch_status_map
from config import DISCORD_WEBHOOK_URL, MODE, TARGET_AIRPORT_CODE
from discord_notifier import format_embed, post_discord
from state import normalize
from utils import airport_code_from_odpt_id


# Discord allows up to 10 embeds per request
_BATCH_SIZE = 10


def _fmt_item(item: dict) -> str:
    """Single-line summary of a flight item for console output."""
    kind_label = "到着" if item["kind"] == "arrival" else "出発"
    fn = item.get("operating_flight_number") or item.get("flight_number", "-")
    cs = item.get("codeshare_numbers")
    fn_display = f"{fn} ({cs})" if cs else fn

    other = airport_code_from_odpt_id(item.get("other_airport"))
    route = f"{other}"


    scheduled = item.get("scheduled") or "-"
    status = item.get("status") or "-"
    return f"[{kind_label}]  {fn_display:<18}  {route:<30}  {scheduled}  {status}"


def _fetch_items(status_map: dict) -> list:
    items = []

    if MODE in ("arrivals", "both"):
        try:
            arrivals = fetch_arrivals()
            print(f"Fetched {len(arrivals)} arrival(s)")
            for row in arrivals:
                items.append(normalize("arrival", row, status_map))
        except Exception as e:
            print(f"Error fetching arrivals: {e}", file=sys.stderr)

    if MODE in ("departures", "both"):
        try:
            departures = fetch_departures()
            print(f"Fetched {len(departures)} departure(s)")
            for row in departures:
                items.append(normalize("departure", row, status_map))
        except Exception as e:
            print(f"Error fetching departures: {e}", file=sys.stderr)

    # Sort by kind then scheduled time (missing scheduled → end of list)
    items.sort(key=lambda x: (x.get("kind", ""), x.get("scheduled") or "99:99"))
    return items


def test_discord_live() -> int:
    print("Testing Discord webhook with LIVE data...")

    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set.", file=sys.stderr)
        return 1

    print(f"Target Airport : {TARGET_AIRPORT_CODE}")
    print(f"Mode           : {MODE}")

    # ── 1. Fetch live data from ODPT API ─────────────────────────────────
    try:
        status_map = fetch_status_map()
    except Exception as e:
        print(f"Error fetching flight status map: {e}", file=sys.stderr)
        return 1

    items = _fetch_items(status_map)

    if not items:
        print("No flight data available right now.")
        return 0

    print(f"\nTotal flights to send: {len(items)}")
    print("-" * 70)
    for item in items:
        print(_fmt_item(item))
    print("-" * 70)

    # ── 2. Build embeds and post to Discord ───────────────────────────────
    sent = 0
    errors = 0

    for i in range(0, len(items), _BATCH_SIZE):
        batch = items[i : i + _BATCH_SIZE]
        embeds = []
        for item in batch:
            embed = format_embed("added", item, None)
            embed["title"] = "[TEST] " + embed["title"]
            embeds.append(embed)

        try:
            post_discord(embeds)
            sent += len(batch)
            print(f"Sent batch {i // _BATCH_SIZE + 1} ({len(batch)} embed(s)).")
        except Exception as e:
            print(f"Error sending batch: {e}", file=sys.stderr)
            errors += 1

        # Rate-limit guard between batches
        if i + _BATCH_SIZE < len(items):
            time.sleep(0.5)

    print(f"\nDone. Sent {sent} notification(s), {errors} error(s).")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(test_discord_live())
