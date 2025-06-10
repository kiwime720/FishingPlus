import os
import pandas as pd

class FishingSpotService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "dataset", "fishing_spot", "fishing_spot.csv")
        region_dir = os.path.join(base_dir, "..", "dataset", "weather_region")
        land_path = os.path.join(region_dir, "region_mid_land.csv")
        temp_path = os.path.join(region_dir, "region_mid_temp.csv")
        sea_path = os.path.join(region_dir, "region_mid_sea.csv")

        self.df = pd.read_csv(file_path)
        self.df = self.df.rename(columns={
            "번호": "id",
            "낚시터명": "name",
            "소재지도로명주소": "road_address",
            "소재지지번주소": "lot_address",
            "WGS84위도": "lat",
            "WGS84경도": "lon",
            "낚시터유형": "type"
        })

        self.land_df = pd.read_csv(land_path, header=None, names=["region_name", "region_code"])
        self.temp_df = pd.read_csv(temp_path, header=None, names=["region_name", "region_code"])
        self.sea_df = pd.read_csv(sea_path, header=None, names=["region_name", "region_code"])

    # 모든 낚시터 출력
    def get_all_spots(self):
        return self.df.to_dict(orient="records")

    # 바다 낚시터 출력
    def get_sea_spots(self):
        filtered = self.df[self.df["type"] == "바다"]
        return filtered.to_dict(orient="records")

    # 육지 낚시터 출력
    def get_ground_spots(self):
        filtered = self.df[self.df["type"] != "바다"]
        return filtered.to_dict(orient="records")
    
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

        road_address = row.iloc[0].get("road_address", "")
        lot_address = row.iloc[0].get("lot_address", "")

        for _, region_row in df.iterrows():
            region_name = region_row["region_name"]
            if region_name in road_address or region_name in lot_address:
                return region_row["region_code"]
        return None

    def get_mid_land_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.land_df)

    def get_mid_temp_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.temp_df)

    def get_mid_sea_code_by_name(self, name: str) -> str:
        return self._lookup_code(name, self.sea_df)
