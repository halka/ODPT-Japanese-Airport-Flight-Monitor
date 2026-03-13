#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import Any, Dict, List, Optional

from config import (
    AIRLINE_MAP,
    AIRPORT_MAP,
    DISCORD_THREAD_ID,
    DISCORD_WEBHOOK_URL,
    HTTP_TIMEOUT_SEC,
    TARGET_AIRPORT_CODE,
    TARGET_AIRPORT_ODPT_ID,
    session,
)
from diff import changed_fields
from utils import airport_code_from_odpt_id, j, terminal_display

# ── Color tables ──────────────────────────────────────────────────────────────
_EVENT_COLORS: Dict[str, int] = {
    "added":      0x2ECC71,  # Green  — new flight appeared
    "changed":    0x3498DB,  # Blue   — flight info updated
    "removed":    0xFF0000,  # Red    — flight disappeared
    "ops_update": 0xF39C12,  # Amber  — gate / terminal announced
}
_DEFAULT_COLOR = 0x34495E  # Dark grey

# Status keyword → color (checked in order; first match wins)
_STATUS_COLORS = [
    ("欠航",     0xE74C3C),  # Bright red  — cancelled
    ("遅延",     0xF1C40F),  # Yellow      — delayed
    ("条件付き", 0xE67E22),  # Orange      — conditional
    ("搭乗中",   0x1ABC9C),  # Teal        — boarding
    ("出発済み", 0x95A5A6),  # Grey        — departed
    ("到着済み", 0x95A5A6),  # Grey        — arrived
]


def _pick_color(event_type: str, status: str) -> int:
    for keyword, color in _STATUS_COLORS:
        if keyword in status:
            return color
    return _EVENT_COLORS.get(event_type, _DEFAULT_COLOR)


# ── Grid layout ───────────────────────────────────────────────────────────────
_SPACER: Dict[str, Any] = {"name": "\u200b", "value": "\u200b", "inline": True}


