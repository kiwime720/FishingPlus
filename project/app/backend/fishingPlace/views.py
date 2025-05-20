import json
from flask import Blueprint, jsonify, Response
from .read_csv import get_fishingPlace

fishing_place_bp = Blueprint('fishingPlace', __name__, url_prefix='/fishingPlace')

@fishing_place_bp.route('/list/', defaults={'type': None})
@fishing_place_bp.route('/list/<type>')
def list(type):
    try:
        data = get_fishingPlace(type)
        return Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500