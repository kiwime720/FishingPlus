import requests

from .const import (
    BASE_URL,
    WFS_ENDPOINT,
    PARAM_SERVICE_KEY,
    PARAM_TYPE_NAME,
    PARAM_BBOX,
    PARAM_MAX_FEATURES,
    DEFAULT_TYPE_NAME,
    DEFAULT_MAX_FEATURES,
)


class FishAPIClient:
    """
    EcoBank 생태계정밀조사_어류_점 API 전용 클라이언트 (WFS 전용).
    • get_wfs_features(): WFS로 피처 XML(또는 JSON) 조회
    """

    def __init__(self, service_key: str):
        self.service_key = service_key

    def get_wfs_features(
        self,
        bbox: str,
        type_name: str = None,
        max_features: int = None,
        srs: str = None,
    ) -> str:
        """
        WFS 조회: 지정한 bbox, 피처 타입, 최대 개수 등에 따라 피처 정보(XML/JSON) 반환.
        • bbox: "minx,miny,maxx,maxy"
        • type_name: 피처 타입명(쉼표 구분, 기본 DEFAULT_TYPE_NAME)
        • max_features: 최대 개수 (기본 DEFAULT_MAX_FEATURES)
        • srs: 좌표계 (기본 DEFAULT_SRS)

        응답 데이터를 XML 문자열로 반환합니다.
        """
        url = BASE_URL + WFS_ENDPOINT
        params = {
            PARAM_SERVICE_KEY: self.service_key,
            PARAM_TYPE_NAME: type_name or DEFAULT_TYPE_NAME,
            PARAM_BBOX: bbox,
            PARAM_MAX_FEATURES: max_features or DEFAULT_MAX_FEATURES,
        }
        resp = requests.get(url, params=params)
        print(url, params)
        resp.raise_for_status()
        print(resp.text)
        return resp.text
