class DataProcessor:
    def _value_or_none(self, value):
        return value if isinstance(value, (int, float)) else None

    def _extract_stats(self, match, stats, team_id):
        match = match or {}
        stats = stats or {}

        home_team = match.get("home_team") or {}
        away_team = match.get("away_team") or {}
        
        home_id = str(home_team.get("id"))
        away_id = str(away_team.get("id"))
        side = "home" if str(team_id) == home_id else "away"

        score = match.get("score") or {}
        overview = stats.get("overview") or {}

        def get_stat_value(stat_name):
            stat_obj = overview.get(stat_name) or {}
            all_obj = stat_obj.get("all") or {}
            return self._value_or_none(all_obj.get(side))

        return {
            "goals": self._value_or_none(score.get(side)),
            "corners": get_stat_value("corner_kicks"),
            "shots_on_target": get_stat_value("shots_on_target"),
            "total_shots": get_stat_value("total_shots")
        }

    def calculate_averages(self, history, team_id):
        if not history:
            return None

        metrics = ["goals", "corners", "shots_on_target", "total_shots"]
        sums = {m: 0.0 for m in metrics}
        counts = {m: 0 for m in metrics}

        for item in history:
            if not item:
                continue
            extracted = self._extract_stats(item.get("match"), item.get("stats"), team_id)
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
        if not team_a_avg or not team_b_avg:
            return combined
            
        for key in team_a_avg.keys():
            if team_a_avg.get(key) is not None and team_b_avg.get(key) is not None:
                combined[f'{key}_a'] = team_a_avg[key]
                combined[f'{key}_b'] = team_b_avg[key]
                combined[f'{key}_max'] = max(team_a_avg[key], team_b_avg[key])
                combined[f'{key}_total'] = team_a_avg[key] + team_b_avg[key]
        return combined
