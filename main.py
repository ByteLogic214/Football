import os
import json
from engine.api_client import FootballDataClient
from engine.processor import DataProcessor
from engine.model import PredictionModel

def extract_team_info(data, side):
    possible_keys = [f'{side}_team', side, f'{side}Team', side.capitalize()]
    for key in possible_keys:
        if key in data:
            team_info = data[key]
            if isinstance(team_info, dict):
                t_id = team_info.get('id') or team_info.get('team_id')
                t_name = team_info.get('name') or team_info.get('team_name')
                if t_id: return str(t_id), t_name
    return None, None

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

    if isinstance(response, dict) and 'data' in response:
        match_data = response['data']
    else:
        match_data = response

    # EXTRAER FECHA PARA EL HISTORIAL (Formato YYYY-MM-DD)
    # La API devuelve "2026-08-09T00:45:00.000Z", tomamos solo la parte de la fecha
    utc_date_full = match_data.get('utc_date', '')
    match_date = utc_date_full.split('T')[0] if utc_date_full else ""

    # 2. Extraer información de los equipos
    team_a_id, team_a_name = extract_team_info(match_data, 'home')
    team_b_id, team_b_name = extract_team_info(match_data, 'away')

    if not team_a_id or not team_b_id:
        print("❌ ERROR: No se pudieron identificar los IDs de los equipos.")
        return

    print(f"✅ Partido detectado: {team_a_name} vs {team_b_name}")
    print(f"   Fecha del partido: {match_date}")

    # 3. Obtener historial usando la nueva lógica de fecha y búsqueda de partidos
    print("\nRecopilando estadísticas de partidos anteriores...")
    hist_a = client.get_historical_team_data(team_a_id, match_date)
    hist_b = client.get_historical_team_data(team_b_id, match_date)

    if not hist_a or not hist_b:
        print(f"❌ Error: Datos insuficientes. Historial A: {len(hist_a)} partidos, Historial B: {len(hist_b)} partidos.")
        return

    # 4. Procesar y Proyectar
    print(f"Calculando promedios con {len(hist_a)} partidos de {team_a_name} y {len(hist_b)} de {team_b_name}...")
    avg_a = processor.calculate_averages(hist_a)
    avg_b = processor.calculate_averages(hist_b)

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
