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
    response = client.get_match_details(match_id)
    if not response:
        print("Error: No se pudo obtener la respuesta de la API.")
        return

    match_data = response.get('data', response)

    # Extraer IDs y Fecha
    team_a_id = match_data.get('home_team', {}).get('id')
    team_b_id = match_data.get('away_team', {}).get('id')
    team_a_name = match_data.get('home_team', {}).get('name', 'Local')
    team_b_name = match_data.get('away_team', {}).get('name', 'Visitante')
    match_date = match_data.get('utc_date', '').split('T')[0]

    if not team_a_id or not team_b_id:
        print("Error: No se pudieron identificar los equipos.")
        return

    print(f"✅ Partido: {team_a_name} vs {team_b_name} ({match_date})")

    # 2. Obtener historial con la nueva lógica de fecha y parámetros
    print("\nRecopilando estadísticas históricas detalladas...")
    hist_a = client.get_historical_team_data(team_a_id, match_date)
    hist_b = client.get_historical_team_data(team_b_id, match_date)

    # 3. Calcular promedios pasando el ID para distinguir Home/Away
    print(f"Procesando {len(hist_a)} partidos de {team_a_name} y {len(hist_b)} de {team_b_name}...")
    avg_a = processor.calculate_averages(hist_a, team_a_id)
    avg_b = processor.calculate_averages(hist_b, team_b_id)

    if not avg_a or not avg_b:
        print("❌ Error: No se pudieron calcular promedios. Verifica que los equipos tengan partidos terminados con estadísticas.")
        return

    # 4. Proyectar
    print("Ejecutando modelo de ML...")
    features = processor.prepare_features(avg_a, avg_b)
    predictions = model.predict_market(features)

    # 5. Resultados
    print(f"\n{'='*45}")
    print(f" PROYECCIÓN: {team_a_name} vs {team_b_name}")
    print(f"{'='*45}")
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
