import os
import pandas as pd
import json

class FishingSpotService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "dataset", "fishing_spot", "fishing_spot.csv")
        region_dir = os.path.join(base_dir, "..", "dataset", "weather_region")
        land_path = os.path.join(region_dir, "region_mid_land.csv")
        temp_path = os.path.join(region_dir, "region_mid_temp.csv")
        sea_path = os.path.join(region_dir, "region_mid_sea.csv")
        short_path = os.path.join(region_dir, "region_short.csv")

        self.df = pd.read_csv(file_path)

        self.land_df = pd.read_csv(land_path, header=None, names=["region_name", "region_code"])
        self.temp_df = pd.read_csv(temp_path, header=None, names=["region_name", "region_code"])
        self.sea_df = pd.read_csv(sea_path, header=None, names=["region_name", "region_code"])

        short_cols = [
            "type",
            "admin_code",
            "level1",
            "level2",
            "level3",
            "grid_x",
            "grid_y",
            "lon_h",
            "lon_m",
            "lon_s",
            "lat_h",
            "lat_m",
            "lat_s",
            "lon_sec100",
            "lat_sec100",
            "update",
            "extra",
        ]
        self.short_df = pd.read_csv(short_path, names=short_cols, header=0)

        self.land_map = dict(zip(self.land_df["region_name"], self.land_df["region_code"]))
        self.temp_map = dict(zip(self.temp_df["region_name"], self.temp_df["region_code"]))
        self.sea_map = dict(zip(self.sea_df["region_name"], self.sea_df["region_code"]))

    # 모든 낚시터 출력
    def get_all_spots(self):
        return self._parse_spot_rows(self.df)

    # 바다 낚시터 출력
    def get_sea_spots(self):
        filtered = self.df[self.df["type"] == "바다"]
        return self._parse_spot_rows(filtered)

    # 육지 낚시터 출력
    def get_ground_spots(self):
        filtered = self.df[self.df["type"] != "바다"]
        return self._parse_spot_rows(filtered)

    # 내부 공통 처리 함수
    def _parse_spot_rows(self, df_subset):
        result = []
        for _, row in df_subset.iterrows():
            record = row.to_dict()
            for col in ["weather_mid", "weather_short", "weather_ultra"]:
                if isinstance(record.get(col), str):
                    try:
                        record[col] = json.loads(record[col])
                    except json.JSONDecodeError:
                        pass
            result.append(record)
        return result
    
    def get_coordinates_by_name(self, name: str):
        """
        낚시터 이름으로 위도(lat)와 경도(lon)를 반환
        """
        row = self.df[self.df["name"] == name]
        if not row.empty:
            lat = float(row.iloc[0]["lat"])
            lon = float(row.iloc[0]["lon"])
            return lat, lon
        else:
            return None, None
        
    def _lookup_code(self, name: str, df: pd.DataFrame) -> str:
        row = self.df[self.df["name"] == name]
        if row.empty:
            return None

        # None 또는 NaN 방지 처리
        road_address = str(row.iloc[0].get("road_address") or "")
        lot_address = str(row.iloc[0].get("lot_address") or "")

        for _, region_row in df.iterrows():
            region_name = region_row["region_name"]
            if region_name in road_address or region_name in lot_address:
                return region_row["region_code"]
        return None
    
    
    def _lookup_code_from_address(self, road_address: str, lot_address: str, df: pd.DataFrame) -> str:
        # None 또는 NaN 방지 처리
        road_address = str(road_address or "")
        lot_address = str(lot_address or "")

        for _, row in df.iterrows():
            region_name = row["region_name"]
            if region_name in road_address or region_name in lot_address:
                return row["region_code"]
        return None

    def get_mid_land_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.land_df)

    def get_mid_temp_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.temp_df)

    def get_mid_sea_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.sea_df)

    # ------------------------------------------------------------------
    # 격자 좌표(nx, ny)를 이용한 중기 예보 코드 조회
    # ------------------------------------------------------------------
    def _simplify(self, name: str) -> str:
        if not isinstance(name, str):
            return ""
        rep = [
            "특별시",
            "광역시",
            "특별자치도",
            "자치도",
            "자치시",
            "특별자치시",
            "도",
            "시",
            "군",
            "구",
            "읍",
            "면",
            "동",
        ]
        for r in rep:
            name = name.replace(r, "")
        return name.strip()

    def _sea_code_from_level1(self, level1: str) -> str | None:
        key = self._simplify(level1)
        sea_region_map = {
            "서울": "서해중부",
            "인천": "서해중부",
            "경기": "서해중부",
            "충남": "서해중부",
            "전북": "서해남부",
            "전남": "남해서부",
            "경남": "남해동부",
            "부산": "남해동부",
            "울산": "동해남부",
            "경북": "동해남부",
            "강원": "동해중부",
            "제주": "제주도",
        }
        sea_region = sea_region_map.get(key)
        if sea_region:
            return self.sea_map.get(sea_region)
        return None

    def _land_code_from_levels(self, l1: str, l2: str) -> str | None:
        key1 = self._simplify(l1)
        key2 = self._simplify(l2)

        if key1 == "강원":
            east_cities = {"강릉", "동해", "속초", "삼척", "양양", "고성"}
            if any(city in key2 for city in east_cities):
                return self.land_map.get("강원도영동")
            else:
                return self.land_map.get("강원도영서")

        for name in self.land_map.keys():
            if name.startswith(key1) or key1.startswith(name):
                return self.land_map[name]
        return None

    def _temp_code_from_levels(self, l1: str, l2: str, l3: str) -> str | None:
        for name in [l3, l2, l1]:
            key = self._simplify(name)
            if not key:
                continue
            for region_name, code in self.temp_map.items():
                if key.startswith(region_name) or region_name in key:
                    return code
        return None

    def get_mid_codes_by_grid(self, nx: int, ny: int) -> tuple[str | None, str | None, str | None]:
        row = self.short_df[(self.short_df["grid_x"] == nx) & (self.short_df["grid_y"] == ny)]
        if row.empty:
            return None, None, None
        row = row.iloc[0]
        l1 = row["level1"]
        l2 = row["level2"]
        l3 = row["level3"]

        land = self._land_code_from_levels(l1, l2)
        temp = self._temp_code_from_levels(l1, l2, l3)
        sea = self._sea_code_from_level1(l1)
        return land, temp, sea
