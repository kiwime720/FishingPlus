from flask import Flask, jsonify, render_template
import os, csv, random, datetime

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, 'data', 'fishing_spot.csv')

app = Flask(__name__, static_folder='static', template_folder='templates')

# ——— 낚시터 데이터 로드 ———
spots = []
with open(CSV_PATH, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        spots.append({
            'name'         : row['낚시터명'],
            'type'         : row['낚시터유형'],
            'road_address' : row['소재지도로명주소'],
            'jibun_address': row['소재지지번주소'],
            'coords'       : [
                float(row['WGS84위도']),
                float(row['WGS84경도'])
            ]
        })

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/spots')
def api_spots():
    return jsonify(spots)

@app.route('/board')
def board():
    return render_template('board.html')

# ——— 날씨 API (모킹) ———
def mock_weather():
    now     = datetime.datetime.now()
    sunrise = "06:00"
    sunset  = "19:00"
    return {
        'location'           : 'Seoul, KR',
        'temperature'        : round(random.uniform(18, 28), 1),
        'description'        : random.choice(['맑음','구름조금','흐림','비']),
        'humidity'           : random.randint(40, 70),
        'wind_speed'         : round(random.uniform(3, 12), 1),
        'sunrise'            : sunrise,
        'sunset'             : sunset,
        'day_length'         : '13h 00m',
        'precipitation_chance': random.randint(0, 30),
        'forecast'           : [
            {
              'day' : (now + datetime.timedelta(days=i)).strftime('%a'),
              'icon': '⛅',
              'temp': round(random.uniform(18, 28),1)
            }
            for i in range(1,5)
        ]
    }

@app.route('/api/weather/today')
def api_weather_today():
    return jsonify(mock_weather())

@app.route('/api/weather/tomorrow')
def api_weather_tomorrow():
    return jsonify(mock_weather())

# ——— 어종 API (임의 데이터) ———
@app.route('/api/fish')
def api_fish():
    species = ['광어','참돔','농어','전어','도미']
    counts  = [ random.randint(10,50) for _ in species ]
    total   = sum(counts)
    distribution = [
        {'species': s, 'percent': round(c/total*100,1)}
        for s,c in zip(species, counts)
    ]
    return jsonify(distribution)

if __name__ == '__main__':
    app.run(debug=True)
