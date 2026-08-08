class DataProcessor:
    def calculate_averages(self, history, team_id):
        """
        Calcula promedios navegando por: item['stats']['overview'][metric]['all'][side]
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
        target_id = str(team_id)

        for item in history:
            try:
                match = item.get("match", {})
                stats = item.get("stats", {})
                overview = stats.get("overview", {})

                # 1. Determinar si el equipo fue Home o Away en este partido
                home_id = str(match.get("home_team", {}).get("id"))
                away_id = str(match.get("away_team", {}).get("id"))
                
                side = None
                if target_id == home_id:
                    side = "home"
                elif target_id == away_id:
                    side = "away"
                
                if not side:
                    continue

                # 2. Extraer métricas usando la ruta exacta proporcionada
                # Estructura: overview -> metric -> all -> side
                sums["shots_on_target"] += float(overview.get("shots_on_target", {}).get("all", {}).get(side, 0))
                sums["total_shots"] += float(overview.get("total_shots", {}).get("all", {}).get(side, 0))
                sums["corners"] += float(overview.get("corners", {}).get("all", {}).get(side, 0))
                sums["goals"] += float(overview.get("goals", {}).get("all", {}).get(side, 0))
                
                count += 1
            except Exception as e:
                print(f"⚠️ Error procesando un partido del historial: {e}")
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
