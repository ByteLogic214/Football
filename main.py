import os
from engine.api_client import FootballDataClient
from engine.processor import DataProcessor
from engine.model import PredictionModel

def run_pipeline(match_id, team_a_id, team_b_id):
    print(f"--- Iniciando Proyección para Match ID: {match_id} ---")
    
    client = FootballDataClient()
    processor = DataProcessor()
    model = PredictionModel()

    # 1. Obtener datos reales
    print("Consultando APIs...")
    realtime_data, _ = client.get_realtime_stats(match_id)
    hist_a = client.get_historical_team_data(team_a_id)
    hist_b = client.get_historical_team_data(team_b_id)

    # 2. Procesar promedios
    print("Calculando promedios...")
    avg_a = processor.calculate_averages(hist_a)
    avg_b = processor.calculate_averages(hist_b)

    if not avg_a or not avg_b:
        print("Error: No se pudieron obtener datos históricos suficientes.")
        return

    # 3. Preparar features y proyectar
    print("Ejecutando modelo de ML...")
    features = processor.prepare_features(avg_a, avg_b)
    predictions = model.predict_market(features)

    # 4. Presentar resultados
    print("\n=== RESULTADOS DE PROYECCIÓN ===")
    for market, data in predictions.items():
        print(f"\nMercado: {market.upper()}")
        print(f"  - Proyección Total: {data['projection_total']}")
        print(f"  - Proyección Máximo Equipo: {data['projection_max']}")
        print(f"  - LÍNEA SEGURA (UNDER): < {data['safe_under_line']}")
        print(f"  - LÍNEA SEGURA (OVER): > {data['safe_over_line']}")

if __name__ == "__main__":
    # Estos IDs se pasarían por parámetros en GitHub Actions
    M_ID = os.getenv('MATCH_ID', '0')
    A_ID = os.getenv('TEAM_A_ID', '0')
    B_ID = os.getenv('TEAM_B_ID', '0')
    
    run_pipeline(M_ID, A_ID, B_ID)
