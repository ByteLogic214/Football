import os
from engine.api_client import FootballDataClient
from engine.processor import DataProcessor
from engine.model import PredictionModel

def run_pipeline(match_id):
    print(f"--- Iniciando Proyección Automática para Match ID: {match_id} ---")
    
    client = FootballDataClient()
    processor = DataProcessor()
    model = PredictionModel()

    # 1. Obtener detalles del partido
    print("Obteniendo detalles del partido...")
    match_data = client.get_match_details(match_id)
    
    if not match_data:
        print("Error: No se pudo obtener la información del partido. Verifica el ID.")
        return

    # Extraer IDs de equipos (ajustado a la estructura probable de la API)
    # Si la API devuelve los equipos en una estructura distinta, esto se ajustará
    home_team = match_data.get('home_team') or match_data.get('home') or {}
    away_team = match_data.get('away_team') or match_data.get('away') or {}
    
    team_a_id = home_team.get('id')
    team_b_id = away_team.get('id')
    team_a_name = home_team.get('name') or home_team.get('team_name') or "Local"
    team_b_name = away_team.get('name') or away_team.get('team_name') or "Visitante"

    if not team_a_id or not team_b_id:
        print("Error: No se pudieron identificar los IDs de los equipos en este partido.")
        return

    print(f"Partido detectado: {team_a_name} vs {team_b_name}")

    # 2. Obtener historial
    print("Calculando promedios históricos...")
    hist_a = client.get_historical_team_data(team_a_id)
    hist_b = client.get_historical_team_data(team_b_id)

    avg_a = processor.calculate_averages(hist_a)
    avg_b = processor.calculate_averages(hist_b)

    if not avg_a or not avg_b:
        print("Error: Datos insuficientes para calcular promedios. Verifica que los equipos tengan historial.")
        return

    # 3. Proyectar
    print("Ejecutando modelo de ML...")
    features = processor.prepare_features(avg_a, avg_b)
    predictions = model.predict_market(features)

    # 4. Resultados
    print(f"\n=== PROYECCIÓN: {team_a_name} vs {team_b_name} ===")
    for market, data in predictions.items():
        print(f"\nMercado: {market.upper()}")
        print(f"  - Proyección Total: {data['projection_total']}")
        print(f"  - Proyección Máximo Equipo: {data['projection_max']}")
        print(f"  - LÍNEA SEGURA (UNDER): < {data['safe_under_line']}")
        print(f"  - LÍNEA SEGURA (OVER): > {data['safe_over_line']}")

if __name__ == "__main__":
    M_ID = os.getenv('MATCH_ID')
    if not M_ID or M_ID == '0':
        print("Error: Debes proporcionar un MATCH_ID.")
    else:
        run_pipeline(M_ID)
