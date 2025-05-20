from flask import Blueprint, jsonify, current_app, Response
from .services import get_current_weather

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

@weather_bp.route('/current')
def current():
    try:
        data = get_current_weather()
        if 'raw' in data:
            # text/plain으로 반환 (한글, 줄바꿈 그대로)
            return Response(data['raw'], content_type='text/plain; charset=utf-8')
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(e, exc_info=e)
        return jsonify(error=str(e)), 502