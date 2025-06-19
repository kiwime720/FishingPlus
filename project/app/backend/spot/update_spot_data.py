import os
import json
import time
import pandas as pd
from spot.weather_by_spot import FishingWeatherService
from spot.fish_by_spot import FishInfoService

def update_fishing_spot_data(
    weather_service: FishingWeatherService,
    fish_service: FishInfoService,
    max_retry: int = 3,
    retry_delay: float = 1.5
):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "dataset", "fishing_spot", "fishing_spot.csv")

    df = pd.read_csv(file_path)

    for idx, row in df.iterrows():
        name = row["name"]
        lat = row["lat"]
        lon = row["lon"]
        address = row.get("address", "")

        print(f"\n[{idx + 1}] {name}")

        # 날씨 정보 조회 (최대 3회)
        for attempt in range(1, max_retry + 1):
            try:
                weather = weather_service.get_weather_by_coordinates(lat, lon, address)
                if weather and isinstance(weather, dict) and "error" not in weather and any(weather.values()):
                    df.at[idx, "weather_mid"] = json.dumps(weather.get("mid", {}), ensure_ascii=False)
                    df.at[idx, "weather_short"] = json.dumps(weather.get("short", {}), ensure_ascii=False)
                    df.at[idx, "weather_ultra"] = json.dumps(weather.get("ultra", {}), ensure_ascii=False)
                    print(f"날씨 정보 조회 성공 (시도 {attempt})")
                    break
                else:
                    raise ValueError("빈 날씨 데이터 또는 오류 응답")
            except Exception as e:
                print(f"날씨 조회 실패 (시도 {attempt}/{max_retry}): {e}")
                if attempt == max_retry:
                    df.at[idx, "weather_mid"] = "조회 실패"
                    df.at[idx, "weather_short"] = "조회 실패"
                    df.at[idx, "weather_ultra"] = "조회 실패"
                else:
                    time.sleep(retry_delay)

        # 🐟 어종 정보 조회 (최대 3회)
        for attempt in range(1, max_retry + 1):
            try:
                fish_result = fish_service.get_fish_by_coordinates(lat, lon)
                fish_names = sorted(set(f.get("spcs_korean_nm", "") for f in fish_result if f.get("spcs_korean_nm")))
                df.at[idx, "fish_list"] = ", ".join(fish_names) if fish_names else "없음"
                print(f"어종 정보 조회 성공 (시도 {attempt})")
                break
            except Exception as e:
                print(f"어종 조회 실패 (시도 {attempt}/{max_retry}): {e}")
                if attempt == max_retry:
                    df.at[idx, "fish_list"] = "조회 실패"
                else:
                    time.sleep(retry_delay)

    # 저장
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"\n완료: {file_path} 갱신됨")

def retry_failed_spots(
    weather_service: FishingWeatherService,
    fish_service: FishInfoService,
    max_retry: int = 3,
    retry_delay: float = 1.5
):
    """
    낚시터 CSV에서 '조회 실패'가 포함된 항목들만 재시도하여 날씨/어종 정보 갱신
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "dataset", "fishing_spot", "fishing_spot.csv")
    df = pd.read_csv(file_path)

    # '조회 실패'가 포함된 인덱스 필터링
    target_indices = df[
        (df["weather_mid"] == "조회 실패") |
        (df["weather_short"] == "조회 실패") |
        (df["weather_ultra"] == "조회 실패") |
        (df["fish_list"] == "조회 실패")
    ].index.tolist()

    if not target_indices:
        print("모든 항목이 성공적으로 조회되어 재시도할 대상이 없습니다.")
        return

    print(f"총 {len(target_indices)}개 항목 재시도 시작")

    for idx in target_indices:
        row = df.iloc[idx]
        name = row["name"]
        lat = row["lat"]
        lon = row["lon"]
        road_address = row.get("road_address", "")
        lot_address = row.get("lot_address", "")
        sea_address = row.get("sea_address", "")
        print(f"\n[재시도] {name} ({idx})")

        # 날씨 재시도
        for attempt in range(1, max_retry + 1):
            try:
                weather = weather_service.get_weather_by_coordinates(lat, lon, road_address, lot_address)
                if weather and isinstance(weather, dict) and "error" not in weather and any(weather.values()):
                    df.at[idx, "weather_mid"] = json.dumps(weather.get("mid", {}), ensure_ascii=False)
                    df.at[idx, "weather_short"] = json.dumps(weather.get("short", {}), ensure_ascii=False)
                    df.at[idx, "weather_ultra"] = json.dumps(weather.get("ultra", {}), ensure_ascii=False)
                    print(f"날씨 정보 갱신 성공 (시도 {attempt})")
                    break
                else:
                    raise ValueError("빈 날씨 데이터 또는 오류 응답")
            except Exception as e:
                print(f"날씨 실패 (시도 {attempt}/{max_retry}): {e}")
                if attempt < max_retry:
                    time.sleep(retry_delay)

        # 어종 재시도
        for attempt in range(1, max_retry + 1):
            try:
                fish_result = fish_service.get_fish_by_coordinates(lat, lon)
                fish_names = sorted(set(f.get("spcs_korean_nm", "") for f in fish_result if f.get("spcs_korean_nm")))
                df.at[idx, "fish_list"] = ", ".join(fish_names) if fish_names else "없음"
                print(f"어종 정보 갱신 성공 (시도 {attempt})")
                break
            except Exception as e:
                print(f"어종 실패 (시도 {attempt}/{max_retry}): {e}")
                if attempt < max_retry:
                    time.sleep(retry_delay)

    # 저장
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"\n재시도 완료: {file_path} 저장됨")
