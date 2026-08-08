import requests
import os

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_base_url = "https://api.thestatsapi.com/api"
        self.isports_base_url = "https://api.isportsapi.com"

    def get_matches_by_date(self, date_str):
        url = f"{self.stats_base_url}/football/matches"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        params = {"date_from": date_str, "date_to": date_str, "utc_offset": "-06:00", "per_page": 100, "status": "scheduled"}
        try:
            res = requests.get(url, headers=headers, params=params)
            return res.json().get('data', []) if res.status_code == 200 else []
        except: return []

    def get_match_details(self, match_id):
        url = f"{self.stats_base_url}/football/matches/{match_id}"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        try:
            res = requests.get(url, headers=headers)
            return res.json() if res.status_code == 200 else None
        except: return None

    def get_historical_team_data(self, team_id, date_to):
        """
        NUEVA LÓGICA: Busca partidos terminados del equipo y extrae estadísticas de cada uno.
        """
        print(f"Buscando historial para equipo {team_id} hasta {date_to}...")
        url = f"{self.stats_base_url}/football/matches"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        params = {
            "team_id": team_id,
            "date_to": date_to,
            "status": "finished",
            "per_page": 15, # Limitamos para no saturar la API y ser rápidos
            "utc_offset": "-06:00"
        }

        history_stats = []

        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code != 200:
                return []
            
            matches = res.json().get('data', [])
            print(f"Se encontraron {len(matches)} partidos terminados.")

            for m in matches:
                m_id = m.get('id')
                if m_id:
                    # Para cada partido, consultamos sus estadísticas detalladas
                    stats = self.get_match_stats(m_id)
                    if stats:
                        history_stats.append(stats)
            
            return history_stats
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    def get_match_stats(self, match_id):
        """
        Consulta el endpoint de estadísticas detalladas de un partido.
        """
        url = f"{self.stats_base_url}/football/matches/{match_id}/stats"
        headers = {"Authorization": f"Bearer {self.stats_api_key}"}
        
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json().get('data', {})
                # Mapeamos los datos de la API a las llaves que nuestro modelo entiende
                # Nota: Ajustar estas llaves si la API usa nombres distintos (ej: 'shots_on_goal')
                return {
                    "shots_on_target": data.get('shots_on_target', 0),
                    "total_shots": data.get('total_shots', 0),
                    "corners": data.get('corners', 0),
                    "goals": data.get('goals', 0)
                }
        except:
            pass
        return None
