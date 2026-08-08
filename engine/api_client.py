import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_base_url = "https://api.thestatsapi.com/api"
        self.isports_base_url = "https://api.isportsapi.com"

    def get_matches_by_date(self, date_str):
        """Busca partidos de una fecha específica (YYYY-MM-DD)"""
        print(f"Buscando partidos para la fecha: {date_str}")
        # Usamos TheStatsAPI para listar partidos
        url = f"{self.stats_base_url}/football/fixtures"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        params = {"date": date_str}
        
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 200:
                return res.json().get('data', [])
            else:
                print(f"Error API: {res.status_code}")
                return []
        except Exception as e:
            print(f"Error de conexión: {e}")
            return []

    def get_match_details(self, match_id):
        """Obtiene detalles de un partido, incluyendo los IDs de los equipos"""
        url = f"{self.stats_base_url}/football/matches/{match_id}"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                return res.json()
            return None
        except:
            return None

    def get_historical_team_data(self, team_id):
        url = f"{self.stats_base_url}/football/teams/{team_id}/history"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        try:
            res = requests.get(url, headers=headers)
            return res.json() if res.status_code == 200 else []
        except:
            return []
