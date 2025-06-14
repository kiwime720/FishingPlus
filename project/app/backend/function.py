import math
import requests
from datetime import datetime, timedelta, timezone


# ─────────────────────────────────────────────────────────────────────────────
# 1) WGS84(lat, lon) → KMA 그리드(nx, ny) 변환
#    (여기서 x는 위도, y는 경도)
# ─────────────────────────────────────────────────────────────────────────────

def x_y_to_kma_grid(x: float, y: float) -> (int, int):
    """
    x(위도), y(경도) → KMA 그리드(nx, ny) 변환
    """
    latitude = x
    longitude = y

    RE    = 6371.00877        # 지구 반경 (km)
    GRID  = 5.0               # 격자 간격 (km)
    SLAT1 = 30.0              # 표준위도 1 (deg)
    SLAT2 = 60.0              # 표준위도 2 (deg)
    OLON  = 126.0             # 기준 경도 (deg)
    OLAT  = 38.0              # 기준 위도 (deg)
    XO    = 43                # 기준 격자 X 좌표 (Nx)
    YO    = 136               # 기준 격자 Y 좌표 (Ny)

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon  = OLON  * DEGRAD
    olat  = OLAT  * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    ra = math.tan(math.pi * 0.25 + latitude * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)
    theta = longitude * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    xg = (ra * math.sin(theta)) + XO + 0.5
    yg = (ro - ra * math.cos(theta)) + YO + 0.5

    return int(xg), int(yg)


# ─────────────────────────────────────────────────────────────────────────────
# 2) 기준 시각 계산 함수 (KST)
# ─────────────────────────────────────────────────────────────────────────────

def get_base_datetime_ultra() -> (str, str):
    KST = timezone(timedelta(hours=9))
    now = datetime.now(timezone.utc).astimezone(KST)
    date_str = now.strftime("%Y%m%d")
    time_str = f"{now.hour:02d}00"
    return date_str, time_str

def get_base_datetime_short() -> (str, str):
    KST = timezone(timedelta(hours=9))
    now = datetime.now(timezone.utc).astimezone(KST)
    hhmm = now.hour * 100 + now.minute
    update_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    base_hour = None
    for h in reversed(update_hours):
        if hhmm >= h * 100:
            base_hour = h
            break

    if base_hour is None:
        yesterday = now.date() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d"), "2300"
    else:
        return now.strftime("%Y%m%d"), f"{base_hour:02d}00"

def get_base_datetime_mid() -> (str, str):
    KST = timezone(timedelta(hours=9))
    now = datetime.now(timezone.utc).astimezone(KST)
    hhmm = now.hour * 100 + now.minute

    if hhmm >= 1830:
        return now.strftime("%Y%m%d"), "1800"
    elif hhmm >=  630:
        return now.strftime("%Y%m%d"), "0600"
    else:
        yesterday = now.date() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d"), "1800"


