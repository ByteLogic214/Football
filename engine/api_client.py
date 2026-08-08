import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_url = "https://api.thestatsapi.com/v1" # URL base ejemplo
        self.isports_url = "https://api.isportsapi.com/v1" # URL base ejemplo

    def get_realtime_stats(self, match_id):
        """
        Consulta datos en tiempo real de ambos proveedores para cruzar información.
        """
        # Consulta TheStatsAPI
        stats_res = requests.get(f"{self.stats_url}/match/{match_id}", params={"key": self.stats_api_key})
        stats_data = stats_res.json() if stats_res.status_code == 200 else {}

        # Consulta iSportsAPI
        isports_res = requests.get(f"{self.isports_url}/match/{match_id}", params={"key": self.isports_api_key})
        isports_data = isports_res.json() if isports_res.status_code == 200 else {}

        return stats_data, isports_data

    def get_historical_team_data(self, team_id):
        """
        Obtiene el historial para calcular promedios.
        """
        # Implementación de consulta de historial según documentación de las APIs
        # Se asume que devuelve un JSON con los últimos N partidos
        res = requests.get(f"{self.stats_url}/team/{team_id}/history", params={"key": self.stats_api_key})
        return res.json() if res.status_code == 200 else []
