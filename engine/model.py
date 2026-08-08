import math

class PredictionModel:
    def predict_market(self, features):
        results = {}
        markets = ['shots_on_target', 'total_shots', 'corners', 'goals']
        
        for m in markets:
            if f'{m}_total' not in features:
                continue
                
            pred_total = features[f'{m}_total']
            pred_max = features[f'{m}_max']
            
            # Líneas de apuesta profesionales (ajuste de 1.5 para seguridad)
            safe_under = math.floor((pred_total - 1.5) * 2) / 2
            safe_over = math.ceil((pred_total + 1.5) * 2) / 2

            results[m] = {
                "projection_total": round(pred_total, 2),
                "projection_max": round(pred_max, 2),
                "safe_under_line": max(0.0, safe_under),
                "safe_over_line": safe_over
            }
        return results
