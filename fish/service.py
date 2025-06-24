# fish/service.py
from .client import FishAPIClient
from .parser import parse_wfs_features
from typing import List, Dict, Any


class FishService:
    """
    WFS 피처 리스트(딕셔너리) 리턴
    """

    def __init__(self, service_key: str):
        self.client = FishAPIClient(service_key)

    def get_features(
        self,
        bbox: str,
        type_name: str = None,
        max_features: int = None,
    ) -> List[Dict[str, Any]]:
        """
        WFS를 통해 피처(속성 + 좌표) 리스트를 파싱하여 반환.
        • bbox: "minx,miny,maxx,maxy"
        • type_name: 피처 타입명 (기본 DEFAULT_TYPE_NAME)
        • max_features: 최대 개수 (기본 DEFAULT_MAX_FEATURES)
        • srs: 좌표계 (기본 DEFAULT_SRS)
        """
        raw_xml = self.client.get_wfs_features(
            bbox=bbox,
            type_name=type_name,
            max_features=max_features,
        )
        return parse_wfs_features(raw_xml)
