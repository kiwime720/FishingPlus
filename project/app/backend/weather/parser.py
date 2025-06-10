import re
from datetime import datetime, timedelta

from .const import (
    ITEM_CATEGORY,
    ITEM_FVALUE,
    ITEM_OVALUE,
    ITEM_FDATE,
    ITEM_FTIME,
    KEY_RESPONSE,
    KEY_BODY,
    KEY_ITEMS,
    KEY_ITEM_LIST,
    CATEGORY_CODE,
)

def _extract_items_list(raw_json: dict) -> list[dict]:
    return (
        raw_json
        .get(KEY_RESPONSE, {})
        .get(KEY_BODY, {})
        .get(KEY_ITEMS, {})
        .get(KEY_ITEM_LIST, [])
    )

def parse_ultra_short(raw_json: dict) -> dict[str, dict]:
    items = _extract_items_list(raw_json)
    result: dict[str, dict] = {}

    for entry in items:
        fcst_dt = entry.get(ITEM_FDATE, "") + entry.get(ITEM_FTIME, "")
        cat = entry.get(ITEM_CATEGORY, "")
        if cat not in CATEGORY_CODE:
            continue

        field_name = CATEGORY_CODE[cat][0]
        raw_val = entry.get(ITEM_FVALUE) or entry.get(ITEM_OVALUE)
        try:
            if raw_val is None or raw_val == "" or raw_val == "-":
                val = None
            elif isinstance(raw_val, str) and raw_val.isdigit():
                val = int(raw_val)
            else:
                val = float(raw_val)
        except:
            val = raw_val

        if fcst_dt not in result:
            result[fcst_dt] = {}
        result[fcst_dt][field_name] = val

    return result

def parse_short_term(raw_json: dict) -> dict[str, dict]:
    return parse_ultra_short(raw_json)

def _parse_mid_common(raw_json: dict) -> dict[str, dict]:
    """Parse mid-term forecast data shared by land/temperature/sea APIs."""
    items = _extract_items_list(raw_json)
    if not isinstance(items, list) or len(items) == 0:
        return {}

    day_data = items[0]
    result: dict[str, dict] = {}

    base_date = datetime.now().date()

    for key_code, raw_val in day_data.items():
        code_key = key_code if key_code in CATEGORY_CODE else key_code.upper()
        if code_key not in CATEGORY_CODE:
            continue

        m = re.search(r"(\d+)", key_code)
        if not m:
            continue
        offset = int(m.group(1))

        target_date = base_date + timedelta(days=offset)
        date_str = target_date.strftime("%Y%m%d")

        field_name = CATEGORY_CODE[code_key][0]
        try:
            if raw_val is None or raw_val == "" or raw_val == "-":
                val = None
            elif isinstance(raw_val, str) and raw_val.isdigit():
                val = int(raw_val)
            else:
                val = float(raw_val)
        except Exception:
            val = raw_val

        if date_str not in result:
            result[date_str] = {}
        result[date_str][field_name] = val

    return result


def parse_mid_land(raw_json: dict) -> dict[str, dict]:
    return _parse_mid_common(raw_json)


def parse_mid_ta(raw_json: dict) -> dict[str, dict]:
    return _parse_mid_common(raw_json)


def parse_mid_sea(raw_json: dict) -> dict[str, dict]:
    return _parse_mid_common(raw_json)
