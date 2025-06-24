from flask import Blueprint, request, jsonify
import pymysql
from dotenv import load_dotenv
from .db_service import get_connection

load_dotenv()

comment_api = Blueprint('comment_api', __name__)

# 댓글 등록
@comment_api.route("/comments", methods=["POST"])
def post_comments():
    data = request.json
    board_id = data.get("board_id")
    user_id = data.get("user_id")
    comment_content = data.get("comment_content")

    if not all([board_id, user_id, comment_content]):
        return jsonify({"result": "실패", "error": "모든 필드가 필요합니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 게시글 존재 여부 확인
        cursor.execute("SELECT 1 FROM board WHERE board_id = %s", (board_id,))
        if not cursor.fetchone():
            return jsonify({"result": "실패", "error": "존재하지 않는 게시글입니다."}), 404

        # 댓글 등록
        sql = """
            INSERT INTO comment (board_id, user_id, comment_content, comment_date)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(sql, (board_id, user_id, comment_content))
        conn.commit()
        return jsonify({"result": "성공"}), 201
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 댓글 조회
@comment_api.route("/comments", methods=["GET"])
def get_comments_by_board():
    board_id = request.args.get("board_id")

    if not board_id:
        return jsonify({"result": "실패", "error": "board_id는 필수입니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            SELECT comment_id, board_id, user_id, comment_content, comment_date
            FROM comment
            WHERE board_id = %s
            ORDER BY comment_date ASC
        """
        cursor.execute(sql, (board_id,))
        comments = cursor.fetchall()
        return jsonify({"result": "성공", "comments": comments}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 댓글 수정
@comment_api.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    data = request.json
    user_id = data.get("user_id")
    new_content = data.get("comment_content")

    if not all([user_id, new_content]):
        return jsonify({"result": "실패", "error": "user_id와 comment_content가 필요합니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 작성자 확인
        cursor.execute("SELECT user_id FROM comment WHERE comment_id = %s", (comment_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"result": "실패", "error": "댓글이 존재하지 않습니다."}), 404
        if row["user_id"] != user_id:
            return jsonify({"result": "실패", "error": "수정 권한이 없습니다."}), 403

        sql = "UPDATE comment SET comment_content = %s WHERE comment_id = %s"
        cursor.execute(sql, (new_content, comment_id))
        conn.commit()
        return jsonify({"result": "성공"}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 댓글 삭제
@comment_api.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"result": "실패", "error": "user_id가 필요합니다."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 작성자 확인
        cursor.execute("SELECT user_id FROM comment WHERE comment_id = %s", (comment_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"result": "실패", "error": "댓글이 존재하지 않습니다."}), 404
        if row["user_id"] != user_id:
            return jsonify({"result": "실패", "error": "삭제 권한이 없습니다."}), 403

        sql = "DELETE FROM comment WHERE comment_id = %s"
        cursor.execute(sql, (comment_id,))
        conn.commit()
        return jsonify({"result": "성공"}), 200
    except Exception as e:
        return jsonify({"result": "실패", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
