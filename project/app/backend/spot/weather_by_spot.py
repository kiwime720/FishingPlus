from spot.service import FishingSpotService
from weather.service import WeatherService
from function import x_y_to_kma_grid
import time

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

        # 낚시터 이름으로 중기예보 지역코드 얻기 (육상/기온/해상)
        land_code = self.spot_service.get_mid_land_code_by_name(name)
        temp_code = self.spot_service.get_mid_temp_code_by_name(name)
        sea_code = self.spot_service.get_mid_sea_code_by_name(name)

        # 날씨 정보 요청
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

    def get_weather_by_coordinates(self, lat: float, lon: float, address: str, max_retry: int = 3, retry_delay: float = 1.5) -> dict:
        """
        위경도 + 주소 정보로 날씨 반환 (모든 예보 종류가 성공해야 성공으로 간주)
        실패 시 {"error": "..."} 형태로 반환
        """
        if lat is None or lon is None:
            return {"error": "위경도가 올바르지 않습니다."}

        try:
            # 위경도 → 기상청 격자
            nx, ny = x_y_to_kma_grid(lat, lon)
            print(f"[Weather] 격자 변환: lat={lat}, lon={lon} → nx={nx}, ny={ny}")

            # 주소에서 지역 코드 추출
            land_code = self.spot_service._lookup_code_from_address(address, self.spot_service.land_df)
            temp_code = self.spot_service._lookup_code_from_address(address, self.spot_service.temp_df)
            sea_code = self.spot_service._lookup_code_from_address(address, self.spot_service.sea_df)

            # 주소 기반으로 찾지 못한 경우 격자 기반 매핑 시도
            if not land_code or not temp_code or not sea_code:
                land_g, temp_g, sea_g = self.spot_service.get_mid_codes_by_grid(nx, ny)
                land_code = land_code or land_g
                temp_code = temp_code or temp_g
                sea_code = sea_code or sea_g

            print(f"[Weather] 코드 추출: land={land_code}, temp={temp_code}, sea={sea_code}")

            for attempt in range(1, max_retry + 1):
                try:
                    print(f"[Weather] get_all_forecasts() 시도 {attempt}")
                    service = WeatherService(
                        self.api_key,
                        nx,
                        ny,
                        reg_id_land=land_code,
                        reg_id_temp=temp_code,
                        reg_id_sea=sea_code,
                    )
                    result = service.get_all_forecasts()

                    if not isinstance(result, dict):
                        raise ValueError("예보 결과가 dict 형식이 아님")

                    mid = result.get("mid")
                    short = result.get("short")
                    ultra = result.get("ultra")

                    # 세 예보가 모두 존재하고 dict 형식인지 확인
                    if all(isinstance(val, dict) and val for val in [mid, short, ultra]):
                        print("[Weather] 모든 예보 조회 성공")
                        return result
                    else:
                        raise ValueError("중기/단기/초단기 중 일부 예보 실패 또는 빈 데이터")

                except Exception as inner_e:
                    print(f"[Weather] 재시도 실패 ({attempt}/{max_retry}): {inner_e}")
                    if attempt < max_retry:
                        time.sleep(retry_delay)

            return {"error": "날씨 전체 예보 조회 실패 (모든 예보 미완성)"}

        except Exception as e:
            print(f"[Weather] 예외 발생: {e}")
            return {"error": f"날씨 조회 중 예외 발생: {e}"}