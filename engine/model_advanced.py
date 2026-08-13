import math

class AdvancedPredictionModel:
    """
    Modelo de predicción avanzado que utiliza las nuevas features
    para mejorar la precisión de las proyecciones
    """
    
    def __init__(self):
        # Pesos para ajustes basados en features avanzadas
        self.weights = {
            "form": 0.15,
            "fatigue": 0.10,
            "home_advantage": 0.12,
            "consistency": 0.08,
            "h2h": 0.10,
            "xg": 0.20,
            "base": 0.25
        }
    
    def _apply_form_adjustment(self, base_prediction, features):
        """Ajusta predicción según forma reciente"""
        form_advantage = features.get("form_advantage", 0)
        
        # Equipo con mejor forma reciente tiene ventaja
        adjustment = form_advantage * 0.1  # +/- 0.3 máximo aprox
        return adjustment
    
    def _apply_fatigue_adjustment(self, base_prediction, features, is_home=True):
        """Ajusta por fatiga acumulada"""
        fatigue_key = "fatigue_home" if is_home else "fatigue_away"
        fatigue = features.get(fatigue_key, 0)
        
        # Alta fatiga reduce rendimiento
        penalty = (fatigue / 10) * 0.15  # Hasta -15% del rendimiento
        return -penalty * base_prediction
    
    def _apply_home_advantage(self, base_prediction, features):
        """Aplica ventaja de localía ajustada"""
        home_index = features.get("home_advantage_index", 1.0)
        goals_boost = features.get("home_goals_boost", 1.0)
        
        # Boost combinado para equipo local
        boost = ((home_index - 1) * 0.5 + (goals_boost - 1) * 0.3)
        return boost * base_prediction
    
    def _apply_consistency_adjustment(self, base_prediction, features, is_home=True):
        """Ajusta por consistencia del equipo"""
        if is_home:
            consistency = features.get("consistency_home_off", 0.5)
        else:
            consistency = features.get("consistency_away_off", 0.5)
        
        # Mayor consistencia = predicción más confiable (menor ajuste)
        # Menor consistencia = mayor variabilidad
        variance_factor = 1 - consistency
        return base_prediction * (1 + variance_factor * 0.1)
    
    def _apply_h2h_adjustment(self, base_prediction, features):
        """Ajusta según historial directo"""
        h2h_matches = features.get("h2h_matches", 0)
        
        if h2h_matches < 3:
            return 0  # No suficiente historial
        
        dominance = features.get("h2h_dominance", 0)
        h2h_goals = features.get("h2h_avg_goals_home", 0)
        
        # Ajuste basado en dominio histórico
        adjustment = dominance * 0.15 + (h2h_goals * 0.05)
        return adjustment
    
    def predict_goals(self, features):
        """
        Predicción avanzada de goles con todas las features
        """
        # Predicción base (xG si está disponible, sino promedios)
        xg_home = features.get("xg_home")
        xg_away = features.get("xg_away")
        
        if xg_home is not None and xg_away is not None:
            base_home = xg_home
            base_away = xg_away
        else:
            base_home = features.get("goals_home", 1.5)
            base_away = features.get("goals_away", 1.0)
        
        # Aplicar ajustes progresivos
        adjusted_home = base_home
        adjusted_away = base_away
        
        # 1. Forma reciente
        form_adj = self._apply_form_adjustment(base_home, features)
        adjusted_home += form_adj * self.weights["form"]
        adjusted_away -= form_adj * self.weights["form"]
        
        # 2. Fatiga
        fatigue_home = self._apply_fatigue_adjustment(adjusted_home, features, True)
        fatigue_away = self._apply_fatigue_adjustment(adjusted_away, features, False)
        adjusted_home += fatigue_home * self.weights["fatigue"]
        adjusted_away += fatigue_away * self.weights["fatigue"]
        
        # 3. Ventaja de localía
        home_boost = self._apply_home_advantage(adjusted_home, features)
        adjusted_home += home_boost * self.weights["home_advantage"]
        
        # 4. Head-to-Head
        h2h_adj = self._apply_h2h_adjustment(adjusted_home, features)
        adjusted_home += h2h_adj * self.weights["h2h"]
        adjusted_away -= h2h_adj * self.weights["h2h"]
        
        # 5. Consistencia (afecta el rango de confianza)
        adjusted_home = self._apply_consistency_adjustment(adjusted_home, features, True)
        adjusted_away = self._apply_consistency_adjustment(adjusted_away, features, False)
        
        # Asegurar valores mínimos razonables
        adjusted_home = max(0.5, adjusted_home)
        adjusted_away = max(0.3, adjusted_away)
        
        return {
            "goals_home_prediction": round(adjusted_home, 2),
            "goals_away_prediction": round(adjusted_away, 2),
            "goals_total_prediction": round(adjusted_home + adjusted_away, 2),
            "goals_home_base": round(base_home, 2),
            "goals_away_base": round(base_away, 2)
        }
    
    def predict_market(self, features):
        """
        Predicción completa de todos los mercados con features avanzadas
        """
        results = {}
        markets = ['shots_on_target', 'total_shots', 'corners', 'goals']
        
        # Predicción especial para goles usando modelo avanzado
        if 'goals_home' in features or 'xg_home' in features:
            goals_pred = self.predict_goals(features)
            
            pred_total = goals_pred["goals_total_prediction"]
            pred_home = goals_pred["goals_home_prediction"]
            pred_away = goals_pred["goals_away_prediction"]
            
            # Calcular niveles de confianza basados en consistencia
            consistency_avg = (
                features.get("consistency_home_off", 0.5) + 
                features.get("consistency_away_off", 0.5)
            ) / 2
            
            # Mayor consistencia = líneas más ajustadas
            confidence_margin = 1.5 - (consistency_avg * 0.5)
            
            safe_under = math.floor((pred_total - confidence_margin) * 2) / 2
            safe_over = math.ceil((pred_total + confidence_margin) * 2) / 2
            
            results['goals'] = {
                "projection_total": pred_total,
                "projection_home": pred_home,
                "projection_away": pred_away,
                "projection_max": max(pred_home, pred_away),
                "safe_under_line": max(0.5, safe_under),
                "safe_over_line": safe_over,
                "confidence_level": round(consistency_avg * 100, 1),
                "adjustments_applied": {
                    "form_impact": round(
                        features.get("form_advantage", 0) * self.weights["form"], 2
                    ),
                    "fatigue_impact": round(
                        features.get("fatigue_diff", 0) * self.weights["fatigue"] * -0.1, 2
                    ),
                    "home_advantage_impact": round(
                        (features.get("home_advantage_index", 1) - 1) * self.weights["home_advantage"], 2
                    ),
                    "h2h_impact": round(
                        features.get("h2h_dominance", 0) * self.weights["h2h"], 2
                    )
                }
            }
        
        # Otros mercados con ajustes similares
        for m in ['shots_on_target', 'total_shots', 'corners']:
            if f'{m}_total' not in features:
                continue
            
            pred_total = features[f'{m}_total']
            pred_home = features.get(f'{m}_home', pred_total / 2)
            pred_away = features.get(f'{m}_away', pred_total / 2)
            
            # Aplicar ajustes ligeros de forma y fatiga
            form_mult = 1 + (features.get("form_advantage", 0) * 0.05)
            fatigue_mult = 1 - (abs(features.get("fatigue_diff", 0)) * 0.02)
            
            pred_total_adj = pred_total * form_mult * fatigue_mult
            
            consistency_avg = (
                features.get("consistency_home_off", 0.5) + 
                features.get("consistency_away_off", 0.5)
            ) / 2
            
            confidence_margin = 1.5 - (consistency_avg * 0.5)
            
            safe_under = math.floor((pred_total_adj - confidence_margin) * 2) / 2
            safe_over = math.ceil((pred_total_adj + confidence_margin) * 2) / 2
            
            results[m] = {
                "projection_total": round(pred_total_adj, 2),
                "projection_home": round(pred_home * form_mult, 2),
                "projection_away": round(pred_away * form_mult, 2),
                "projection_max": round(max(pred_home, pred_away) * form_mult, 2),
                "safe_under_line": max(0.0, safe_under),
                "safe_over_line": safe_over,
                "confidence_level": round(consistency_avg * 100, 1)
            }
        
        return results
    
    def generate_betting_recommendations(self, predictions, features):
        """
        Genera recomendaciones de apuestas basadas en confianza
        """
        recommendations = []
        
        for market, pred in predictions.items():
            confidence = pred.get("confidence_level", 50)
            
            if confidence >= 70:
                risk_level = "BAJO"
                bet_confidence = "ALTA"
            elif confidence >= 55:
                risk_level = "MEDIO"
                bet_confidence = "MEDIA"
            else:
                risk_level = "ALTO"
                bet_confidence = "BAJA"
            
            # Recomendaciones específicas
            if market == "goals":
                total = pred["projection_total"]
                
                if confidence >= 65:
                    if total < 2.3:
                        recommendations.append({
                            "market": "Goles Totales",
                            "bet": f"UNDER {pred['safe_over_line']}",
                            "confidence": bet_confidence,
                            "risk": risk_level,
                            "reason": f"Proyección: {total} goles. Alta consistencia defensiva."
                        })
                    elif total > 3.2:
                        recommendations.append({
                            "market": "Goles Totales",
                            "bet": f"OVER {pred['safe_under_line']}",
                            "confidence": bet_confidence,
                            "risk": risk_level,
                            "reason": f"Proyección: {total} goles. Equipos ofensivos en forma."
                        })
                
                # Ambos equipos marcan
                if pred["projection_home"] >= 1.0 and pred["projection_away"] >= 1.0:
                    recommendations.append({
                        "market": "Ambos Equipos Marcan",
                        "bet": "SÍ",
                        "confidence": bet_confidence,
                        "risk": risk_level,
                        "reason": f"Local: {pred['projection_home']}, Visitante: {pred['projection_away']}"
                    })
            
            elif market == "corners" and confidence >= 60:
                recommendations.append({
                    "market": "Corners",
                    "bet": f"Rango {pred['safe_under_line']}-{pred['safe_over_line']}",
                    "confidence": bet_confidence,
                    "risk": risk_level,
                    "reason": f"Proyección: {pred['projection_total']} corners totales"
                })
        
        return recommendations
