import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_base_url = "https://api.thestatsapi.com/api"
        self.isports_base_url = "https://api.isportsapi.com"

    def get(self, endpoint, params=None):
        """Método base para todas las llamadas a TheStatsAPI"""
        url = f"{self.stats_base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception as e:
            print(f"Error en llamada a {endpoint}: {e}")
            return None

    def get_matches_by_date(self, date_str):
        params = {
            "date_from": date_str,
            "date_to": date_str,
            "utc_offset": "-06:00",
            "per_page": 100,
            "status": "scheduled"
        }
        response = self.get("/football/matches", params=params)
        return response.get("data", []) if response else []

    def get_match_details(self, match_id):
        return self.get(f"/football/matches/{match_id}")

    def get_historical_team_data(self, team_id, match_date):
        """
        Implementación exacta según la estructura requerida.
        """
        params = {
            "team_id": team_id,
            "date_to": match_date,
            "status": "finished",
            "per_page": 100,
            "utc_offset": "-06:00"
        }

        response = self.get("/football/matches", params=params)
        matches = response.get("data", []) if response else []

        history = []
        for match in matches:
            match_id = match.get("id")
            if not match_id:
                continue

            stats_response = self.get(f"/football/matches/{match_id}/stats")

            if stats_response and stats_response.get("data"):
                history.append({
                    "match": match,
                    "stats": stats_response["data"]
                })
        return history
