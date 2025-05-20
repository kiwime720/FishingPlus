import os
import requests
import xmltodict
from datetime import datetime
from flask import current_app

def _get_api_key():
    key = (
        os.getenv('WEATHER_API_KEY')
        or current_app.config['API_KEYS'].get('weather', '')
    )
    if not key:
        raise RuntimeError("WEATHER_API_KEY가 설정되어 있지 않습니다.")
    return key

def get_current_weather(stn=0, help_flag=1):
    """XML/JSON/Plain Text 모두 처리하여 dict로 반환."""
    api_key = _get_api_key()
    tm = datetime.now().strftime("%Y%m%d%H%M")
    url = "https://apihub.kma.go.kr/api/typ01/url/sea_obs.php"
    params = {'tm': tm, 'stn': stn, 'help': help_flag, 'authKey': api_key}

    current_app.logger.debug(f"{params}")
    current_app.logger.debug(f"[weather] GET {url} params={params}")
    current_app.logger.debug(params)
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    text = resp.text.strip()
    if not text:
        raise RuntimeError("Empty response from KMA sea_obs API")

    ctype = resp.headers.get('Content-Type', '').lower()
    # XML
    if 'xml' in ctype or text.startswith('<?xml'):
        try:
            return xmltodict.parse(text)
        except Exception as e:
            current_app.logger.error("XML parse error", exc_info=e)
            raise
    # JSON
    if 'json' in ctype:
        return resp.json()
    # Plain Text
    lines = [l for l in text.splitlines() if l]
    if len(lines) >= 2:
        for d in ['\t', ',', ';', ' ']:
            if d in lines[0]:
                hdrs = lines[0].split(d)
                vals = lines[1].split(d)
                return {h.strip(): v.strip() for h, v in zip(hdrs, vals)}
    return {'raw': text}

def get_short_weather():