from weather.client import KMAClient
from weather.parser import parse_ultra_short, parse_short_term, parse_mid_land

class WeatherService:
    def __init__(self, api_key: str, grid_x: int, grid_y: int, reg_id: str):
        self.client = KMAClient(api_key, grid_x, grid_y, reg_id)

    def get_all_forecasts(self) -> dict:
        out = {}

        # 초단기
        try:
            raw_ultra = self.client.fetch_ultra()
            ultra_data = parse_ultra_short(raw_ultra)
        except Exception as e:
            ultra_data = {}
            print(f"[Error][초단기] {e}")

        # 단기
        try:
            raw_short = self.client.fetch_short()
            short_data = parse_short_term(raw_short)
        except Exception as e:
            short_data = {}
            print(f"[Error][단기] {e}")

        # 중기(육상)
        try:
            raw_mid_ground = self.client.fetch_mid_land()
            raw_mid_sea = self.client.fetch_mid_sea()
            mid_data_ground = parse_mid_land(raw_mid)
            mid_data_sea = parse_mid_sea(raw_mid)
        except Exception as e:
            mid_data = {}
            print(f"[Error][중기] {e}")

        out["ultra"] = ultra_data
        out["short"] = short_data
        out["mid"]   = mid_data_ground
        out["mid_sea"] = mid_data_sea

        return out