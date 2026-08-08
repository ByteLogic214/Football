import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.base_url = "https://api.thestatsapi.com/api"
        
        # Usamos Session para persistir headers y mejorar rendimiento
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.stats_api_key}"})

    def get_match_details(self, match_id):
        try:
            response = self.session.get(f"{self.base_url}/football/matches/{match_id}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error en get_match_details: {e}")
            return None

    def get_historical_team_data(self, team_id, match_date):
        """
        Implementación exacta: Obtiene partidos y luego consulta estadísticas de cada uno.
        """
        params = {
            "team_id": str(team_id),
            "date_to": match_date,
            "status": "finished",
            "per_page": 100,
            "utc_offset": "-06:00"
        }

        print(f"\n[API] Solicitando historial para Team ID: {team_id}")
        print(f"[API] Params: {params}")

        try:
            response = self.session.get(f"{self.base_url}/football/matches", params=params)
            response.raise_for_status()
            payload = response.json()
            
            print(f"[API] URL: {response.url}")
            print(f"[API] Total partidos encontrados en meta: {payload.get('meta', {}).get('total')}")

            matches = payload.get("data", [])
            history = []

            for match in matches:
                match_id = match.get("id")
                if not match_id:
                    continue

                # Consultar estadísticas de cada partido
                stats_response = self.session.get(f"{self.base_url}/football/matches/{match_id}/stats")
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json().get("data")
                    if stats_data:
                        history.append({
                            "match": match,
                            "stats": stats_data
                        })
            
            return history

        except Exception as e:
            print(f"❌ Error en get_historical_team_data para {team_id}: {e}")
            return []
