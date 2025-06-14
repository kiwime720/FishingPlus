import requests
from datetime import datetime, timedelta, timezone

DEBUG = False

from weather.const import (
    KMA_URL,
    KMA_MID_URL,
    CAST_F,
    CAST_V,
    CAST_ML,
    CAST_MT,
    CAST_MS
)

# KST(한국 표준시: UTC+9)
KST = timezone(timedelta(hours=9))


def _now_kst():
    return datetime.now(timezone.utc).astimezone(KST)


def get_base_datetime_ultra():
    now = _now_kst()
    hh, mm = now.hour, now.minute
    if mm < 40:
        prev = now - timedelta(hours=1)
        return prev.strftime("%Y%m%d"), f"{prev.hour:02d}00"
    else:
        return now.strftime("%Y%m%d"), f"{hh:02d}00"


def get_base_datetime_short():
    KST = timezone(timedelta(hours=9))
    now = datetime.now(timezone.utc).astimezone(KST)
    hhmm = now.hour * 100 + now.minute

    update_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    base_hour = None
    for h in reversed(update_hours):
        if hhmm >= h * 100:
            base_hour = h
            break

    if base_hour is None:
        yesterday = now.date() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d"), "2300"
    return now.strftime("%Y%m%d"), f"{base_hour:02d}00"

def get_base_datetime_mid():
    now = _now_kst()
    hh, mm = now.hour, now.minute
    if hh < 6 or (hh == 6 and mm < 0):
        base = now - timedelta(days=1)
        return base.strftime("%Y%m%d"), "1800"
    elif hh < 18:
        return now.strftime("%Y%m%d"), "0600"
    else:
        return now.strftime("%Y%m%d"), "1800"


class KMAClient:
    def __init__(
        self,
        api_key: str,
        grid_x: int,
        grid_y: int,
        reg_id_land: str | None,
        reg_id_temp: str | None,
        reg_id_sea: str | None,
    ):
        self.api_key = api_key
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.reg_id_land = reg_id_land
        self.reg_id_temp = reg_id_temp
        self.reg_id_sea = reg_id_sea

    def fetch_ultra(self):
        date, time = get_base_datetime_ultra()
        url = KMA_URL.format(CAST_F, self.api_key, self.grid_x, self.grid_y, date, time)
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def fetch_short(self):
        date, time = get_base_datetime_short()
        url = KMA_URL.format(CAST_V, self.api_key, self.grid_x, self.grid_y, date, time)
        resp = requests.get(url)
        resp.raise_for_status()
        
        if DEBUG == True:
            print(f"Response status: {resp.status_code}")
            print(f"Response URL: {resp.url}")
            print(f"Response content: {resp.text[:200]}...")
            print(f"Response headers: {resp.headers}")
        #print(resp.json())
        return resp.json()

    def fetch_mid_land(self):
        if not self.reg_id_land:
            raise ValueError("reg_id_land is None")
        date, time = get_base_datetime_mid()
        tmFc = f"{date}{time}"
        url = KMA_MID_URL.format(CAST_ML, self.api_key, self.reg_id_land, tmFc[:8], tmFc[8:])
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def fetch_mid_ta(self):
        if not self.reg_id_temp:
            raise ValueError("reg_id_temp is None")
        date, time = get_base_datetime_mid()
        tmFc = f"{date}{time}"
        url = KMA_MID_URL.format(CAST_MT, self.api_key, self.reg_id_temp, tmFc[:8], tmFc[8:])
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def fetch_mid_sea(self):
        if not self.reg_id_sea:
            raise ValueError("reg_id_sea is None")
        date, time = get_base_datetime_mid()
        tmFc = f"{date}{time}"
        url = KMA_MID_URL.format(CAST_MS, self.api_key, self.reg_id_sea, tmFc[:8], tmFc[8:])
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
