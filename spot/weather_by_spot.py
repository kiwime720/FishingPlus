from spot.service import FishingSpotService
from weather.service import WeatherService
from function import x_y_to_kma_grid
from spot.local_weather_data import LocalWeatherData

class FishingWeatherService:
    def __init__(self, weather_api_key: str, spot_service: FishingSpotService):
        """Initialize with API key, spot service and local csv weather."""
        self.api_key = weather_api_key
        self.spot_service = spot_service
        # Load local weather data once at startup
        self.local_data = LocalWeatherData()

    def get_weather_by_spot_name(self, name: str) -> dict:
        """
        낚시터 이름으로 날씨 정보 반환
        """
        # 우선 로컬 CSV에서 날씨 조회
        local = self.local_data.get_by_name(name)
        if local:
            return local

        # 로컬 데이터가 없을 경우에만 외부 API 사용
        lat, lon = self.spot_service.get_coordinates_by_name(name)
        if lat is None or lon is None:
            return {"error": "해당 낚시터를 찾을 수 없습니다."}

        nx, ny = x_y_to_kma_grid(lat, lon)

        land_code = self.spot_service.get_mid_land_code_by_name(name)
        temp_code = self.spot_service.get_mid_temp_code_by_name(name)
        sea_code = self.spot_service.get_mid_sea_code_by_name(name)

        service = WeatherService(
            self.api_key,
            nx,
            ny,
            reg_id_land=land_code,
            reg_id_temp=temp_code,
            reg_id_sea=sea_code,
        )

        forecasts = service.get_all_forecasts()
        return forecasts

    def get_weather_by_coordinates(self, lat: float, lon: float) -> dict:
        """
        위도(lat), 경도(lon) 기준 날씨 정보 반환 (중기코드는 사용 안 함)
        """
        # 로컬 CSV 우선 조회
        local = self.local_data.get_by_coordinates(lat, lon)
        if local:
            return local

        nx, ny = x_y_to_kma_grid(lat, lon)

        service = WeatherService(
            self.api_key,
            nx,
            ny,
            reg_id_land=None,
            reg_id_temp=None,
            reg_id_sea=None,
        )

        forecasts = service.get_all_forecasts()
        return forecasts
