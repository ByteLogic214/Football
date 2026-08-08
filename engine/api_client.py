import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_base_url = "https://api.thestatsapi.com/api"
        self.isports_base_url = "https://api.isportsapi.com"

    def get_matches_by_date(self, date_str):
        """
        Consulta partidos usando el endpoint exacto proporcionado.
        """
        print(f"Consultando partidos para: {date_str}")
        url = f"{self.stats_base_url}/football/matches"
        
        headers = {
            "Authorization": f"Bearer {self.stats_api_key}"
        }
        
        # Parámetros exactos según tu documentación
        params = {
            "date_from": date_str,
            "date_to": date_str,
            "utc_offset": "-06:00", # Ajustado a CDMX según tu ejemplo
            "per_page": 100,
            "status": "scheduled"   # Solo partidos programados
        }

        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 200:
                data = res.json()
                # La API suele devolver los datos dentro de una llave 'data'
                return data.get('data', []) if isinstance(data, dict) else data
            else:
                print(f"❌ Error API TheStatsAPI: {res.status_code}")
                print(f"Respuesta: {res.text}")
                return []
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return []

    def get_match_details(self, match_id):
        """
        Obtiene detalles de un partido específico.
        Basado en el patrón de la API: /football/matches/{id}
        """
        url = f"{self.stats_base_url}/football/matches/{match_id}"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                return res.json()
            else:
                print(f"❌ Error al obtener detalles del partido: {res.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def get_historical_team_data(self, team_id):
        """Obtiene historial para promedios"""
        url = f"{self.stats_base_url}/football/teams/{team_id}/history"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        try:
            res = requests.get(url, headers=headers)
            return res.json() if res.status_code == 200 else []
        except:
            return []
