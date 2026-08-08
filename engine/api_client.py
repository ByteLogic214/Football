import requests
import os

class FootballDataClient:
    def __init__(self):
        # Obtener llaves de los GitHub Secrets
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        
        # URLs Base según tu documentación
        self.stats_base_url = "https://api.thestatsapi.com/api"
        self.isports_base_url = "https://api.isportsapi.com"

    def get_realtime_stats(self, match_id):
        """
        Consulta datos en tiempo real. 
        Nota: Ajustar los endpoints según la documentación de 'match details' de cada API.
        """
        # 1. Consulta TheStatsAPI (Usa Bearer Token en Headers)
        stats_url = f"{self.stats_base_url}/football/matches/{match_id}"
        stats_headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        
        try:
            stats_res = requests.get(stats_url, headers=stats_headers)
            stats_data = stats_res.json() if stats_res.status_code == 200 else {}
        except Exception as e:
            print(f"Error TheStatsAPI: {e}")
            stats_data = {}

        # 2. Consulta iSportsAPI (Usa api_key en Params)
        isports_url = f"{self.isports_base_url}/sport/football/livescores" # Ejemplo de endpoint
        isports_params = {"api_key": self.isports_api_key}
        
        try:
            isports_res = requests.get(isports_url, params=isports_params)
            isports_data = isports_res.json() if isports_res.status_code == 200 else {}
        except Exception as e:
            print(f"Error iSportsAPI: {e}")
            isports_data = {}

        return stats_data, isports_data

    def get_historical_team_data(self, team_id):
        """
        Obtiene el historial para calcular promedios.
        """
        # Implementación para TheStatsAPI
        url = f"{self.stats_base_url}/football/teams/{team_id}/history"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        
        try:
            res = requests.get(url, headers=headers)
            return res.json() if res.status_code == 200 else []
        except:
            return []

    def search_team_name(self, team_name):
        """
        Método unificado para buscar equipos usando las reglas de cada API.
        """
        results = {"thestats": [], "isports": []}

        # --- Búsqueda en TheStatsAPI ---
        # Asumiendo endpoint de búsqueda: /football/teams/search?name=...
        stats_url = f"{self.stats_base_url}/football/teams/search"
        stats_headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        stats_params = {"name": team_name}
        
        try:
            r = requests.get(stats_url, headers=stats_headers, params=stats_params)
            if r.status_code == 200:
                results["thestats"] = r.json().get('data', [])
        except:
            pass

        # --- Búsqueda en iSportsAPI ---
        # Asumiendo endpoint de búsqueda: /sport/football/teams/search?api_key=...
        isports_url = f"{self.isports_base_url}/sport/football/teams/search"
        isports_params = {"api_key": self.isports_api_key, "name": team_name}
        
        try:
            r = requests.get(isports_url, params=isports_params)
            if r.status_code == 200:
                results["isports"] = r.json().get('data', [])
        except:
            pass

        return results
