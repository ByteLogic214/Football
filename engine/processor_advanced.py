import math
from datetime import datetime, timedelta
from collections import defaultdict

class AdvancedDataProcessor:
    """
    Procesador avanzado de datos con métricas de rendimiento reciente,
    fatiga, ventaja de localía, xG, head-to-head y consistencia.
    """
    
    def __init__(self):
        self.last_n_matches = 5  # Para forma reciente
        self.h2h_lookback_years = 3
        
    def _value_or_none(self, value):
        """Validación segura de valores numéricos"""
        return value if isinstance(value, (int, float)) else None

    def _extract_stats(self, match, stats, team_id):
        """Extracción mejorada con más métricas"""
        match = match or {}
        stats = stats or {}

        home_team = match.get("home_team") or {}
        away_team = match.get("away_team") or {}
        
        home_id = str(home_team.get("id"))
        away_id = str(away_team.get("id"))
        is_home = str(team_id) == home_id
        side = "home" if is_home else "away"
        opp_side = "away" if is_home else "home"

        score = match.get("score") or {}
        overview = stats.get("overview") or {}

        def get_stat_value(stat_name, side_key=side):
            stat_obj = overview.get(stat_name) or {}
            all_obj = stat_obj.get("all") or {}
            return self._value_or_none(all_obj.get(side_key))

        # Extraer métricas básicas y avanzadas
        goals_for = self._value_or_none(score.get(side))
        goals_against = self._value_or_none(score.get(opp_side))
        
        return {
            # Métricas básicas
            "goals": goals_for,
            "goals_conceded": goals_against,
            "corners": get_stat_value("corner_kicks"),
            "shots_on_target": get_stat_value("shots_on_target"),
            "total_shots": get_stat_value("total_shots"),
            
            # Métricas adicionales para xG
            "possession": get_stat_value("ball_possession"),
            "passes_completed": get_stat_value("passes_completed"),
            "passes_total": get_stat_value("total_passes"),
            "attacks": get_stat_value("attacks"),
            "dangerous_attacks": get_stat_value("dangerous_attacks"),
            
            # Datos del partido
            "is_home": is_home,
            "match_date": match.get("utc_date", ""),
            "opponent_id": away_id if is_home else home_id,
            
            # Resultado del partido (para forma reciente)
            "result": self._determine_result(goals_for, goals_against),
            "points": self._calculate_points(goals_for, goals_against)
        }

    def _determine_result(self, goals_for, goals_against):
        """Determina W/D/L"""
        if goals_for is None or goals_against is None:
            return None
        if goals_for > goals_against:
            return "W"
        elif goals_for < goals_against:
            return "L"
        return "D"

    def _calculate_points(self, goals_for, goals_against):
        """Calcula puntos de liga (3-1-0)"""
        result = self._determine_result(goals_for, goals_against)
        if result == "W":
            return 3
        elif result == "D":
            return 1
        return 0

    def calculate_xg(self, shots_on_target, total_shots, dangerous_attacks, possession):
        """
        Cálculo simplificado de Expected Goals (xG)
        Fórmula basada en calidad de ocasiones
        """
        if not all([shots_on_target, total_shots, dangerous_attacks]):
            return None
            
        # Factores de calidad
        shot_quality = shots_on_target / total_shots if total_shots > 0 else 0
        danger_factor = dangerous_attacks / 100 if dangerous_attacks else 0
        possession_factor = (possession / 100) if possession else 0.5
        
        # Fórmula de xG simplificada
        xg = (shots_on_target * 0.35 * shot_quality + 
              dangerous_attacks * 0.08 * possession_factor)
        
        return round(xg, 2)

    def calculate_recent_form(self, history, team_id, n_matches=5):
        """
        Calcula la forma reciente de los últimos N partidos
        Retorna: puntos promedio, goles a favor/contra, racha
        """
        if not history or len(history) < 1:
            return None
            
        recent = history[:min(n_matches, len(history))]
        
        total_points = 0
        total_gf = 0
        total_ga = 0
        wins = 0
        draws = 0
        losses = 0
        
        for item in recent:
            extracted = self._extract_stats(
                item.get("match"), 
                item.get("stats"), 
                team_id
            )
            
            if extracted.get("points") is not None:
                total_points += extracted["points"]
                
            if extracted.get("goals") is not None:
                total_gf += extracted["goals"]
                
            if extracted.get("goals_conceded") is not None:
                total_ga += extracted["goals_conceded"]
            
            result = extracted.get("result")
            if result == "W":
                wins += 1
            elif result == "D":
                draws += 1
            elif result == "L":
                losses += 1
        
        n_valid = len(recent)
        
        return {
            "avg_points": round(total_points / n_valid, 2) if n_valid > 0 else 0,
            "avg_goals_for": round(total_gf / n_valid, 2) if n_valid > 0 else 0,
            "avg_goals_against": round(total_ga / n_valid, 2) if n_valid > 0 else 0,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "matches_played": n_valid,
            "goal_difference": round((total_gf - total_ga) / n_valid, 2) if n_valid > 0 else 0
        }

    def calculate_fatigue(self, history, reference_date):
        """
        Calcula índice de fatiga basado en:
        - Densidad de partidos en últimos 7/14/21 días
        - Distancia de viajes (si juega de visitante)
        """
        if not history or not reference_date:
            return {"fatigue_index": 0, "matches_last_7d": 0, "matches_last_14d": 0}
        
        try:
            ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
        except:
            return {"fatigue_index": 0, "matches_last_7d": 0, "matches_last_14d": 0}
        
        matches_7d = 0
        matches_14d = 0
        matches_21d = 0
        away_matches_14d = 0
        
        for item in history:
            match_date_str = item.get("match", {}).get("utc_date", "")
            if not match_date_str:
                continue
                
            try:
                match_date = datetime.strptime(match_date_str.split('T')[0], "%Y-%m-%d")
                days_diff = (ref_date - match_date).days
                
                if days_diff < 0:  # Partido futuro
                    continue
                    
                if days_diff <= 7:
                    matches_7d += 1
                if days_diff <= 14:
                    matches_14d += 1
                    # Contar partidos de visitante
                    extracted = self._extract_stats(
                        item.get("match"), 
                        item.get("stats"), 
                        item.get("team_id")
                    )
                    if not extracted.get("is_home"):
                        away_matches_14d += 1
                        
                if days_diff <= 21:
                    matches_21d += 1
                    
            except:
                continue
        
        # Índice de fatiga (0-10, donde 10 es máxima fatiga)
        fatigue = (
            matches_7d * 2.5 +  # Partidos muy recientes pesan más
            matches_14d * 1.0 +
            away_matches_14d * 0.5  # Viajes añaden fatiga
        )
        
        return {
            "fatigue_index": min(round(fatigue, 2), 10),
            "matches_last_7d": matches_7d,
            "matches_last_14d": matches_14d,
            "matches_last_21d": matches_21d,
            "away_matches_14d": away_matches_14d
        }

    def calculate_home_advantage(self, history, team_id):
        """
        Calcula ventaja de localía ajustada
        Compara rendimiento en casa vs fuera
        """
        if not history:
            return None
            
        home_stats = {"goals": [], "goals_conceded": [], "points": []}
        away_stats = {"goals": [], "goals_conceded": [], "points": []}
        
        for item in history:
            extracted = self._extract_stats(
                item.get("match"), 
                item.get("stats"), 
                team_id
            )
            
            stats_dict = home_stats if extracted.get("is_home") else away_stats
            
            if extracted.get("goals") is not None:
                stats_dict["goals"].append(extracted["goals"])
            if extracted.get("goals_conceded") is not None:
                stats_dict["goals_conceded"].append(extracted["goals_conceded"])
            if extracted.get("points") is not None:
                stats_dict["points"].append(extracted["points"])
        
        def avg(lst):
            return sum(lst) / len(lst) if lst else 0
        
        home_avg_goals = avg(home_stats["goals"])
        away_avg_goals = avg(away_stats["goals"])
        home_avg_points = avg(home_stats["points"])
        away_avg_points = avg(away_stats["points"])
        
        # Factor de ventaja (ratio casa/fuera)
        goals_advantage = (home_avg_goals / away_avg_goals) if away_avg_goals > 0 else 1.0
        points_advantage = (home_avg_points / away_avg_points) if away_avg_points > 0 else 1.0
        
        return {
            "home_goals_avg": round(home_avg_goals, 2),
            "away_goals_avg": round(away_avg_goals, 2),
            "home_points_avg": round(home_avg_points, 2),
            "away_points_avg": round(away_avg_points, 2),
            "goals_advantage_ratio": round(goals_advantage, 2),
            "points_advantage_ratio": round(points_advantage, 2),
            "home_advantage_index": round((goals_advantage + points_advantage) / 2, 2)
        }

    def calculate_head_to_head(self, history_a, history_b, team_a_id, team_b_id):
        """
        Analiza historial de enfrentamientos directos
        """
        h2h_matches = []
        
        # Buscar partidos entre ambos equipos
        for item in history_a:
            match = item.get("match", {})
            opponent_id = None
            
            home_id = str(match.get("home_team", {}).get("id"))
            away_id = str(match.get("away_team", {}).get("id"))
            
            if str(team_a_id) == home_id and str(team_b_id) == away_id:
                opponent_id = team_b_id
            elif str(team_a_id) == away_id and str(team_b_id) == home_id:
                opponent_id = team_b_id
                
            if opponent_id:
                extracted = self._extract_stats(
                    match, 
                    item.get("stats"), 
                    team_a_id
                )
                h2h_matches.append(extracted)
        
        if not h2h_matches:
            return {
                "matches_played": 0,
                "team_a_wins": 0,
                "draws": 0,
                "team_b_wins": 0,
                "avg_goals_team_a": 0,
                "avg_goals_team_b": 0
            }
        
        wins_a = sum(1 for m in h2h_matches if m.get("result") == "W")
        draws = sum(1 for m in h2h_matches if m.get("result") == "D")
        losses_a = sum(1 for m in h2h_matches if m.get("result") == "L")
        
        avg_gf = sum(m.get("goals", 0) for m in h2h_matches) / len(h2h_matches)
        avg_ga = sum(m.get("goals_conceded", 0) for m in h2h_matches) / len(h2h_matches)
        
        return {
            "matches_played": len(h2h_matches),
            "team_a_wins": wins_a,
            "draws": draws,
            "team_b_wins": losses_a,
            "avg_goals_team_a": round(avg_gf, 2),
            "avg_goals_team_b": round(avg_ga, 2),
            "dominance_index": round((wins_a - losses_a) / len(h2h_matches), 2)
        }

    def calculate_consistency(self, history, team_id):
        """
        Calcula consistencia ofensiva y defensiva
        Usa desviación estándar de goles
        """
        if not history:
            return None
            
        goals_for = []
        goals_against = []
        
        for item in history:
            extracted = self._extract_stats(
                item.get("match"), 
                item.get("stats"), 
                team_id
            )
            
            if extracted.get("goals") is not None:
                goals_for.append(extracted["goals"])
            if extracted.get("goals_conceded") is not None:
                goals_against.append(extracted["goals_conceded"])
        
        def std_dev(lst):
            if len(lst) < 2:
                return 0
            mean = sum(lst) / len(lst)
            variance = sum((x - mean) ** 2 for x in lst) / len(lst)
            return math.sqrt(variance)
        
        offensive_std = std_dev(goals_for)
        defensive_std = std_dev(goals_against)
        
        # Consistencia: menor desviación = mayor consistencia (inverso normalizado)
        offensive_consistency = round(1 / (1 + offensive_std), 2)
        defensive_consistency = round(1 / (1 + defensive_std), 2)
        
        return {
            "offensive_std": round(offensive_std, 2),
            "defensive_std": round(defensive_std, 2),
            "offensive_consistency": offensive_consistency,
            "defensive_consistency": defensive_consistency,
            "overall_consistency": round((offensive_consistency + defensive_consistency) / 2, 2)
        }

    def calculate_advanced_averages(self, history, team_id, reference_date=None):
        """
        Calcula promedios avanzados con todas las nuevas métricas
        """
        if not history:
            return None

        metrics = ["goals", "corners", "shots_on_target", "total_shots", 
                   "goals_conceded", "possession", "dangerous_attacks"]
        
        sums = {m: 0.0 for m in metrics}
        counts = {m: 0 for m in metrics}
        xg_values = []

        for item in history:
            if not item:
                continue
            extracted = self._extract_stats(
                item.get("match"), 
                item.get("stats"), 
                team_id
            )
            
            for m in metrics:
                val = extracted.get(m)
                if val is not None:
                    sums[m] += val
                    counts[m] += 1
            
            # Calcular xG para este partido
            xg = self.calculate_xg(
                extracted.get("shots_on_target"),
                extracted.get("total_shots"),
                extracted.get("dangerous_attacks"),
                extracted.get("possession")
            )
            if xg is not None:
                xg_values.append(xg)

        averages = {}
        for m in metrics:
            averages[m] = round(sums[m] / counts[m], 2) if counts[m] > 0 else None
        
        # Agregar xG promedio
        averages["xg"] = round(sum(xg_values) / len(xg_values), 2) if xg_values else None
        
        # Agregar métricas avanzadas
        averages["recent_form"] = self.calculate_recent_form(history, team_id)
        averages["fatigue"] = self.calculate_fatigue(history, reference_date)
        averages["home_advantage"] = self.calculate_home_advantage(history, team_id)
        averages["consistency"] = self.calculate_consistency(history, team_id)
        
        return averages

    def prepare_advanced_features(self, team_a_avg, team_b_avg, h2h_stats=None):
        """
        Prepara features avanzadas para el modelo
        """
        combined = {}
        
        if not team_a_avg or not team_b_avg:
            return combined
        
        # Features básicas mejoradas
        basic_metrics = ["goals", "corners", "shots_on_target", "total_shots", 
                        "goals_conceded", "xg"]
        
        for key in basic_metrics:
            val_a = team_a_avg.get(key)
            val_b = team_b_avg.get(key)
            
            if val_a is not None and val_b is not None:
                combined[f'{key}_home'] = val_a
                combined[f'{key}_away'] = val_b
                combined[f'{key}_diff'] = round(val_a - val_b, 2)
                combined[f'{key}_total'] = round(val_a + val_b, 2)
                combined[f'{key}_ratio'] = round(val_a / val_b, 2) if val_b > 0 else 1.0
        
        # Features de forma reciente
        form_a = team_a_avg.get("recent_form") or {}
        form_b = team_b_avg.get("recent_form") or {}
        
        combined["form_home_points"] = form_a.get("avg_points", 0)
        combined["form_away_points"] = form_b.get("avg_points", 0)
        combined["form_home_gd"] = form_a.get("goal_difference", 0)
        combined["form_away_gd"] = form_b.get("goal_difference", 0)
        combined["form_advantage"] = round(
            form_a.get("avg_points", 0) - form_b.get("avg_points", 0), 2
        )
        
        # Features de fatiga
        fatigue_a = team_a_avg.get("fatigue") or {}
        fatigue_b = team_b_avg.get("fatigue") or {}
        
        combined["fatigue_home"] = fatigue_a.get("fatigue_index", 0)
        combined["fatigue_away"] = fatigue_b.get("fatigue_index", 0)
        combined["fatigue_diff"] = round(
            fatigue_b.get("fatigue_index", 0) - fatigue_a.get("fatigue_index", 0), 2
        )
        
        # Features de ventaja de localía
        home_adv = team_a_avg.get("home_advantage") or {}
        combined["home_advantage_index"] = home_adv.get("home_advantage_index", 1.0)
        combined["home_goals_boost"] = home_adv.get("goals_advantage_ratio", 1.0)
        
        # Features de consistencia
        cons_a = team_a_avg.get("consistency") or {}
        cons_b = team_b_avg.get("consistency") or {}
        
        combined["consistency_home_off"] = cons_a.get("offensive_consistency", 0.5)
        combined["consistency_home_def"] = cons_a.get("defensive_consistency", 0.5)
        combined["consistency_away_off"] = cons_b.get("offensive_consistency", 0.5)
        combined["consistency_away_def"] = cons_b.get("defensive_consistency", 0.5)
        
        # Features de head-to-head
        if h2h_stats:
            combined["h2h_matches"] = h2h_stats.get("matches_played", 0)
            combined["h2h_dominance"] = h2h_stats.get("dominance_index", 0)
            combined["h2h_avg_goals_home"] = h2h_stats.get("avg_goals_team_a", 0)
            combined["h2h_avg_goals_away"] = h2h_stats.get("avg_goals_team_b", 0)
        
        return combined
