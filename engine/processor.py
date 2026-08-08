class DataProcessor:
    def _value_or_none(self, value):
        return value if isinstance(value, (int, float)) else None

    def _extract_stats(self, match, stats, team_id):
        home_id = str(match.get("home_team", {}).get("id"))
        away_id = str(match.get("away_team", {}).get("id"))
        side = "home" if str(team_id) == home_id else "away"

        score = match.get("score", {})
        overview = stats.get("overview", {})

        return {
            "goals": self._value_or_none(score.get(side)),
            "corners": self._value_or_none(overview.get("corner_kicks", {}).get("all", {}).get(side)),
            "shots_on_target": self._value_or_none(overview.get("shots_on_target", {}).get("all", {}).get(side)),
            "total_shots": self._value_or_none(overview.get("total_shots", {}).get("all", {}).get(side))
        }

    def calculate_averages(self, history, team_id):
        if not history:
            return None

        metrics = ["goals", "corners", "shots_on_target", "total_shots"]
        sums = {m: 0.0 for m in metrics}
        counts = {m: 0 for m in metrics}

        for item in history:
            extracted = self._extract_stats(item["match"], item["stats"], team_id)
            for m in metrics:
                val = extracted.get(m)
                if val is not None:
                    sums[m] += val
                    counts[m] += 1

        averages = {}
        for m in metrics:
            averages[m] = sums[m] / counts[m] if counts[m] > 0 else None
        
        return averages

    def prepare_features(self, team_a_avg, team_b_avg):
        combined = {}
        for key in team_a_avg.keys():
            if team_a_avg[key] is not None and team_b_avg[key] is not None:
                combined[f'{key}_a'] = team_a_avg[key]
                combined[f'{key}_b'] = team_b_avg[key]
                combined[f'{key}_max'] = max(team_a_avg[key], team_b_avg[key])
                combined[f'{key}_total'] = team_a_avg[key] + team_b_avg[key]
        return combined
