from flask import Blueprint, request, jsonify
import pymysql
from dotenv import load_dotenv
from .db_service import get_connection

load_dotenv()

user_api = Blueprint('user_api', __name__)

# 회원 생성
@user_api.route('/create/users', methods=['POST'])
def create_user():
    data = request.json

    required_fields = ['user_id', 'user_pw', 'name', 'email']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"result": "실패", "error": f"필수 필드 누락: {', '.join(missing)}"}), 400

    user_id = data['user_id']
    user_pw = data['user_pw']
    name = data['name']
    email = data['email']
    address = data.get('address')
    phone = data.get('phone')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM users WHERE user_id = %s OR email = %s", (user_id, email))
        if cursor.fetchone():
            return jsonify({"result": "실패", "error": "이미 존재하는 ID 또는 이메일입니다."}), 409

        sql = """
            INSERT INTO users (user_id, user_pw, name, email, address, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, user_pw, name, email, address, phone))
        conn.commit()
        return jsonify({"result": "성공", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 로그인
@user_api.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    user_pw = data.get('user_pw')

    if not user_id or not user_pw:
        return jsonify({"result": "실패", "error": "ID/PW 입력 누락"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        sql = """
            SELECT *
            FROM users
            WHERE user_id = %s AND user_pw = %s
        """
        cursor.execute(sql, (user_id, user_pw))
        user = cursor.fetchone()

        if user:
            return jsonify({"result": "성공", "user_id": user['user_id']}), 200
        else:
            return jsonify({"result": "실패", "error": "아이디 또는 비밀번호가 틀렸습니다."}), 401
    finally:
        cursor.close()
        conn.close()


