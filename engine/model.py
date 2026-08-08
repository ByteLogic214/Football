import math

class PredictionModel:
    def __init__(self):
        pass

    def predict_market(self, features):
        results = {}
        markets = ['shots_on_target', 'total_shots', 'corners', 'goals']
        
        for m in markets:
            pred_total = features[f'{m}_total']
            pred_max = features[f'{m}_max']
            
            # LÓGICA DE LÍNEA SEGURA PROFESIONAL
            # En lugar de %, usamos un margen de seguridad basado en la volatilidad
            # Para mercados de fútbol, un margen de 1.5 o 2.0 es más realista que un %
            
            if pred_total == 0:
                safe_under = 0.0
                safe_over = 0.0
            else:
                # El Under seguro es la proyección menos un margen de seguridad
                # El Over seguro es la proyección más un margen de seguridad
                # Redondeamos a la línea de apuesta más cercana (.5)
                safe_under = math.floor((pred_total - 1.5) * 2) / 2
                safe_over = math.ceil((pred_total + 1.5) * 2) / 2

            # Asegurar que las líneas no sean negativas
            safe_under = max(0.0, safe_under)

            results[m] = {
                "projection_total": round(pred_total, 2),
                "projection_max": round(pred_max, 2),
                "safe_under_line": safe_under,
                "safe_over_line": safe_over
            }
        return results
