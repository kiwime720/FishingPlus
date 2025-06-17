from flask import Flask, jsonify, render_template, request, session
import os, pandas as pd

app = Flask(__name__)
app.secret_key = 'replace-with-your-secret-key'

# ——— spot 데이터 읽기 ———
BASE_DIR = os.path.dirname(__file__)
XLSX_PATH = os.path.join(BASE_DIR, 'data', 'spot_table_01.xlsx')

# 1) 엑셀 로드
df = pd.read_excel(XLSX_PATH, dtype={
    'spot_id': int, 'name': str, 'address': str,
    'tel': str, 'operation_hours': str, 'thum_url': str,
    'x': float, 'y': float, 'menu_info': str, 'type': str
})

# 2) NaN → '' 로 채우기
df.fillna('', inplace=True)

spots = []
for _, row in df.iterrows():
    spots.append({
        'spot_id'        : int(row['spot_id']),
        'name'           : row['name'],
        'address'        : row['address'],
        'tel'            : row['tel'],            # 이제 항상 문자열
        'operation_hours': row['operation_hours'],# 빈 문자열 또는 실제 값
        'type'           : row['type'],
        'coords'         : [row['x'], row['y']]   # 숫자 필드는 NaN이 아닙니다
    })

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/spots')
def api_spots():
    return jsonify(spots)

# ——— 로그인/로그아웃 API ———
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user_id = data.get('id')
    user_pw = data.get('pw')
    # TODO: 실제 DB 검증 로직으로 교체
    if user_id == 'admin' and user_pw == 'password':
        session['user'] = user_id
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