def _pad_to_grid(fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pad inline-field rows with spacers so each row has exactly 3 columns."""
    result: List[Dict[str, Any]] = []
    inline_count = 0
    for field in fields:
        if field.get("inline"):
            result.append(field)
            inline_count += 1
        else:
            # flush current row before a full-width field
            while inline_count % 3:
                result.append(_SPACER)
                inline_count += 1
            result.append(field)
            inline_count = 0
    # flush final row
    while inline_count % 3:
        result.append(_SPACER)
        inline_count += 1
    return result


def format_embed(event_type: str, item: Dict[str, Any], old_item: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    kind_emoji = "\U0001f6ec" if item["kind"] == "arrival" else "\U0001f6eb"
    event_emoji = {"added": "", "changed": "\U0001f504 ", "removed": "\U0001f6ab "}.get(event_type, "")
    description = ""
    # Flight Number ICAO Conversion — use operating_flight_number (title/author only)
    operating = item.get("operating_flight_number") or item.get("flight_number", "-")
    flight_nums = [fn.strip() for fn in operating.split(",") if fn.strip() != "-"]
    icao_flight_nums = []
    for fn in flight_nums:
        converted = fn
        for iata, icao in AIRLINE_MAP.items():
            if fn.startswith(iata):
                converted = converted.replace(iata, icao, 1)
                break
        icao_flight_nums.append(converted)
    display_flight_number = ", ".join(icao_flight_nums) if icao_flight_nums else "-"

    airport_display = airport_code_from_odpt_id(item["other_airport"])

    # Title: kind emoji + destination / origin airport
    title = f"{event_emoji}{kind_emoji} {airport_display}"

    # ゲート/ターミナル確定チェック（null → 値 の遷移）
    ops_announced: List[str] = []
    if event_type == "changed" and old_item is not None:
        for key, label in (
            ("gate",            "搭乗口"),
            ("terminal",        "ターミナル"),
            ("checkin_counter", "チェックインカウンター"),
            ("baggage_claim",   "手荷物受取"),
        ):
            if not old_item.get(key) and item.get(key):
                ops_announced.append(label)
    if ops_announced:
        title = "\U0001f6c2 " + title  # 🛂

    # Fields: FIDS board columns
    fields: List[Dict[str, Any]] = []

    # 定刻
    scheduled_val = j(item["scheduled"])
    fields.append({"name": "\u5b9a\u523b", "value": f"`{scheduled_val}`", "inline": True})

    # 変更 (estimated — only when it differs from scheduled)
    estimated_val = item.get("estimated")
    actual_val = item.get("actual")
    if estimated_val and estimated_val != item.get("scheduled"):
        history = item.get("estimated_history", [])
        if history:
            history_str = " \u2192 ".join(history) + f" \u2192 **{estimated_val}**"
            fields.append({"name": "\U0001f504 \u5909\u66f4", "value": history_str, "inline": True})
        else:
            fields.append({"name": "\U0001f504 \u5909\u66f4", "value": f"**{estimated_val}**", "inline": True})
    elif actual_val and actual_val != item.get("scheduled"):
        fields.append({"name": "\u5b9f\u7e3e", "value": f"`{actual_val}`", "inline": True})

    # 備考 (status / remarks)
    fields.append({"name": "\u5099\u8003", "value": j(item["status"]), "inline": True})

    # ターミナル
    terminal_val = item.get("terminal")
    if terminal_val and terminal_val != "-":
        fields.append({"name": "ターミナル", "value": terminal_display(terminal_val), "inline": True})

    # 搭乗口 / ゲート
    gate_val = item.get("gate")
    if gate_val and gate_val != "-":
        fields.append({"name": "\u642d\u4e57\u53e3", "value": gate_val, "inline": True})

    # コードシェア便
    codeshare = item.get("codeshare_numbers")
    if codeshare:
        fields.append({"name": "コードシェア", "value": codeshare, "inline": True})

    # チェックインカウンター (出発便)
    checkin = item.get("checkin_counter")
    if checkin and checkin != "-":
        fields.append({"name": "チェックインカウンター", "value": checkin, "inline": True})

    # 手荷物受取 (到着便)
    baggage = item.get("baggage_claim")
    if baggage and baggage != "-":
        fields.append({"name": "\U0001f9f3 手荷物受取", "value": baggage, "inline": True})

    # 機材
    if item.get("aircraft_type"):
        fields.append({"name": "\u6a5f\u6750", "value": item["aircraft_type"], "inline": True})

    # お知らせ (full-width, only when present)
    info = item.get("info_summary") or item.get("info_text")
    if info:
        fields.append({"name": "\U0001f4e2 \u304a\u77e5\u3089\u305b", "value": info, "inline": False})

    # Change diff (changed events only)
    if event_type == "changed" and old_item is not None:
        delta = changed_fields(old_item, item)
        if delta:
            fields.append({
                "name": "\U0001f504 \u5909\u66f4\u5185\u5bb9",
                "value": "\n".join(delta),
                "inline": False,
            })

    # Metadata for links / logos
    url = None
    logo_url = None
    operating = item.get("operating_flight_number") or item.get("flight_number", "-")
    if operating != "-":
        first_fn = operating.split(",")[0].strip().replace(" ", "")
        first_icao = icao_flight_nums[0] if icao_flight_nums else first_fn
        url = f"https://www.flightaware.com/live/flight/{first_icao}"
        iata = first_fn[:2].upper()
        if iata:
            logo_url = f"https://www.gstatic.com/flights/airline_logos/70px/{iata}.png"

    embed_color = _pick_color(
        "ops_update" if ops_announced else event_type,
        str(item.get("status", "")),
    )
    fields = _pad_to_grid(fields)

    footer_parts = [f"Issued: {j(item.get('generated_at'))}\nValid: {item.get('valid_until', '-')}\n{item.get('fingerprint', '-')}"]

    # Author: logo + flight number (with FlightAware link) — shown whenever a flight number exists
    author = None
    if display_flight_number != "-":
        author = {"name": display_flight_number, "url": url}
        if logo_url:
            author["icon_url"] = logo_url

    embed = {
        "title": title,
        "description": description,
        "url": url,
        "color": embed_color,
        "fields": fields,
        "author": author,
        "footer": {"text": " | ".join(footer_parts)},
    }

    return embed

def post_discord(embeds: List[Dict[str, Any]]) -> None:
    params: Dict[str, Any] = {"wait": "true"}
    if DISCORD_THREAD_ID:
        params["thread_id"] = DISCORD_THREAD_ID

    # Use ICAO for monitor name
    airport_display = TARGET_AIRPORT_CODE
    info = AIRPORT_MAP.get(TARGET_AIRPORT_CODE)
    if info and info.get("icao"):
        airport_display = info["icao"]

    payload = {
        "username": f"{airport_display} Flight Monitor",
        "embeds": embeds,
        "allowed_mentions": {"parse": []},
    }

    for _ in range(3):
        resp = session.post(
            DISCORD_WEBHOOK_URL,
            params=params,
            json=payload,
            timeout=HTTP_TIMEOUT_SEC,
        )

        if resp.status_code != 429:
            resp.raise_for_status()
            return

        retry_after = 1.0
        try:
            body = resp.json()
            retry_after = float(body.get("retry_after", retry_after))
        except Exception:
            pass

        header_retry = resp.headers.get("X-RateLimit-Reset-After") or resp.headers.get("Retry-After")
        if header_retry:
            try:
                retry_after = max(retry_after, float(header_retry))
            except ValueError:
                pass

        time.sleep(retry_after)

    raise RuntimeError("Discord webhook rate-limited too many times")
