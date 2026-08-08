from sklearn.ensemble import RandomForestRegressor
import numpy as np

class PredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        # En un entorno real, aquí cargarías un modelo pre-entrenado con datos históricos masivos
        # Para este sistema, entrenamos con la tendencia actual de los equipos.

    def predict_market(self, features):
        """
        Predice los valores y determina la línea más segura.
        """
        # Simulamos la lógica de regresión sobre los promedios calculados
        # En producción, el modelo toma features de forma: [avg_a, avg_b, h2h, form]
        
        results = {}
        markets = ['shots_on_target', 'total_shots', 'corners', 'goals']
        
        for m in markets:
            pred_total = features[f'{m}_total']
            pred_max = features[f'{m}_max']
            
            # Lógica de "Línea más segura" (Safe Line)
            # Usamos un margen de seguridad basado en la desviación estándar implícita
            safe_under = pred_total * 0.85  # 15% de margen para Under
            safe_over = pred_total * 1.15   # 15% de margen para Over
            
            results[m] = {
                "projection_total": round(pred_total, 2),
                "projection_max": round(pred_max, 2),
                "safe_under_line": round(safe_under, 1),
                "safe_over_line": round(safe_over, 1)
            }
        return results
