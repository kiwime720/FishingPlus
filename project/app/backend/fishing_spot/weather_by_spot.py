from fishing_spot.service import FishingSpotService
from weather.service import WeatherService
from function import x_y_to_kma_grid

class FishingWeatherService:
    def __init__(self, weather_api_key: str, spot_service: FishingSpotService):
        self.api_key = weather_api_key
        self.spot_service = spot_service

    def get_weather_by_spot_name(self, name: str) -> dict:
        """
        낚시터 이름으로 날씨 정보 반환
        """
        lat, lon = self.spot_service.get_coordinates_by_name(name)
        if lat is None or lon is None:
            return {"error": "해당 낚시터를 찾을 수 없습니다."}

        # 위경도를 기상청 격자 좌표로 변환
        nx, ny = x_y_to_kma_grid(lat, lon)

        # 낚시터 이름으로 중기예보 지역코드 얻기
        region_code = self.spot_service.get_mid_code_by_name(name)
        if region_code is None:
            return {"error": "중기예보용 지역코드를 찾을 수 없습니다."}

        # 날씨 정보 요청
        service = WeatherService(self.api_key, nx, ny, region_code)
        forecasts = service.get_all_forecasts()
        return forecasts
