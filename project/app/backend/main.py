# project/main.py

import requests
import env

from weather.service import WeatherService
from fish.service import FishService

def main():
    API_KEY = env.EnvironmentKey.KMA_SERVICE_KEY
    GRID_X  = 60
    GRID_Y  = 127
    REG_ID  = "11B00000"  # 예: 서울 종로구 중기예보 지점코드

    service = WeatherService(API_KEY, GRID_X, GRID_Y, REG_ID)
    forecasts = service.get_all_forecasts()

    print("=== 초단기 예보 ===")
    for date, data in sorted(forecasts["ultra"].items()):
        print(f"{date} → {data}")

    print("\n=== 단기 예보 ===")
    for date, data in sorted(forecasts["short"].items()):
        print(f"{date} → {data}")

    print("\n=== 중기 예보 ===")
    for date, data in sorted(forecasts["mid"].items()):
        print(f"{date} → {data}")

    # 1) 자신의 EcoBank API 서비스 키를 입력하세요
    SERVICE_KEY = env.EnvironmentKey.FISH_API_KEY

    # 2) 조회할 Bounding Box (EPSG:5186 좌표계)
    bbox_example = "314548.93,401742.29,320867.01,409072.03"

    # 3) FishService 객체 생성
    service = FishService(SERVICE_KEY)

    try:
        # 4) WFS 피처 조회
        features = service.get_features(
            bbox=bbox_example,
            type_name="mv_map_ecpe_fishes_point",
            max_features=10
        )

        # 5) 결과 출력
        if not features:
            print("조회된 피처가 없습니다.")
        else:
            print("WFS 조회 결과 (최대 10개):")
            for idx, feat in enumerate(features, start=1):
                print(f"\n--- Feature #{idx} ---")
                for key, val in feat.items():
                    print(f"{key}: {val}")

    except requests.exceptions.RequestException as re:
        # requests 라이브러리에서 발생할 수 있는 예외
        print(f"[RequestException] {re}")
    except Exception as e:
        # FishAPIClient.get_wfs_features()에서 던진 Exception 포함
        print(f"[Error] WFS 조회 실패: {e}")

if __name__ == "__main__":
    main()
