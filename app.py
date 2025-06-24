import os
from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from dotenv import load_dotenv

# 서비스 및 API Blueprint 임포트
from spot.service import FishingSpotService
from spot.weather_by_spot import FishingWeatherService
from spot.fish_by_spot import FishInfoService
from service_db.favorites_service import favorites_api
from service_db.user_service import user_api
from service_db.board_service import board_api
from service_db.comment_service import comment_api

import env


def create_app():
    """
    애플리케이션 팩토리 함수:
    - 환경 변수 로드
    - Flask 인스턴스 생성 및 설정
    - 서비스 객체 초기화
    - 블루프린트 등록
    - 라우트(엔드포인트) 정의
    """
    # 1) 환경 변수 로드
    load_dotenv()

    # 2) Flask 앱 생성 및 기본 설정
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'replace-with-your-secret-key')
    CORS(app, supports_credentials=True)   # CORS 허용

    # 3) 서비스 인스턴스 초기화
    spot_service = FishingSpotService()
    weather_service = FishingWeatherService(
        weather_api_key=env.EnvironmentKey.KMA_SERVICE_KEY,
        spot_service=spot_service
    )
    fish_service = FishInfoService(
        fish_api_key=env.EnvironmentKey.FISH_API_KEY,
        spot_service=spot_service
    )

    # 4) 앱 설정에 서비스 객체와 API 키 저장
    app.config.update({
        'SPOT_SERVICE': spot_service,
        'WEATHER_SERVICE': weather_service,
        'FISH_SERVICE': fish_service,
        'KAKAO_API_KEY': os.getenv('KAKAO_API_KEY')
    })

    # 5) Blueprint 등록 (/api/*)
    app.register_blueprint(favorites_api, url_prefix='/api')
    app.register_blueprint(user_api,      url_prefix='/api')
    app.register_blueprint(board_api,     url_prefix='/api')
    app.register_blueprint(comment_api,   url_prefix='/api')

    # ----------------------------
    # 기본 화면 렌더링
    # ----------------------------

    @app.route('/')
    def index():
        """메인 페이지 (지도 + 검색) 렌더링"""
        return render_template('home.html', kakao_key=app.config['KAKAO_API_KEY'])

    @app.route('/signup')
    def signup_page():
        """회원가입 페이지 렌더링"""
        return render_template('signup.html')

    # ----------------------------
    # 낚시터 API
    # ----------------------------

    @app.route('/api/spots', methods=['GET'])
    def get_spots():
        """모든 낚시터 정보 반환"""
        data = spot_service.get_all_spots()
        return jsonify(data)

    # ----------------------------
    # 날씨 API
    # ----------------------------

    @app.route('/api/weather', methods=['GET'])
    def get_weather():
        """
        날씨 정보 조회
        - ?name=스팟명 으로 조회: 중기 예보 포함
        - ?lat=위도&lng=경도 으로 조회: 중기 코드는 사용 안 함
        """
        name = request.args.get('name')
        lat  = request.args.get('lat', type=float)
        lng  = request.args.get('lng', type=float)

        if name:
            result = weather_service.get_weather_by_spot_name(name)
        elif lat is not None and lng is not None:
            result = weather_service.get_weather_by_coordinates(lat, lng)
        else:
            return jsonify({
                'error': "Missing 'name' or 'lat/lng' parameters"
            }), 400

        return jsonify(result)

    # ----------------------------
    # 어종 정보 API
    # ----------------------------

    @app.route('/api/fish', methods=['GET'])
    def get_fish_by_name():
        """스팟명으로 물고기 정보 조회"""
        name = request.args.get('name')
        if not name:
            return jsonify({'error': "Missing 'name' parameter"}), 400
        data = fish_service.get_fish_by_spot_name(name)
        return jsonify(data)

    @app.route('/api/fish/by-coords', methods=['GET'])
    def get_fish_by_coords():
        """위도/경도 기준 물고기 정보 조회"""
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        if lat is None or lng is None:
            return jsonify({'error': "Missing 'lat' or 'lng' parameter"}), 400
        data = fish_service.get_fish_by_coords(lat, lng)
        return jsonify(data)

    return app


if __name__ == '__main__':
    # 개발 모드에서 실행
    app = create_app()
    app.run(debug=True)