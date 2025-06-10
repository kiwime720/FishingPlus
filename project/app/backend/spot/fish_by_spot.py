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
