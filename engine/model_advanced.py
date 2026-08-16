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
        # Prior weight for Bayesian shrinkage toward league mean
        self.shrinkage_prior = 5.0
        # Cap for extreme team-level xG
        self.max_team_xg = 2.8
        # Smallest line step (half-goal increments)
        self.line_step = 0.5
    
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
    
    def _compute_safe_lines(self, projection, confidence_margin, min_lower=0.0, step=None):
        """
        Compute safe_over_line and safe_under_line so that:
          safe_over_line < projection < safe_under_line
        Lines are rounded to the nearest step (default: self.line_step).
        """
        if step is None:
            step = self.line_step
        # safe_over should be strictly less than projection
        safe_over = math.floor((projection - confidence_margin) / step) * step
        # safe_under should be strictly greater than projection
        safe_under = math.ceil((projection + confidence_margin) / step) * step
        # Ensure strict inequalities; adjust by one step if equal
        if safe_over >= projection:
            safe_over = projection - step
        if safe_under <= projection:
            safe_under = projection + step
        # Enforce minimum lower bound
        safe_over = max(min_lower, safe_over)
        return safe_over, safe_under
    
    def _shrink_toward_league(self, value, sample_size, league_mean):
        """
        Apply Bayesian shrinkage toward league_mean when sample_size is small
        """
        if sample_size is None or sample_size > self.shrinkage_prior:
            return value
        prior = self.shrinkage_prior
        n = max(0.0, float(sample_size))
        shrunk = (n * value + prior * league_mean) / (n + prior)
        return shrunk
    
    def predict_goals(self, features):
        """
        Predicción avanzada de goles con todas las features
        """
        # Predicción base (xG si está disponible, sino promedios)
        xg_home = features.get("xg_home")
        xg_away = features.get("xg_away")
        missing_xg_count = 0
        imputed_flag = False

        # League defaults
        league_team_xg = features.get("league_avg_team_xg", 1.25)
        league_conversion = features.get("league_avg_conversion", 0.12)

        # If xG missing, try to impute from shots on target
        if xg_home is None:
            shots_on_target_home = features.get("shots_on_target_home")
            if shots_on_target_home is not None:
                xg_home = shots_on_target_home * league_conversion
                imputed_flag = True
            else:
                missing_xg_count += 1
        if xg_away is None:
            shots_on_target_away = features.get("shots_on_target_away")
            if shots_on_target_away is not None:
                xg_away = shots_on_target_away * league_conversion
                imputed_flag = True
            else:
                missing_xg_count += 1

        # Fall back to raw goals averages only if we absolutely have no xG nor shots
        if xg_home is None and xg_away is None:
            base_home = features.get("goals_home", 1.5)
            base_away = features.get("goals_away", 1.0)
        else:
            base_home = xg_home if xg_home is not None else features.get("goals_home", 1.25)
            base_away = xg_away if xg_away is not None else features.get("goals_away", 1.0)

        # Apply shrinkage toward league mean when sample sizes are small
        sample_home = features.get("sample_size_home")
        sample_away = features.get("sample_size_away")
        base_home = self._shrink_toward_league(base_home, sample_home, league_team_xg)
        base_away = self._shrink_toward_league(base_away, sample_away, league_team_xg)

        # Cap extreme team-level xG for realism
        base_home = min(base_home, self.max_team_xg)
        base_away = min(base_away, self.max_team_xg)

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

        # Final projection
        total_prediction = adjusted_home + adjusted_away

        # Compute confidence and apply penalty for missing data
        consistency_avg = (
            features.get("consistency_home_off", 0.5) + 
            features.get("consistency_away_off", 0.5)
        ) / 2
        # Base confidence based on consistency
        base_confidence = consistency_avg
        # Penalize missing xG but less severely if we imputed
        penalty = 0.0
        if missing_xg_count > 0:
            penalty += 0.06 * missing_xg_count  # 6% per truly missing xG
        if imputed_flag:
            penalty += 0.03  # small penalty for imputed xG
        confidence_level = max(0.0, base_confidence * (1 - penalty))

        # Confidence margin used to set safe lines
        confidence_margin = 1.5 - (consistency_avg * 0.5)
        safe_over, safe_under = self._compute_safe_lines(total_prediction, confidence_margin, min_lower=0.5)

        return {
            "goals_home_prediction": round(adjusted_home, 2),
            "goals_away_prediction": round(adjusted_away, 2),
            "goals_total_prediction": round(total_prediction, 2),
            "goals_home_base": round(base_home, 2),
            "goals_away_base": round(base_away, 2),
            "confidence_level": round(confidence_level * 100, 1),
            "safe_under_line": safe_under,
            "safe_over_line": safe_over
        }
    
    def predict_market(self, features):
        """
        Predicción completa de todos los mercados con features avanzadas
        """
        results = {}
        markets = ['shots_on_target', 'total_shots', 'corners', 'goals']
        
        # Predicción especial para goles usando modelo avanzado
        if 'goals_home' in features or 'xg_home' in features or 'goals_away' in features or 'xg_away' in features:
            goals_pred = self.predict_goals(features)
            pred_total = goals_pred["goals_total_prediction"]
            pred_home = goals_pred["goals_home_prediction"]
            pred_away = goals_pred["goals_away_prediction"]
            
            results['goals'] = {
                "projection_total": pred_total,
                "projection_home": pred_home,
                "projection_away": pred_away,
                "projection_max": max(pred_home, pred_away),
                "safe_under_line": goals_pred["safe_under_line"],
                "safe_over_line": goals_pred["safe_over_line"],
                "confidence_level": goals_pred.get("confidence_level", round(((features.get("consistency_home_off", 0.5) + features.get("consistency_away_off", 0.5))/2)*100, 1)),
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
            safe_over, safe_under = self._compute_safe_lines(pred_total_adj, confidence_margin, min_lower=0.0)
            
            results[m] = {
                "projection_total": round(pred_total_adj, 2),
                "projection_home": round(pred_home * form_mult, 2),
                "projection_away": round(pred_away * form_mult, 2),
                "projection_max": round(max(pred_home, pred_away) * form_mult, 2),
                "safe_under_line": safe_under,
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
                            # safe_over is intentionally below projection (safer over bet)
                            "bet": f"UNDER {pred['safe_over_line']}",
                            "confidence": bet_confidence,
                            "risk": risk_level,
                            "reason": f"Proyección: {total} goles. Alta consistencia defensiva."
                        })
                    elif total > 3.2:
                        recommendations.append({
                            "market": "Goles Totales",
                            # safe_under is intentionally above projection (safer under bet)
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
