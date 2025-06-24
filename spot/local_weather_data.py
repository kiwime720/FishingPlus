import csv
import json
import os
from typing import Dict, List, Optional


class LocalWeatherData:
    """Load weather data from csv/fishing_spot.csv"""

    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_dir, "..", "csv", "fishing_spot.csv")
        self.rows: List[dict] = []
        try:
            with open(csv_path, encoding="utf-8") as f:
                self.rows = list(csv.DictReader(f))
        except FileNotFoundError:
            self.rows = []

    def _extract_weather(self, row: dict) -> Dict[str, dict]:
        out = {}
        if row.get("weather_mid"):
            try:
                out["mid"] = json.loads(row["weather_mid"])
            except json.JSONDecodeError:
                out["mid"] = {}
        if row.get("weather_short"):
            try:
                out["short"] = json.loads(row["weather_short"])
            except json.JSONDecodeError:
                out["short"] = {}
        if row.get("weather_ultra"):
            try:
                out["ultra"] = json.loads(row["weather_ultra"])
            except json.JSONDecodeError:
                out["ultra"] = {}
        return out

    def _match_name(self, target: str) -> Optional[dict]:
        for row in self.rows:
            if row.get("name") == target:
                return row
        for row in self.rows:
            if target.lower() in row.get("name", "").lower():
                return row
        return None

    def _match_coords(self, lat: float, lon: float, tol: float = 0.0001) -> Optional[dict]:
        for row in self.rows:
            try:
                rlat = float(row.get("lat"))
                rlon = float(row.get("lon"))
            except (TypeError, ValueError):
                continue
            if abs(rlat - lat) <= tol and abs(rlon - lon) <= tol:
                return row
        return None

    def get_by_name(self, name: str) -> Dict[str, dict]:
        row = self._match_name(name)
        return self._extract_weather(row) if row else {}

    def get_by_coordinates(self, lat: float, lon: float) -> Dict[str, dict]:
        row = self._match_coords(lat, lon)
        return self._extract_weather(row) if row else {}
