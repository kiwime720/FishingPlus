import re
from datetime import datetime, timedelta

from weather.const import (
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

def parse_mid_land(raw_json: dict) -> dict[str, dict]:
    items = _extract_items_list(raw_json)
    if not isinstance(items, list) or len(items) == 0:
        return {}

    day_data = items[0]
    result: dict[str, dict] = {}

    # 중기 예보의 “기준일”은 외부에서 제공되지 않으므로,
    # parser 입장에서는 오늘 날짜를 기준으로 day_offset 계산
    base_date = datetime.now().date()

    for key_code, raw_val in day_data.items():
        m = re.match(r"([a-zA-Z]+)(\d+)(?:Am|Pm)?", key_code)
        if not m:
            continue
        cat_part, day_offset = m.groups()

        # 중기에서 taMin → TMN, taMax → TMX, sky→ SKY, rnSt→ POP 등으로 매핑
        cat_upper = cat_part.upper()
        if cat_upper.startswith("TAMIN"):
            code = "TMN"
        elif cat_upper.startswith("TAMAX"):
            code = "TMX"
        elif cat_upper.startswith("SKY"):
            code = "SKY"
        elif cat_upper.startswith("RNST"):
            code = "POP"
        else:
            code = cat_upper  # 필요에 따라 추가 mapping

        if code not in CATEGORY_CODE:
            continue

        offset = int(day_offset)
        target_date = base_date + timedelta(days=offset)
        date_str = target_date.strftime("%Y%m%d")

        field_name = CATEGORY_CODE[code][0]
        try:
            if raw_val is None or raw_val == "" or raw_val == "-":
                val = None
            elif isinstance(raw_val, str) and raw_val.isdigit():
                val = int(raw_val)
            else:
                val = float(raw_val)
        except:
            val = raw_val

        if date_str not in result:
            result[date_str] = {}
        result[date_str][field_name] = val

    return result
