# app/main/views.py
from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Welcome to Fishing Plus API"

@main_bp.route('/health')
def health():
    return jsonify(status='ok')
