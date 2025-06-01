import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class EnvironmentKey:
    # 기상청 API 키
    KMA_SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")
    # 물고기 API 키
    FISH_API_KEY = os.getenv("FISH_API_KEY")
    # 데이터베이스 URL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False