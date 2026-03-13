#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional, Tuple

from config import NOTIFY_REMOVED
from utils import airport_code_from_odpt_id, j, terminal_display


def diff_states(
    old: Dict[str, Any], new: Dict[str, Any]
) -> List[Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]]:
    old_items = old.get("items", {})
    new_items = new.get("items", {})

    events: List[Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]] = []

    for item_id, new_item in new_items.items():
        old_item = old_items.get(item_id)
        if not old_item:
            events.append(("added", new_item, None))
        else:
            # Preserve estimated_history from old_item as the baseline
            history = old_item.get("estimated_history", [])

            # If the estimate changed, record the old estimate in the history
            old_est = old_item.get("estimated")
            new_est = new_item.get("estimated")

            if old_est and old_est != new_est:
                if not history or history[-1] != old_est:
                    history.append(old_est)

            new_item["estimated_history"] = history

            if old_item.get("fingerprint") != new_item.get("fingerprint"):
                events.append(("changed", new_item, old_item))

    if NOTIFY_REMOVED:
        for item_id, old_item in old_items.items():
            if item_id not in new_items:
                events.append(("removed", old_item, None))

    events.sort(key=lambda ev: (ev[1].get("kind", ""), ev[1].get("flight_number", "")))
    return events


def changed_fields(old_item: Dict[str, Any], new_item: Dict[str, Any]) -> List[str]:
    labels = {
        "status": "状態",
        "scheduled": "定刻",
        "estimated": "予想",
        "actual": "実績",
        "gate": "ゲート",
        "terminal": "ターミナル",
        "other_airport": "出発地" if new_item.get("kind") == "arrival" else "目的地",
        "aircraft_type": "機材",
        "checkin_counter": "チェックインカウンター",
        "baggage_claim": "手荷物受取",
        "codeshare_numbers": "コードシェア",
        "info_summary": "お知らせ",
    }

    out = []
    for key, label in labels.items():
        if old_item.get(key) != new_item.get(key):
            old_val = old_item.get(key)
            new_val = new_item.get(key)

            if key == "other_airport":
                old_val = airport_code_from_odpt_id(old_val)
                new_val = airport_code_from_odpt_id(new_val)
            elif key == "terminal":
                old_val = terminal_display(old_val)
                new_val = terminal_display(new_val)

            jv_old = j(old_val)
            jv_new = j(new_val)
            if jv_old == "-":
                out.append(f"**{label}**: **{jv_new}**")
            elif key == "estimated":
                history = new_item.get("estimated_history", [])
                if history:
                    history_str = " ➔ ".join(history)
                    out.append(f"**{label}**: ~~{history_str}~~ ➔ **{jv_new}**")
                else:
                    out.append(f"**{label}**: ~~{jv_old}~~ ➔ **{jv_new}**")
            else:
                out.append(f"**{label}**: ~~{jv_old}~~ ➔ **{jv_new}**")
    return out
