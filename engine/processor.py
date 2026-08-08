class DataProcessor:
    def calculate_averages(self, history, team_id):
        """
        Calcula promedios analizando el rol del equipo (home/away) 
        en cada partido del historial.
        """
        if not history:
            return None

        sums = {
            "shots_on_target": 0.0,
            "total_shots": 0.0,
            "corners": 0.0,
            "goals": 0.0
        }
        count = 0

        for item in history:
            match = item.get("match", {})
            stats = item.get("stats", {})
            
            # 1. Determinar el lado (home o away) del equipo en este partido
            side = None
            home_id = str(match.get("home_team", {}).get("id"))
            away_id = str(match.get("away_team", {}).get("id"))
            target_id = str(team_id)

            if target_id == home_id:
                side = "home"
            elif target_id == away_id:
                side = "away"
            
            if not side:
                continue

            # 2. Acceder a la estructura anidada: stats -> overview -> [metric] -> all -> [side]
            try:
                overview = stats.get("overview", {})
                
                # Función auxiliar para extraer con seguridad
                def get_metric_val(metric_name):
                    return overview.get(metric_name, {}).get("all", {}).get(side, 0)

                sums["shots_on_target"] += float(get_metric_val("shots_on_target"))
                sums["total_shots"] += float(get_metric_val("total_shots"))
                sums["corners"] += float(get_metric_val("corners"))
                sums["goals"] += float(get_metric_val("goals"))
                
                count += 1
            except Exception as e:
                # Si un partido tiene estructura corrupta, lo saltamos
                continue

        if count == 0:
            return None

        return {k: v / count for k, v in sums.items()}

    def prepare_features(self, team_a_avg, team_b_avg):
        combined = {}
        for key in team_a_avg.keys():
            combined[f'{key}_a'] = team_a_avg[key]
            combined[f'{key}_b'] = team_b_avg[key]
            combined[f'{key}_max'] = max(team_a_avg[key], team_b_avg[key])
            combined[f'{key}_total'] = team_a_avg[key] + team_b_avg[key]
        return combined
