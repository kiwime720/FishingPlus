# views.py

from flask import Blueprint, jsonify, request
from .services import fetch_fish_info

fish_bp = Blueprint('fish', __name__, url_prefix='/api/fish')

@fish_bp.route('/info')
def fish_info():
    bbox = request.args.get('bbox')
    if not bbox:
        return jsonify({"error": "bbox 파라미터가 필요합니다."}), 400
    maxf = int(request.args.get('maxFeatures', 100))

    try:
        data = fetch_fish_info(bbox, max_features=maxf)
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    return jsonify(fish=data)
