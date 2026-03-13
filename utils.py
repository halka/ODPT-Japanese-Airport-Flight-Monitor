#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re as _re
from typing import Any, List

from config import AIRPORT_MAP


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def j(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        return ", ".join(str(x) for x in value) if value else "-"
    return str(value)


def terminal_display(val: Any) -> str:
    """Convert a raw ODPT terminal ID to a short label.

    Examples:
      "odpt.AirportTerminal:NRT.Terminal1" → "T1"
      "odpt.AirportTerminal:HND.Terminal3" → "T3"
      "Terminal2"                          → "T2"
      "domestic"                           → "domestic"
    """
    if not val:
        return "-"
    s = str(val)
    # Strip ODPT ID prefix: "odpt.AirportTerminal:NRT.Terminal1" → "NRT.Terminal1"
    if ":" in s:
        s = s.split(":")[-1]
    # Strip airport prefix: "NRT.Terminal1" → "Terminal1"
    if "." in s:
        s = s.split(".")[-1]
    # "Terminal1" → "T1"
    m = _re.match(r"[Tt]erminal(\w+)$", s)
    if m:
        return f"T{m.group(1)}"
    return s


def airport_code_from_odpt_id(odpt_id: Any) -> str:
    if not odpt_id:
        return "-"
    s = str(odpt_id)
    code = s.split(":")[-1] if ":" in s else s

    info = AIRPORT_MAP.get(code.upper())
    if info:
        icao = info.get("icao")
        title = info.get("title")
        if icao and title:
            return f"{icao} {title}"
        elif icao:
            return icao
        elif title:
            return title

    return code
