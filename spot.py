FILE_PATH = 'dataset\weather_region\region.csv'

class Spot:
    region_code: str
    region_name: list[str]
    region_X: float
    region_Y: float
    # ... 이런식으로 전처리 하면 됩니다.
    
    def __init__(self, region_code, region_name):
        self.region_code = region_code
        self.region_name = region_name
        # ...

    def __repr__(self):
        return f"Spot(region_code={self.region_code}, region_name={self.region_name})"