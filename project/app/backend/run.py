# run.py

from backend import create_app

app = create_app()

if __name__ == '__main__':
    # 0.0.0.0 으로 바인딩하면 외부에서도 접근 가능
    app.run(host='0.0.0.0', port=5000, debug=True)