# ─────────────────────────────────────────────────────────────────────────────
# 3) 초단기·단기·중기 예보를 한 번에 가져오는 함수
#    (x=위도, y=경도, reg_id=중기예보용 지역코드)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_weather_all(
    api_key: str,
    x: float,
    y: float,
    reg_id: str
) -> dict:
    """
    • x: 위도 (latitude)
    • y: 경도 (longitude)
    • reg_id: 중기예보용 지역 코드 (예: '11B10101')

    반환 형식:
    {
      "ultra": { "ncst": {...},  "fcst": {...} },
      "short": {...},
      "mid":   { "land": {...}, "ta": {...} }
    }
    """
    # 1) WGS84(x, y) → KMA 그리드(nx, ny)
    nx, ny = x_y_to_kma_grid(x, y)

    result = {}

    # ─────────────────────────────────────────────────────────────────────────
    # 2-1) 초단기 실황/예보
    # ─────────────────────────────────────────────────────────────────────────
    base_date_u, base_time_u = get_base_datetime_ultra()
    common_params = {
        "serviceKey": api_key,
        "nx": nx,
        "ny": ny,
        "base_date": base_date_u,
        "base_time": base_time_u,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
    }

    # 2-1-a) 초단기 실황
    url_ncst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    r_ncst = requests.get(url_ncst, params=common_params, timeout=10)
    r_ncst.raise_for_status()
    result["ultra"] = { "ncst": r_ncst.json() }

    # 2-1-b) 초단기 예보
    url_fcst = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    r_fcst = requests.get(url_fcst, params=common_params, timeout=10)
    r_fcst.raise_for_status()
    result["ultra"]["fcst"] = r_fcst.json()


    # ─────────────────────────────────────────────────────────────────────────
    # 2-2) 단기 예보 (getVilageFcst)
    # ─────────────────────────────────────────────────────────────────────────
    base_date_s, base_time_s = get_base_datetime_short()
    params_short = {
        "serviceKey": api_key,
        "nx": nx,
        "ny": ny,
        "base_date": base_date_s,
        "base_time": base_time_s,
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
    }
    url_short = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    r_short = requests.get(url_short, params=params_short, timeout=10)
    r_short.raise_for_status()
    result["short"] = r_short.json()


    # ─────────────────────────────────────────────────────────────────────────
    # 2-3) 중기 예보 (getMidLandFcst, getMidTa)
    # ─────────────────────────────────────────────────────────────────────────
    base_date_m, base_time_m = get_base_datetime_mid()
    params_mid = {
        "serviceKey": api_key,
        "regId": reg_id,
        "tmFc": f"{base_date_m}{base_time_m}",
        "numOfRows": 1000,
        "pageNo": 1,
        "dataType": "JSON",
    }

    # 2-3-a) 중기 육상 예보
    url_mid_land = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
    r_mid_land = requests.get(url_mid_land, params=params_mid, timeout=10)
    r_mid_land.raise_for_status()
    result["mid"] = { "land": r_mid_land.json() }

    # 2-3-b) 중기 기온 예보
    url_mid_ta = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
    r_mid_ta = requests.get(url_mid_ta, params=params_mid, timeout=10)
    r_mid_ta.raise_for_status()
    result["mid"]["ta"] = r_mid_ta.json()

    # 2-3-c) 중기 해상 예보
    url_mid_sea = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidSeaFcst"
    r_mid_sea = requests.get(url_mid_sea, params=params_mid, timeout=10)
    r_mid_sea.raise_for_status()
    result["mid"]["sea"] = r_mid_sea.json()

    return result

import requests
import xmltodict
from pyproj import Transformer
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# Fish WFS 상수
# ─────────────────────────────────────────────────────────────────────────────
BASE_URL            = "https://www.nie-ecobank.kr/ecoapi/NteeInfoService"
WFS_ENDPOINT        = "/wfs/getFishesPointWFS"

PARAM_SERVICE_KEY   = "serviceKey"
PARAM_TYPE_NAME     = "typeName"
PARAM_BBOX          = "bbox"
PARAM_MAX_FEATURES  = "maxFeatures"

DEFAULT_TYPE_NAME   = "mv_map_ecpe_fishes_point"
DEFAULT_MAX_FEATURES= 10


# ─────────────────────────────────────────────────────────────────────────────
# 2-1) WGS84(x, y) → EPSG:5186 바운딩박스 계산
#     (x=위도, y=경도, radius_km=반경)
# ─────────────────────────────────────────────────────────────────────────────

def bbox_from_x_y_radius(x: float, y: float, radius_km: float) -> str:
    """
    • x: 위도(lat), y: 경도(lon)
    • radius_km: 반경(단위: km)

    반환: EPSG:5186 좌표계의 "miny,minx,maxy,maxx" 문자열
    """
    # 1) WGS84(4326) → EPSG:5186
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True)
    x_5186, y_5186 = transformer.transform(y, x)  # transform(lon, lat)

    # 2) 반경 km → 미터
    r_m = radius_km * 1000.0

    # 3) 바운딩박스 계산
    minx = x_5186 - r_m
    maxx = x_5186 + r_m
    miny = y_5186 - r_m
    maxy = y_5186 + r_m

    # 4) "minx,miny,maxx,maxy" 순서
    return f"{minx},{miny},{maxx},{maxy}"


