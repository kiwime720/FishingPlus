# services.py

import os
import requests
import xml.etree.ElementTree as ET
import logging

SERVICE_KEY = os.getenv("FISH_API_KEY")
BASE_URL    = "https://www.nie-ecobank.kr/ecoapi/EcpeInfoService/wfs/getFishesPointWFS"

# 로거 설정 (Flask 디버그 모드라면 콘솔로 바로 찍힙니다)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def fetch_fish_info(bbox: str,
                    type_name: str = "mv_map_ecpe_fishes_point",
                    max_features: int = 100) -> list[dict]:
    params = {
        "serviceKey":  SERVICE_KEY,
        "request":     "GetFeature",
        "service":     "WFS",
        "version":     "2.0.0",
        "typeName":    type_name,
        "bbox":        bbox,
        "maxFeatures": str(max_features),
        "outputFormat":"text/xml; subtype=gml/3.1.1"
    }

    # 1) 요청 URL 로그
    full_url = requests.Request('GET', BASE_URL, params=params).prepare().url
    logger.debug(f"[WFS REQUEST] {full_url}")

    resp = requests.get(BASE_URL, params=params, timeout=10)
    # 2) 상태 코드 로그
    logger.debug(f"[WFS RESPONSE STATUS] {resp.status_code}")
    # 3) 원본 XML 로그 (처음 500자만)
    logger.debug(f"[WFS RAW XML]\n{resp.text[:500]}")

    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    # 4) featureMember 개수 로그
    members = root.findall('.//{http://www.opengis.net/gml}featureMember')
    logger.debug(f"[Parsed featureMember count] {len(members)}")

    fish_list = []
    gml = "{http://www.opengis.net/gml}"
    for member in members:
        # 파싱 전, 해당 member XML 출력 (첫 200자)
        xml_snippet = ET.tostring(member, encoding='unicode')[:200]
        logger.debug(f"[featureMember snippet]\n{xml_snippet}…")

        feature = member.find(f'.//EcoBank:{type_name}', {
            "EcoBank": "www.wavus.com"
        })
        if feature is None:
            continue

        coords = feature.find(f'.//{gml}coordinates')
        lon, lat = map(float, coords.text.split(',')) if coords is not None else (None, None)

        info = {
            "spcs_korean_nm":  feature.findtext("EcoBank:spcs_korean_nm", namespaces={"EcoBank": "www.wavus.com"}),
            "spcs_scncenm":    feature.findtext("EcoBank:spcs_scncenm",   namespaces={"EcoBank": "www.wavus.com"}),
            "indvd_co":        feature.findtext("EcoBank:indvd_co",       namespaces={"EcoBank": "www.wavus.com"}),
            "examin_begin_de": feature.findtext("EcoBank:examin_begin_de",namespaces={"EcoBank": "www.wavus.com"}),
            "latitude":        lat,
            "longitude":       lon,
        }
        fish_list.append(info)

    # 5) 최종 반환 리스트 로그
    logger.debug(f"[fish_list] {fish_list}")
    return fish_list
