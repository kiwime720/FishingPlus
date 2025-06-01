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


def parse_wfs_features(raw_xml: str) -> List[Dict[str, Any]]:
    features: List[Dict[str, Any]] = []

    try:
        doc = xmltodict.parse(raw_xml)
    except Exception as e:
        raise RuntimeError(f"WFS XML 파싱 실패: {e}")

    # <wfs:FeatureCollection> → <gml:featureMember> 리스트
    root = doc.get("wfs:FeatureCollection") or doc.get("FeatureCollection")
    if not root:
        return features

    raw_members = root.get("gml:featureMember") or root.get("featureMember") or []
    if isinstance(raw_members, dict):
        members = [raw_members]
    else:
        members = raw_members

    for member in members:
        # <EcoBank:mv_map_ecpe_fishes_point> 요소 추출
        key_candidates = [k for k in member.keys() if k.endswith("mv_map_ecpe_fishes_point")]
        if not key_candidates:
            continue
        feature_node = member.get(key_candidates[0])
        if not isinstance(feature_node, dict):
            continue

        parsed_feat: Dict[str, Any] = {}

        # 1) spce_id
        parsed_feat["spce_id"] = feature_node.get(WFS_FIELD_SPC_ID)

        # 2) geom (Point 좌표)
        #    실제 XML 구조: <gml:Point><gml:coordinates>x,y</gml:coordinates></gml:Point>
        coords = None
        geom_node = feature_node.get(WFS_FIELD_GEOM) or feature_node.get("gml:Point")
        if geom_node:
            point_node = geom_node.get("gml:Point") or geom_node if "Point" in geom_node else geom_node
            coord_text = point_node.get("gml:coordinates") or point_node.get("coordinates")
            if coord_text:
                xy = coord_text.split(",")
                try:
                    coords = [float(xy[0]), float(xy[1])]
                except:
                    coords = None
        parsed_feat["geom"] = {"type": "Point", "coordinates": coords}

        # 3) 나머지 속성
        parsed_feat["examin_year"]      = feature_node.get(WFS_FIELD_EXAMIN_YEAR)
        parsed_feat["spcs_korean_nm"]   = feature_node.get(WFS_FIELD_SPCS_KOR_NAME)
        parsed_feat["examin_area_nm"]   = feature_node.get(WFS_FIELD_AREA_NAME)
        parsed_feat["examin_begin_de"]  = feature_node.get(WFS_FIELD_BEGIN_DATE)
        parsed_feat["examin_end_de"]    = feature_node.get(WFS_FIELD_END_DATE)

        features.append(parsed_feat)

    return features