# ─────────────────────────────────────────────────────────────────────────────
# 2-2) 물고기 점 피처 조회 함수
# ─────────────────────────────────────────────────────────────────────────────

def fetch_fish_by_radius(
    service_key: str,
    x: float,
    y: float,
    radius_km: float,
    type_name: str = DEFAULT_TYPE_NAME,
    max_features: int = DEFAULT_MAX_FEATURES
) -> List[Dict[str, Any]]:
    """
    • x: 위도(lat), y: 경도(lon)
    • radius_km: 반경(km)
    • type_name: 피처 타입명 (기본 mv_map_ecpe_fishes_point)
    • max_features: 최대 개수 (기본 10, 최대 500)

    반환: 파싱된 피처 리스트(딕셔너리 목록)
    """
    # 1) 반경 radius_km → EPSG:5186 bbox
    bbox = bbox_from_x_y_radius(x, y, radius_km)

    # 2) WFS 호출
    url = BASE_URL + WFS_ENDPOINT
    params = {
        PARAM_SERVICE_KEY:  service_key,
        PARAM_TYPE_NAME:    type_name,
        PARAM_BBOX:         bbox,
        PARAM_MAX_FEATURES: max_features,
    }

    # 호출 URL 출력 (디버깅용)
    prepared = requests.Request("GET", url, params=params).prepare()
    print("▶ 호출 URL:", prepared.url)

    resp = requests.get(url, params=params, timeout=10)
    print("▶ HTTP 상태 코드:", resp.status_code)
    resp.raise_for_status()

    raw_xml = resp.text

    # 3) XML 파싱
    try:
        doc = xmltodict.parse(raw_xml)
    except Exception as ex:
        raise RuntimeError(f"WFS XML 파싱 실패: {ex}")

    features: List[Dict[str, Any]] = []
    root = doc.get("wfs:FeatureCollection") or doc.get("FeatureCollection")
    if not root:
        return features

    raw_members = root.get("gml:featureMember") or root.get("featureMember") or []
    if isinstance(raw_members, dict):
        members = [raw_members]
    else:
        members = raw_members

    for member in members:
        key_candidates = [k for k in member.keys() if k.endswith(type_name)]
        if not key_candidates:
            continue
        feature_node = member[key_candidates[0]]
        if not isinstance(feature_node, dict):
            continue

        parsed_feat: Dict[str, Any] = {}
        parsed_feat["spce_id"] = feature_node.get("spce_id")

        # geom (Point 좌표)
        coords = None
        geom_node = feature_node.get("geom") or feature_node.get("gml:Point")
        if geom_node:
            point_node = None
            if isinstance(geom_node, dict) and "gml:Point" in geom_node:
                point_node = geom_node["gml:Point"]
            elif geom_node.get("gml:coordinates"):
                point_node = geom_node
            if point_node:
                text = point_node.get("gml:coordinates") or point_node.get("coordinates")
                if text:
                    xy = text.split(",")
                    try:
                        coords = [float(xy[0]), float(xy[1])]
                    except:
                        coords = None
        parsed_feat["geom"] = {"type": "Point", "coordinates": coords}

        # 기타 속성
        parsed_feat["examin_year"]     = feature_node.get("examin_year")
        parsed_feat["spcs_korean_nm"]  = feature_node.get("spcs_korean_nm")
        parsed_feat["examin_area_nm"]  = feature_node.get("examin_area_nm")
        parsed_feat["examin_begin_de"] = feature_node.get("examin_begin_de")
        parsed_feat["examin_end_de"]   = feature_node.get("examin_end_de")

        features.append(parsed_feat)

    return features
