from flask import Blueprint, request, jsonify
import pymysql
from dotenv import load_dotenv
from .db_service import get_connection

load_dotenv()

board_api = Blueprint('board_api', __name__)

# 게시판 조회
@board_api.route("/boards", methods=["GET"])
def search_all_boards():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        sql = """
            SELECT board_id, user_id, title, content, reg_date
            FROM board
            ORDER BY reg_date DESC
        """
        cursor.execute(sql)
        boards = cursor.fetchall()
        return jsonify({"result": "성공", "boards": boards}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 게시판 등록
@board_api.route("/boards", methods=["POST"])
def create_board():
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")
    spot_id = data.get("spot_id")

    if not all([user_id, title, content]):
        return jsonify({"result": "실패", "error": "필수 필드 필요"}), 400

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            INSERT INTO board (user_id, title, content, reg_date)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, title, content))
        board_id = cursor.lastrowid

        if spot_id:
            cursor.execute("""
                INSERT INTO board_spot (board_id, spot_id)
                VALUES (%s, %s)
            """, (board_id, spot_id))

        conn.commit()
        return jsonify({"result": "성공", "board_id": board_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"result": "실패", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# 게시판 수정
@board_api.route("boards/<int:board_id>", methods=["PUT"])
def update_board(board_id):
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")
    spot_id = data.get("spot_id")

    if not all([user_id, title, content]):
        return jsonify({"result": "실패", "error": "필수 항목 누락"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 작성자 확인
        cursor.execute("SELECT user_id FROM board WHERE board_id = %s", (board_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"result": "실패", "error": "게시글 없음"}), 404
        if result["user_id"] != user_id:
            return jsonify({"result": "실패", "error": "권한 없음"}), 403

        # 게시글 수정
        cursor.execute("UPDATE board SET title = %s, content = %s WHERE board_id = %s", (title, content, board_id))

        if spot_id:
            cursor.execute("DELETE FROM board_spot WHERE board_id = %s", (board_id,))
            cursor.execute("INSERT INTO board_spot (board_id, spot_id) VALUES (%s, %s)", (board_id, spot_id))

        conn.commit()
        return jsonify({"result": "성공"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 게시판 삭제
@board_api.route("boards/<int:board_id>", methods=["DELETE"])
def delete_board(board_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"result": "실패", "error": "user_id 필요"}), 400

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 작성자 확인
        cursor.execute("SELECT user_id FROM board WHERE board_id = %s", (board_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"result": "실패", "error": "게시글 없음"}), 404
        if result["user_id"] != user_id:
            return jsonify({"result": "실패", "error": "권한 없음"}), 403

        # 댓글 먼저 삭제
        cursor.execute("DELETE FROM comment WHERE board_id = %s", (board_id,))

        # board_spot 관계 삭제
        cursor.execute("DELETE FROM board_spot WHERE board_id = %s", (board_id,))

        # 게시글 삭제
        cursor.execute("DELETE FROM board WHERE board_id = %s", (board_id,))
        conn.commit()
        return jsonify({"result": "성공"}), 200
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 가게 정보 조회
@board_api.route("/spots/search", methods=["GET"])
def search_spots():
    keyword = request.args.get("q", "")
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT spot_id, name, address
            FROM spot
            WHERE name LIKE %s
            LIMIT 20
        """, (f"%{keyword}%",))
        spots = cursor.fetchall()
        return jsonify({"result": "성공", "spots": spots}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@board_api.route("/boards/<int:board_id>", methods=["GET"])
def get_board_detail(board_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 게시글 정보
        cursor.execute("""
            SELECT board_id, user_id, title, content, reg_date
            FROM board WHERE board_id = %s
        """, (board_id,))
        board = cursor.fetchone()
        if not board:
            return jsonify({"result": "실패", "error": "게시글 없음"}), 404

        # 낚시터 정보
        cursor.execute("""
            SELECT s.spot_id, s.name, s.address, s.tel, s.operation_hours, s.thum_url, s.menu_info, s.type
            FROM spot s
            JOIN board_spot bs ON s.spot_id = bs.spot_id
            WHERE bs.board_id = %s
        """, (board_id,))
        spot = cursor.fetchone()

        return jsonify({"result": "성공", "board": board, "spot": spot}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

