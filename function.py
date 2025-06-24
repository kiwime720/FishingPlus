"""
utility module for coordinate conversions, base time calculations,
weather and fish API fetching for Fishing+ application.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any, List

import requests
import xmltodict
from pyproj import Transformer

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
# Earth's radius and grid parameters for KMA conversion
_RE = 6371.00877      # Earth radius (km)
_GRID = 5.0           # Grid spacing (km)
_SLAT1 = 30.0         # Standard latitude 1 (deg)
_SLAT2 = 60.0         # Standard latitude 2 (deg)
_OLON = 126.0         # Reference longitude (deg)
_OLAT = 38.0          # Reference latitude (deg)
_XO = 43              # Reference grid X coordinate
_YO = 136             # Reference grid Y coordinate

# Timezone for KST (UTC+9)
_KST = timezone(timedelta(hours=9))

# KMA API endpoints
_KMA_ULTRA_NCST_URL = (
    "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
)
_KMA_ULTRA_FCST_URL = (
    "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
)
_KMA_SHORT_URL = (
    "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
)
_KMA_MID_LAND_URL = (
    "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
)
_KMA_MID_TA_URL = (
    "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
)

# Fish WFS constants
_FISH_BASE_URL = "https://www.nie-ecobank.kr/ecoapi/NteeInfoService"
_FISH_WFS_ENDPOINT = "/wfs/getFishesPointWFS"

# Default fish WFS parameters
_DEFAULT_FISH_TYPE = "mv_map_ntee_fishes_point"
_DEFAULT_MAX_FEATURES = 10

# Coordinate transformer (WGS84 -> EPSG:5186)
_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1) WGS84(lat, lon) → KMA 그리드(nx, ny) 변환
# ─────────────────────────────────────────────────────────────────────────────
def x_y_to_kma_grid(lat: float, lon: float) -> Tuple[int, int]:
    """
    Convert WGS84 coordinates to KMA grid coordinates.
    :param lat: latitude in degrees
    :param lon: longitude in degrees
    :return: (nx, ny) grid indices
    """
    deg2rad = math.pi / 180.0
    slat1 = _SLAT1 * deg2rad
    slat2 = _SLAT2 * deg2rad
    olon = _OLON * deg2rad
    olat = _OLAT * deg2rad

    re = _RE / _GRID
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / \
         math.log(math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5))
    sf = (math.tan(math.pi * 0.25 + slat1 * 0.5) ** sn * math.cos(slat1)) / sn
    ro = re * sf / (math.tan(math.pi * 0.25 + olat * 0.5) ** sn)

    ra = re * sf / (math.tan(math.pi * 0.25 + lat * deg2rad * 0.5) ** sn)
    theta = (lon * deg2rad - olon) * sn

    xg = ra * math.sin(theta) + _XO + 0.5
    yg = ro - ra * math.cos(theta) + _YO + 0.5

    return int(xg), int(yg)


# ─────────────────────────────────────────────────────────────────────────────
# 2) 기준 시각 계산 함수 (KST)
# ─────────────────────────────────────────────────────────────────────────────
def get_base_datetime_ultra() -> Tuple[str, str]:
    """
    Get base date and time for ultra short-term forecast (every hour)
    """
    now = datetime.now(timezone.utc).astimezone(_KST)
    return now.strftime("%Y%m%d"), f"{now.hour:02d}00"


def get_base_datetime_short() -> Tuple[str, str]:
    """
    Get base date and time for short-term forecast (various fixed hours)
    """
    now = datetime.now(timezone.utc).astimezone(_KST)
    hhmm = now.hour * 100 + now.minute
    update_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    for h in reversed(update_hours):
        if hhmm >= h * 100:
            return now.strftime("%Y%m%d"), f"{h:02d}00"

    # Before first update => use yesterday 23:00
    yesterday = now - timedelta(days=1)
    return yesterday.strftime("%Y%m%d"), "2300"


def get_base_datetime_mid() -> Tuple[str, str]:
    """
    Get base date and time for mid-term forecast (06:00 or 18:00 releases)
    """
    now = datetime.now(timezone.utc).astimezone(_KST)
    hhmm = now.hour * 100 + now.minute

    if hhmm >= 1830:
        return now.strftime("%Y%m%d"), "1800"
    if hhmm >= 630:
        return now.strftime("%Y%m%d"), "0600"

    yesterday = now - timedelta(days=1)
    return yesterday.strftime("%Y%m%d"), "1800"


# ─────────────────────────────────────────────────────────────────────────────
# 3) KMA 예보 전체 조회 함수
# ─────────────────────────────────────────────────────────────────────────────
def fetch_weather_all(
    api_key: str,
    lat: float,
    lon: float,
    reg_id: str = None
) -> Dict[str, Any]:
    """
    Fetch ultra short-term, short-term, and mid-term forecasts.
    :param api_key: KMA API key
    :param lat: latitude
    :param lon: longitude
    :param reg_id: mid-term region ID (optional)
    :return: dict with keys 'ultra', 'short', 'mid'
    """
    nx, ny = x_y_to_kma_grid(lat, lon)
    result: Dict[str, Any] = {}

    # 초단기 실황/예보
    date_u, time_u = get_base_datetime_ultra()
    common_params = dict(
        serviceKey=api_key, nx=nx, ny=ny,
        base_date=date_u, base_time=time_u,
        numOfRows=1000, pageNo=1, dataType="JSON"
    )
    # 실황
    resp = requests.get(_KMA_ULTRA_NCST_URL, params=common_params, timeout=10)
    resp.raise_for_status()
    result['ultra'] = {'ncst': resp.json()}
    # 예보
    resp = requests.get(_KMA_ULTRA_FCST_URL, params=common_params, timeout=10)
    resp.raise_for_status()
    result['ultra']['fcst'] = resp.json()

    # 단기 예보
    date_s, time_s = get_base_datetime_short()
    params_s = {**common_params, 'base_date': date_s, 'base_time': time_s}
    resp = requests.get(_KMA_SHORT_URL, params=params_s, timeout=10)
    resp.raise_for_status()
    result['short'] = resp.json()

    # 중기 예보
    mid: Dict[str, Any] = {}
    if reg_id:
        date_m, time_m = get_base_datetime_mid()
        params_m = dict(
            serviceKey=api_key, regId=reg_id,
            tmFc=f"{date_m}{time_m}", numOfRows=1000,
            pageNo=1, dataType="JSON"
        )
        # 육상
        resp = requests.get(_KMA_MID_LAND_URL, params=params_m, timeout=10)
        resp.raise_for_status()
        mid['land'] = resp.json()
        # 기온
        resp = requests.get(_KMA_MID_TA_URL, params=params_m, timeout=10)
        resp.raise_for_status()
        mid['ta'] = resp.json()
    result['mid'] = mid
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 4) 어류 WFS 피처 조회
# ─────────────────────────────────────────────────────────────────────────────
def bbox_from_x_y_radius(lat: float, lon: float, radius_km: float) -> str:
    """
    Compute bounding box in EPSG:5186 from WGS84 coordinate and radius.
    """
    x5186, y5186 = _TRANSFORMER.transform(lon, lat)
    delta = radius_km * 1000
    minx, maxx = x5186 - delta, x5186 + delta
    miny, maxy = y5186 - delta, y5186 + delta
    return f"{minx},{miny},{maxx},{maxy}"


def fetch_fish_by_radius(
    service_key: str,
    lat: float,
    lon: float,
    radius_km: float,
    type_name: str = _DEFAULT_FISH_TYPE,
    max_features: int = _DEFAULT_MAX_FEATURES
) -> List[Dict[str, Any]]:
    """
    Fetch fish point features via WFS and parse XML to list.
    """
    bbox = bbox_from_x_y_radius(lat, lon, radius_km)
    url = f"{_FISH_BASE_URL}{_FISH_WFS_ENDPOINT}"
    params = {
        'serviceKey': service_key,
        'typeName': type_name,
        'bbox': bbox,
        'maxFeatures': max_features,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    raw_xml = resp.text

    doc = xmltodict.parse(raw_xml)
    members = doc.get('wfs:FeatureCollection', {})
    members = members.get('gml:featureMember', [])
    if isinstance(members, dict):
        members = [members]

    features: List[Dict[str, Any]] = []
    for member in members:
        # Find the feature node by matching the type_name suffix
        node = next((v for k, v in member.items() if k.endswith(type_name)), None)
        if not isinstance(node, dict):
            continue
        feat: Dict[str, Any] = {}
        # Parse coords
        coord_txt = ''
        geom = node.get('gml:Point') or node.get('geom')
        if geom:
            coords = geom.get('gml:coordinates') or geom.get('coordinates')
            coord_txt = coords.get('#text') if isinstance(coords, dict) else coords or ''
        if coord_txt:
            lon_x, lat_y = map(float, coord_txt.split(','))
            feat['geom'] = {'type': 'Point', 'coordinates': [lon_x, lat_y]}

        # Other properties
        for key in ['spce_id', 'examin_year', 'spcs_korean_nm', 'examin_area_nm',
                    'examin_begin_de', 'examin_end_de']:
            feat[key] = node.get(key) or node.get(f'EcoBank:{key}')
        features.append(feat)
    return features
