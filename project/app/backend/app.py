from flask import Flask, jsonify, request, Response, json
from spot.service import FishingSpotService
from spot.weather_by_spot import FishingWeatherService
from spot.fish_by_spot import FishInfoService
from spot.update_spot_data import update_fishing_spot_data, retry_failed_spots
from apscheduler.schedulers.background import BackgroundScheduler
import env
import atexit

app = Flask(__name__)

# 서비스 인스턴스 생성
spot_service = FishingSpotService()
weather_service = FishingWeatherService(weather_api_key=env.EnvironmentKey.KMA_SERVICE_KEY, spot_service=spot_service)
fish_service = FishInfoService(fish_api_key=env.EnvironmentKey.FISH_API_KEY, spot_service=spot_service)

# 낚시터 출력
@app.route("/api/spots", methods=["GET"])
def get_all_spots():
    return Response(
        json.dumps(spot_service.get_all_spots(), ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

# 바다 낚시터 출력
@app.route("/api/spots/sea", methods=["GET"])
def get_sea_spots():
    return Response(
        json.dumps(spot_service.get_sea_spots(), ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

# 육지 낚시터 출력
@app.route("/api/spots/ground", methods=["GET"])
def get_ground_spots():
    return Response(
        json.dumps(spot_service.get_ground_spots(), ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

# 낚시터 날씨 출력, 파라미터 낚시터이름
@app.route("/api/weather", methods=["GET"])
def get_weather_by_name():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400
    result = weather_service.get_weather_by_spot_name(name)
    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

# 낚시터 어종 출력, 파라미터 낚시터이름
@app.route("/api/fish", methods=["GET"])
def get_fish_by_name():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400
    result = fish_service.get_fish_by_spot_name(name)
    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
