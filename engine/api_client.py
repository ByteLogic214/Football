import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.base_url = "https://api.thestatsapi.com/api"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.stats_api_key}"})

    def get(self, endpoint, params=None):
        """Método base para todas las llamadas a la API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error en llamada a {endpoint}: {e}")
            return None

    def get_match_details(self, match_id):
        return self.get(f"/football/matches/{match_id}")

    def get_historical_team_data(self, team_id, match_date):
        """
        Implementación exacta: Obtiene partidos y vincula sus estadísticas.
        """
        params = {
            "team_id": str(team_id),
            "date_to": match_date,
            "status": "finished",
            "per_page": 100,
            "utc_offset": "-06:00"
        }

        print(f"\n[API] Solicitando historial para Team ID: {team_id}")
        response = self.get("/football/matches", params=params)
        
        if not response:
            return []

        matches = response.get("data", [])
        history = []

        for match in matches:
            match_id = match.get("id")
            if not match_id:
                continue

            # Consultar estadísticas de cada partido
            stats_response = self.get(f"/football/matches/{match_id}/stats")

            if stats_response and stats_response.get("data"):
                history.append({
                    "match": match,
                    "stats": stats_response["data"]
                })
        
        return history
