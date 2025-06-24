# spot/service.py

import os
import pandas as pd

class FishingSpotService:
    def __init__(self):
        # 엑셀 파일 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(base_dir, "..", "data", "spot_table_01.xlsx")

        # 엑셀 읽기
        self.df = pd.read_excel(
            excel_path,
            dtype={
                'spot_id': int,
                'name': str,
                'address': str,
                'tel': str,
                'operation_hours': str,
                'thum_url': str,
                'x': float,  # 경도
                'y': float,  # 위도
                'menu_info': str,
                'type': str
            }
        )
        # 결측값 빈 문자열로 대체
        self.df.fillna("", inplace=True)

        # 컬럼명 매핑: 엑셀 스키마 → 서비스 스키마
        #   x(경도) → lon, y(위도) → lat, thum_url → thumbnail
        self.df = self.df.rename(columns={
            'x': 'lon',
            'y': 'lat',
            'thum_url': 'thumbnail',
            'menu_info': 'menu'
        })

        # 중기예보용 지역코드 매핑 파일 로드
        region_dir = os.path.join(base_dir, "..", "dataset", "weather_region")
        self.land_df = pd.read_csv(os.path.join(region_dir, "region_mid_land.csv"),
                                   header=None, names=["region_name", "region_code"])
        self.temp_df = pd.read_csv(os.path.join(region_dir, "region_mid_temp.csv"),
                                   header=None, names=["region_name", "region_code"])
        self.sea_df  = pd.read_csv(os.path.join(region_dir, "region_mid_sea.csv"),
                                   header=None, names=["region_name", "region_code"])

    def get_all_spots(self) -> list[dict]:
        """
        엑셀 데이터를 기반으로, 프론트엔드가 기대하는 JSON 스펙으로 반환합니다.
        각 레코드는 다음 키를 가집니다:
          spot_id, name, address, tel, operation_hours, type,
          coords: [lon, lat], thumbnail, menu
        """
        spots = []
        for _, row in self.df.iterrows():
            spots.append({
                "spot_id":         int(row["spot_id"]),
                "name":            row["name"],
                "address":         row["address"],
                "tel":             row["tel"],
                "operation_hours": row["operation_hours"],
                "type":            row["type"],
                "coords":          [row["lon"], row["lat"]],
                "thumbnail":       row["thumbnail"],
                "menu":            row["menu"]
            })
        return spots

    def get_coordinates_by_name(self, name: str) -> tuple[float, float] | tuple[None, None]:
        """
        spot 이름으로 위도(lat), 경도(lon)를 반환합니다.
        """
        match = self.df[self.df["name"].str.contains(name, case=False, na=False)]
        if not match.empty:
            return float(match.iloc[0]["lat"]), float(match.iloc[0]["lon"])
        return None, None

    def _lookup_code(self, name: str, df: pd.DataFrame) -> str | None:
        """
        spot 이름으로 주소를 검색해, 주어진 region_df에서
        일치하는 region_name을 찾아 region_code를 반환합니다.
        """
        match = self.df[self.df["name"] == name]
        if match.empty:
            return None
        addr = match.iloc[0]["address"]
        for _, region in df.iterrows():
            if region["region_name"] in addr:
                return region["region_code"]
        return None

    def get_mid_land_code_by_name(self, name: str) -> str | None:
        return self._lookup_code(name, self.land_df)

    def get_mid_temp_code_by_name(self, name: str) -> str | None:
        return self._lookup_code(name, self.temp_df)

    def get_mid_sea_code_by_name(self, name: str) -> str | None:
        return self._lookup_code(name, self.sea_df)
