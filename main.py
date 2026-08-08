import os
import json
from engine.api_client import FootballDataClient
from engine.processor import DataProcessor
from engine.model import PredictionModel

def extract_team_info(data, side):
    """
    Busca de forma agresiva el ID y el nombre del equipo (home o away).
    Intenta múltiples combinaciones de llaves comunes en APIs de fútbol.
    """
    # Lista de posibles llaves para el objeto del equipo
    possible_keys = [f'{side}_team', side, f'{side}Team', side.capitalize()]
    
    for key in possible_keys:
        if key in data:
            team_info = data[key]
            # Si el objeto encontrado es un diccionario, buscamos dentro
            if isinstance(team_info, dict):
                # Intentamos encontrar el ID con diferentes nombres de llave
                t_id = team_info.get('id') or team_info.get('team_id') or team_info.get('id_team') or team_info.get('id')
                # Intentamos encontrar el nombre
                t_name = team_info.get('name') or team_info.get('team_name') or team_info.get('name_en')
                
                if t_id:
                    return t_id, t_name
    return None, None

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

    # --- BLOQUE DE DEBUG (CRUCIAL SI FALLA) ---
    # Esto imprimirá la estructura real en el log de GitHub Actions
    print("\n[DEBUG] Estructura de la respuesta de la API:")
    print(json.dumps(match_data, indent=2))
    print("-" * 30 + "\n")
    # -----------------------------------------

    # 2. Extraer información de los equipos usando el extractor universal
    team_a_id, team_a_name = extract_team_info(match_data, 'home')
    team_b_id, team_b_name = extract_team_info(match_data, 'away')

    if not team_a_id or not team_b_id:
        print("❌ ERROR: No se pudieron identificar los IDs de los equipos.")
        print("Revisa la sección [DEBUG] arriba para ver cómo vienen los datos.")
        return

    print(f"✅ Partido detectado: {team_a_name} vs {team_b_name}")
    print(f"   IDs: Local({team_a_id}) | Visitante({team_b_id})")

    # 3. Obtener historial
    print("\nCalculando promedios históricos...")
    hist_a = client.get_historical_team_data(team_a_id)
    hist_b = client.get_historical_team_data(team_b_id)

    avg_a = processor.calculate_averages(hist_a)
    avg_b = processor.calculate_averages(hist_b)

    if not avg_a or not avg_b:
        print("❌ Error: Datos insuficientes para calcular promedios.")
        print("Asegúrate de que los equipos tengan historial disponible en la API.")
        return

    # 4. Proyectar
    print("Ejecutando modelo de ML...")
    features = processor.prepare_features(avg_a, avg_b)
    predictions = model.predict_market(features)

    # 5. Resultados
    print(f"\n{'='*40}")
    print(f" PROYECCIÓN: {team_a_name} vs {team_b_name}")
    print(f"{'='*40}")
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
