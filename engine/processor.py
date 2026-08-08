class DataProcessor:
    def _value_or_none(self, value):
        """Retorna el valor si es numérico, de lo contrario None."""
        return value if isinstance(value, (int, float)) else None

    def _extract_stats(self, match, stats, team_id):
        """
        Extrae métricas específicas basándose en el rol del equipo (home/away).
        """
        # Determinar el lado (side)
        home_id = str(match.get("home_team", {}).get("id"))
        away_id = str(match.get("away_team", {}).get("id"))
        side = "home" if str(team_id) == home_id else "away"

        score = match.get("score", {})
        overview = stats.get("overview", {})

        # Extracción siguiendo la estructura exacta de la API
        return {
            "goals": self._value_or_none(score.get(side)),
            "corners": self._value_or_none(overview.get("corner_kicks", {}).get("all", {}).get(side)),
            "shots_on_target": self._value_or_none(overview.get("shots_on_target", {}).get("all", {}).get(side)),
            "total_shots": self._value_or_none(overview.get("total_shots", {}).get("all", {}).get(side))
        }

    def calculate_averages(self, history, team_id):
        """
        Calcula promedios únicamente con valores existentes (sin sesgo de ceros).
        """
        if not history:
            return None

        # Listas para recolectar valores válidos
        goals_list = []
        corners_list = []
        sot_list = []
        shots_list = []

        for item in history:
            match = item.get("match")
            stats = item.get("stats")
            
            if not match or not stats:
                continue

            # Extraer métricas para este partido
            extracted = self._extract_stats(match, stats, team_id)

            # Agregar a las listas solo si el valor no es None
            if extracted["goals"] is not None: goals_list.append(extracted["goals"])
            if extracted["corners"] is not None: corners_list.append(extracted["corners"])
            if extracted["shots_on_target"] is not None: sot_list.append(extracted["shots_on_target"])
            if extracted["total_shots"] is not None: shots_list.append(extracted["total_shots"])

        # Calcular promedios finales
        averages = {
            "goals": sum(goals_list) / len(goals_list) if goals_list else None,
            "corners": sum(corners_list) / len(corners_list) if corners_list else None,
            "shots_on_target": sum(sot_list) / len(sot_list) if sot_list else None,
            "total_shots": sum(shots_list) / len(shots_list) if shots_list else None
        }
        
        return averages

    def prepare_features(self, team_a_avg, team_b_avg):
        combined = {}
        for key in team_a_avg.keys():
            combined[f'{key}_a'] = team_a_avg[key]
            combined[f'{key}_b'] = team_b_avg[key]
            combined[f'{key}_max'] = max(team_a_avg[key], team_b_avg[key])
            combined[f'{key}_total'] = team_a_avg[key] + team_b_avg[key]
        return combined
