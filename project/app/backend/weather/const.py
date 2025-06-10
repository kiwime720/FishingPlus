# ─────────────────────────────────────────────────────────────────────────────
#  KMA API URL 템플릿
# ─────────────────────────────────────────────────────────────────────────────
KMA_URL      = (
    "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/"
    "{}?serviceKey={}&nx={}&ny={}&base_date={}&base_time={}&numOfRows=1000&pageNo=1&dataType=json"
)
KMA_MID_URL  = (
    "http://apis.data.go.kr/1360000/MidFcstInfoService/"
    "{}?serviceKey={}&regId={}&tmFc={}{}&numOfRows=1000&pageNo=1&dataType=json"
)

# ─────────────────────────────────────────────────────────────────────────────
#  CAST 종류 (KMA API 엔드포인트 이름)
# ─────────────────────────────────────────────────────────────────────────────
CAST_R  = "getUltraSrtNcst"   # 초단기 실황
CAST_F  = "getUltraSrtFcst"   # 초단기 예보
CAST_V  = "getVilageFcst"     # 단기(동네) 예보
CAST_ML = "getMidLandFcst"    # 중기 육상 예보
CAST_MT = "getMidTa"          # 중기 기온 예보 (필요하면)
CAST_MS = "getMidSeaFcst"    # 중기 해상 예보

# ─────────────────────────────────────────────────────────────────────────────
#  JSON 파싱에 사용할 Key 이름
# ─────────────────────────────────────────────────────────────────────────────
KEY_RESPONSE  = "response"
KEY_BODY      = "body"
KEY_ITEMS     = "items"
KEY_ITEM_LIST = "item"

ITEM_CATEGORY = "category"
ITEM_FVALUE   = "fcstValue"
ITEM_OVALUE   = "obsrValue"
ITEM_FDATE    = "fcstDate"
ITEM_FTIME    = "fcstTime"
ITEM_BDATE    = "baseDate"
ITEM_BTIME    = "baseTime"

# ─────────────────────────────────────────────────────────────────────────────
#  카테고리 코드 → 내부 필드명 매핑
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_CODE = {
    # 초단기 예보 필드명 매핑
    "T1H": ["temperature"],
    "RN1": ["precipitation"],
    "REH": ["humidity"],
    "PTY": ["precipitation_type"],
    "SKY": ["sky"],
    "WSD": ["wind_speed"],
    "VEC": ["wind_bearing"],

    # 단기 예보 필드명 매핑
    "TMP": ["temperature"],             # 기온
    "SKY": ["sky"],                     # 하늘상태
    "POP": ["precipitation_probability"],  # 강수확률
    "PTY": ["precipitation_type"],      # 강수형태
    "REH": ["humidity"],                # 습도
    "WSD": ["wind_speed"],              # 풍속

    # 중기 예보 필드명 매핑
    "rnSt4Am": ["precipitation_probability_4_am"],
    "rnSt4Pm": ["precipitation_probability_4_pm"],
    "rnSt5Am": ["precipitation_probability_5_am"],
    "rnSt5Pm": ["precipitation_probability_5_pm"],
    "rnSt6Am": ["precipitation_probability_6_am"],
    "rnSt6Pm": ["precipitation_probability_6_pm"],
    "rnSt7Am": ["precipitation_probability_7_am"],
    "rnSt7Pm": ["precipitation_probability_7_pm"],
    "rnSt8":   ["precipitation_probability_8"],
    "rnSt9":   ["precipitation_probability_9"],
    "rnSt10":  ["precipitation_probability_10"],

    "wf4Am": ["sky_4_am"],
    "wf4Pm": ["sky_4_pm"],
    "wf5Am": ["sky_5_am"],
    "wf5Pm": ["sky_5_pm"],
    "wf6Am": ["sky_6_am"],
    "wf6Pm": ["sky_6_pm"],
    "wf7Am": ["sky_7_am"],
    "wf7Pm": ["sky_7_pm"],

    "taMin4":     ["temperature_min_4"],
    "taMin4Low":  ["temperature_min_4_low"],
    "taMin4High": ["temperature_min_4_high"],
    "taMax4":     ["temperature_max_4"],
    "taMax4Low":  ["temperature_max_4_low"],
    "taMax4High": ["temperature_max_4_high"],

    "taMin5":     ["temperature_min_5"],
    "taMin5Low":  ["temperature_min_5_low"],
    "taMin5High": ["temperature_min_5_high"],
    "taMax5":     ["temperature_max_5"],
    "taMax5Low":  ["temperature_max_5_low"],
    "taMax5High": ["temperature_max_5_high"],

    "taMin6":     ["temperature_min_6"],
    "taMin6Low":  ["temperature_min_6_low"],
    "taMin6High": ["temperature_min_6_high"],
    "taMax6":     ["temperature_max_6"],
    "taMax6Low":  ["temperature_max_6_low"],
    "taMax6High": ["temperature_max_6_high"],

    "taMin7":     ["temperature_min_7"],
    "taMin7Low":  ["temperature_min_7_low"],
    "taMin7High": ["temperature_min_7_high"],
    "taMax7":     ["temperature_max_7"],
    "taMax7Low":  ["temperature_max_7_low"],
    "taMax7High": ["temperature_max_7_high"],

    "WF4AM": ["wf4Am"],
    "WF4PM": ["wf4Pm"],
    "WF5AM": ["Wf5AM"],
    "WF5PM": ["wf5Pm"],
    "WF6AM": ["wf6Am"],
    "WF6PM": ["wf6Pm"],
    "WF7AM": ["wf7Am"],
    "WF7PM": ["wf7Pm"],

    "WH4AAM": ["wh4AAm"],
    "WH4APM": ["wh4APm"],
    "WH4BAM": ["wh4BAm"],
    "WH4BPM": ["wh4BPm"],
    "WH5AAM": ["Wh5AAm"],
    "WH5APM": ["Wh5APm"],
    "WH5BAM": ["Wh5BAm"],
    "WH5BPM": ["Wh5BPm"],
    "WH6AAM": ["wh6AAm"],
    "WH6APM": ["wh6APm"],
    "WH6BAM": ["wh6BAm"],
    "WH6BPM": ["wh6BPm"],
    "WH7AAM": ["wh7AAm"],
    "WH7APM": ["wh7APm"],
    "WH7BAM": ["wh7BAm"],
    "WH7BPM": ["wh7BPm"]
}
