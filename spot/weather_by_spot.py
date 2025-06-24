from spot.service import FishingSpotService
from weather.service import WeatherService
from function import x_y_to_kma_grid

class FishingWeatherService:
    def __init__(self, weather_api_key: str, spot_service: FishingSpotService):
        # 기상청 API 키 및 낚시터 서비스 초기화
        self.api_key = weather_api_key
        self.spot_service = spot_service

    def get_weather_by_spot_name(self, name: str) -> dict:
        """
        낚시터 이름으로 날씨 정보 반환
        """
        # 낚시터 이름을 통해 위도/경도 조회
        lat, lon = self.spot_service.get_coordinates_by_name(name)
        if lat is None or lon is None:
            return {"error": "해당 낚시터를 찾을 수 없습니다."}

        # 위경도를 기상청 격자 좌표로 변환
        nx, ny = x_y_to_kma_grid(lat, lon)

        # 낚시터 이름으로 중기예보 지역코드 얻기 (육상/기온/해상)
        land_code = self.spot_service.get_mid_land_code_by_name(name)
        temp_code = self.spot_service.get_mid_temp_code_by_name(name)
        sea_code = self.spot_service.get_mid_sea_code_by_name(name)

        # 날씨 서비스 인스턴스 생성
        service = WeatherService(
            self.api_key,
            nx,
            ny,
            reg_id_land=land_code,
            reg_id_temp=temp_code,
            reg_id_sea=sea_code,
        )

        # 전체 예보 데이터 반환
        forecasts = service.get_all_forecasts()
        return forecasts

    def get_weather_by_coordinates(self, lat: float, lon: float) -> dict:
        """
        위도(lat), 경도(lon) 기준 날씨 정보 반환 (중기코드는 사용 안 함)
        """
        # 위경도를 기상청 격자 좌표로 변환
        nx, ny = x_y_to_kma_grid(lat, lon)

        # 중기코드 없이 날씨 요청
        service = WeatherService(
            self.api_key,
            nx,
            ny,
            reg_id_land=None,
            reg_id_temp=None,
            reg_id_sea=None,
        )

        # 전체 예보 데이터 반환
        forecasts = service.get_all_forecasts()
        return forecasts
