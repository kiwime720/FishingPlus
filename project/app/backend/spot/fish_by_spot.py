from spot.service import FishingSpotService
from fish.service import FishService
from function import bbox_from_x_y_radius

class FishInfoService:
    def __init__(self, fish_api_key: str, spot_service: FishingSpotService):
        self.fish_service = FishService(fish_api_key)
        self.spot_service = spot_service

    # 낚시터 이름으로 어종 구하기
    def get_fish_by_spot_name(self, name: str) -> list:
        # 위경도 조회
        lat, lon = self.spot_service.get_coordinates_by_name(name)
        if lat is None or lon is None:
            return [{"error": "해당 낚시터를 찾을 수 없습니다."}]

        # bbox 계산 (반경 5km 기준)
        bbox = bbox_from_x_y_radius(lat, lon, radius_km=5)
        # bbox = 314548.9311225004,401742.29949240043,320867.0145135768,409072.0397406582

        # # 물고기 API 조회
        # return self.fish_service.get_features(
        #     bbox=bbox,
        #     type_name="mv_map_ntee_fishes_point",
        #     max_features=10
        # )
        result = self.fish_service.get_features(
        bbox=bbox,
        type_name="mv_map_ntee_fishes_point",
        max_features=10
        )
        return result
    
    def get_fish_by_coordinates(self, lat: float, lon: float) -> list:
        """
        위도/경도로부터 BBOX를 계산해 물고기 API를 호출하고,
        조회된 어종 정보를 리스트로 반환합니다.
        - 어종이 없으면 빈 리스트 반환
        - 실패 시 예외 로그를 출력하고 빈 리스트 반환
        """
        bbox = bbox_from_x_y_radius(lat, lon, radius_km=5)
        print(f"[FishAPI] 요청 bbox: {bbox} (위도: {lat}, 경도: {lon})")

        try:
            result = self.fish_service.get_features(
                bbox=bbox,
                type_name="mv_map_ntee_fishes_point",
                max_features=10
            )

            # 결과 검증
            if not isinstance(result, list):
                print("[FishAPI] 경고: API 응답이 list가 아닙니다.")
                return []

            if not result:
                print("[FishAPI] 조회된 어종 없음.")
                return []

            # 유효한 어종 정보 있는지 확인
            valid_items = [f for f in result if f.get("spcs_korean_nm")]
            print(f"[FishAPI] 유효 어종 개수: {len(valid_items)}")

            return valid_items

        except Exception as e:
            print(f"[FishAPI] 예외 발생: {e}")
            return []
