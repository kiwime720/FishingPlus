import os
import pandas as pd

class FishingSpotService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "dataset", "fishing_spot", "fishing_spot.csv")
        region_path = os.path.join(base_dir, "..", "dataset", "weather_region", "region_mid.csv")

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

        self.region_df = pd.read_csv(region_path)
        self.region_df.columns = ["region_name", "region_code"]

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
        
    def get_mid_code_by_name(self, name: str) -> str:
        """
        낚시터 이름의 도로명주소 또는 지번주소에 포함된 지역명을 이용해 중기예보 지역코드를 반환
        """
        row = self.df[self.df["name"] == name]
        if row.empty:
            return None

        road_address = row.iloc[0].get("address", "")
        lot_address = row.iloc[0].get("lot_address", "")

        for _, region_row in self.region_df.iterrows():
            region_name = region_row["region_name"]
            if region_name in road_address or region_name in lot_address:
                return region_row["region_code"]

        return None