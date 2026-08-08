import requests
import os
import time  # IMPORTANTE: Para controlar la velocidad

class FootballDataClient:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.base_url = "https://api.thestatsapi.com/api"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.stats_api_key}"})

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            # Si recibimos un 429, lanzamos una excepción para manejarla en el bucle
            if response.status_code == 429:
                raise requests.exceptions.HTTPError("429 Client Error: Too Many Requests")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error en llamada a {endpoint}: {e}")
            return None

    def get_match_details(self, match_id):
        return self.get(f"/football/matches/{match_id}")

    def get_historical_team_data(self, team_id, match_date):
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

        print(f"[API] Se encontraron {len(matches)} partidos. Iniciando recolección de estadísticas...")

        for index, match in enumerate(matches):
            match_id = match.get("id")
            if not match_id:
                continue

            # --- ESTRATEGIA DE CONTROL DE VELOCIDAD ---
            # 1. Pausa pequeña entre cada partido para evitar el 429
            time.sleep(0.5) 

            # 2. Intentar obtener estadísticas con reintento en caso de 429
            stats_data = self._get_stats_with_retry(match_id)
            
            if stats_data:
                history.append({
                    "match": match,
                    "stats": stats_data
                })
            
            # Feedback visual para saber que el proceso sigue vivo
            if (index + 1) % 5 == 0:
                print(f"   > Procesados {index + 1}/{len(matches)} partidos...")

        return history

    def _get_stats_with_retry(self, match_id, retries=3, backoff=5):
        """
        Intenta obtener estadísticas. Si recibe un 429, espera y reintenta.
        """
        for i in range(retries):
            try:
                stats_response = self.get(f"/football/matches/{match_id}/stats")
                
                if stats_response and stats_response.get("data"):
                    return stats_response["data"]
                return None

            except requests.exceptions.HTTPError as e:
                if "429" in str(e):
                    wait_time = backoff * (i + 1)
                    print(f"⚠️ Rate Limit (429) detectado en partido {match_id}. Esperando {wait_time}s para reintentar...")
                    time.sleep(wait_time)
                else:
                    # Si es un 404, no reintentamos, simplemente saltamos el partido
                    return None
            except Exception:
                return None
        return None
