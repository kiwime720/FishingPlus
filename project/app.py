import os
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "replace-with-your-secret-key")

# Read Kakao API key from .env
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

# Load spot data from Excel
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'data', 'spot_table_01.xlsx')

df = pd.read_excel(
    DATA_PATH,
    dtype={
        'spot_id': int,
        'name': str,
        'address': str,
        'tel': str,
        'operation_hours': str,
        'thum_url': str,
        'menu_info': str,
        'x': float,
        'y': float,
        'type': str
    }
)

df.fillna('', inplace=True)

spots = [
    {
        'spot_id': int(r['spot_id']),
        'name': r['name'],
        'address': r['address'],
        'tel': r['tel'],
        'operation_hours': r['operation_hours'],
        'type': r['type'],
        'coords': [r['x'], r['y']],
        'thumbnail': r['thum_url'],
        'menu': r['menu_info']
    }
    for _, r in df.iterrows()
]

@app.route('/')
def index():
    return render_template('home.html', kakao_key=KAKAO_API_KEY)

@app.route('/api/spots')
def api_spots():
    return jsonify(spots)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    if data.get('id') == 'admin' and data.get('pw') == 'password':
        session['user'] = data['id']
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)