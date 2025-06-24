from flask import Blueprint, request, jsonify
from .db_service import get_connection
from pymysql.cursors import DictCursor
import pymysql

favorites_api = Blueprint('favorites_api', __name__)

# 즐겨찾기 등록
@favorites_api.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id')
    spot_id = data.get('spot_id')
    memo = data.get('memo', '')

    if not user_id or not spot_id:
        return jsonify({"result": "실패", "error": "user_id와 spot_id는 필수입니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 중복 확인
        sql_check = "SELECT 1 FROM favorites WHERE user_id = %s AND spot_id = %s"
        cursor.execute(sql_check, (user_id, spot_id))
        if cursor.fetchone():
            return jsonify({"result": "실패", "error": "이미 즐겨찾기에 추가된 항목입니다."}), 400

        sql_insert = """
            INSERT INTO favorites (user_id, spot_id, memo)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql_insert, (user_id, spot_id, memo))
        conn.commit()
        return jsonify({"result": "성공"}), 201

    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 즐겨찾기 삭제
@favorites_api.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.json
    user_id = data.get('user_id')
    spot_id = data.get('spot_id')

    if not user_id or not spot_id:
        return jsonify({"result": "실패", "error": "user_id와 spot_id는 필수입니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM favorites WHERE user_id = %s AND spot_id = %s"
        affected_rows = cursor.execute(sql, (user_id, spot_id))
        conn.commit()
        if affected_rows == 0:
            return jsonify({"result": "실패", "error": "삭제할 항목이 없습니다."}), 404
        return jsonify({"result": "삭제 완료"}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 즐겨찾기 조회
@favorites_api.route('/favorites', methods=['GET'])
def get_favorite_spots():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"result": "실패", "error": "user_id는 필수입니다."}), 400

    conn = get_connection()
    cursor = conn.cursor(DictCursor)
    try:
        sql = """
            SELECT s.*, f.memo
            FROM favorites f
            JOIN spot s ON f.spot_id = s.spot_id
            WHERE f.user_id = %s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return jsonify({"result": "성공", "data": result}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

