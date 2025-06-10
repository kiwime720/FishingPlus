import xmltodict
from typing import List, Dict, Any

from .const import (
    WFS_FIELD_SPC_ID,
    WFS_FIELD_GEOM,
    WFS_FIELD_EXAMIN_YEAR,
    WFS_FIELD_SPCS_KOR_NAME,
    WFS_FIELD_AREA_NAME,
    WFS_FIELD_BEGIN_DATE,
    WFS_FIELD_END_DATE,
)

def fix_encoding_if_needed(text: str) -> str:
    """
    깨진 한글 복구: latin1로 잘못 디코딩된 문자열을 utf-8로 복구
    """
    if not isinstance(text, str):
        return text
    try:
        return bytes(text, "latin1").decode("utf-8")
    except Exception:
        return text

def parse_wfs_features(raw_xml: str) -> List[Dict[str, Any]]:
    features: List[Dict[str, Any]] = []

    try:
        doc = xmltodict.parse(raw_xml)
    except Exception as e:
        raise RuntimeError(f"WFS XML 파싱 실패: {e}")

    root = doc.get("wfs:FeatureCollection") or doc.get("FeatureCollection")
    if not root:
        return features

    raw_members = root.get("gml:featureMember") or root.get("featureMember") or []
    members = [raw_members] if isinstance(raw_members, dict) else raw_members

    for member in members:
        key_candidates = [k for k in member.keys() if k.endswith("fishes_point")]
        if not key_candidates:
            continue

        feature_node = member.get(key_candidates[0])
        if not isinstance(feature_node, dict):
            continue

        parsed_feat: Dict[str, Any] = {}

        # 일반 필드 (한글 포함된 항목은 디코딩 시도)
        parsed_feat["spce_id"]          = feature_node.get("EcoBank:spcs_code")
        parsed_feat["spcs_korean_nm"]   = fix_encoding_if_needed(feature_node.get("EcoBank:spcs_korean_nm"))
        parsed_feat["examin_year"]      = feature_node.get("EcoBank:examin_year")
        parsed_feat["examin_area_nm"]   = feature_node.get("EcoBank:examin_realm_se_code")
        parsed_feat["examin_begin_de"]  = feature_node.get("EcoBank:examin_begin_de")
        parsed_feat["examin_end_de"]    = feature_node.get("EcoBank:examin_end_de")

        # 좌표 파싱
        coords = None
        geom_node = feature_node.get("EcoBank:geom")
        if geom_node:
            point_node = geom_node.get("gml:Point")
            if point_node:
                coord_obj = point_node.get("gml:coordinates")
                coord_text = coord_obj.get("#text") if isinstance(coord_obj, dict) else coord_obj
                if coord_text:
                    try:
                        x, y = map(float, coord_text.split(","))
                        coords = [x, y]
                    except:
                        coords = None

        parsed_feat["geom"] = {"type": "Point", "coordinates": coords}
        features.append(parsed_feat)

    return features
