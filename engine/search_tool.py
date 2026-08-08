import requests
import os

class IDFinder:
    def __init__(self):
        self.stats_api_key = os.getenv('THESTATSAPI_KEY')
        self.isports_api_key = os.getenv('ISPORTSAPI_KEY')
        self.stats_url = "https://api.thestatsapi.com/v1"
        self.isports_url = "https://api.isportsapi.com/v1"

    def search_thestats(self, team_name):
        print(f"\n--- Buscando en TheStatsAPI: '{team_name}' ---")
        # Nota: El endpoint exacto puede variar según la versión de la API, 
        # usualmente es /teams/search o /search/team
        try:
            params = {"name": team_name, "key": self.stats_api_key}
            response = requests.get(f"{self.stats_url}/teams/search", params=params)
            if response.status_code == 200:
                data = response.json()
                # Asumiendo que la API devuelve una lista de equipos
                teams = data.get('data', [])
                if not teams:
                    print("No se encontraron resultados.")
                for t in teams:
                    print(f"ID: {t.get('id')} | Nombre: {t.get('name')} | Liga: {t.get('league')}")
            else:
                print(f"Error en TheStatsAPI: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión en TheStatsAPI: {e}")

    def search_isports(self, team_name):
        print(f"\n--- Buscando en iSportsAPI: '{team_name}' ---")
        try:
            params = {"name": team_name, "key": self.isports_api_key}
            response = requests.get(f"{self.isports_url}/teams/search", params=params)
            if response.status_code == 200:
                data = response.json()
                teams = data.get('data', [])
                if not teams:
                    print("No se encontraron resultados.")
                for t in teams:
                    print(f"ID: {t.get('team_id')} | Nombre: {t.get('team_name')}")
            else:
                print(f"Error en iSportsAPI: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión en iSportsAPI: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python search_tool.py 'Nombre del Equipo'")
    else:
        name = sys.argv[1]
        finder = IDFinder()
        finder.search_thestats(name)
        finder.search_isports(name)
