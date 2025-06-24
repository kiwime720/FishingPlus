from collections import defaultdict
from spot.service import FishingSpotService
from fish.service import FishService
from function import bbox_from_x_y_radius

class FishInfoService:
    def __init__(self, fish_api_key: str, spot_service: FishingSpotService):
        self.fish_service = FishService(fish_api_key)
        self.spot_service = spot_service

    def _process_fish_data(self, raw_features: list) -> list:
        if not raw_features:
            return []

        result_dict = defaultdict(int)
        unit_percent = 100 // len(raw_features)

        # 어종별 percent 합산
        for f in raw_features:
            species_name = f.get("spcs_korean_nm") or "이름 없음"
            result_dict[species_name] += unit_percent

        # 결과 정렬 및 총합 100%로 제한
        sorted_items = sorted(result_dict.items(), key=lambda x: -x[1])
        final_result = []
        accumulated = 0

        for species, percent in sorted_items:
            if accumulated + percent > 100:
                percent = 100 - accumulated
            final_result.append({
                "species": species,
                "percent": percent
            })
            accumulated += percent
            if accumulated >= 100:
                break

        return final_result

    def get_fish_by_coords(self, lat: float, lon: float) -> list:
        bbox = bbox_from_x_y_radius(lat, lon, radius_km=5)
        raw_features = self.fish_service.get_features(
            bbox=bbox,
            type_name="mv_map_ntee_fishes_point",
            max_features=10
        )
        return self._process_fish_data(raw_features)

    def get_fish_by_spot_name(self, name: str) -> list:
        lat, lon = self.spot_service.get_coordinates_by_name(name)
        if lat is None or lon is None:
            return [{"error": "해당 낚시터를 찾을 수 없습니다."}]
        
        bbox = bbox_from_x_y_radius(lat, lon, radius_km=5)
        raw_features = self.fish_service.get_features(
            bbox=bbox,
            type_name="mv_map_ntee_fishes_point",
            max_features=10
        )
        return self._process_fish_data(raw_features)
