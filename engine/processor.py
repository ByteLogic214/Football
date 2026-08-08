import pandas as pd
import numpy as np

class DataProcessor:
    @staticmethod
    def calculate_averages(history_data):
        """
        Calcula promedios de: remates al arco, remates totales, corners, goles.
        """
        if not history_data:
            return None
        
        df = pd.DataFrame(history_data)
        metrics = ['shots_on_target', 'total_shots', 'corners', 'goals']
        averages = df[metrics].mean().to_dict()
        return averages

    @staticmethod
    def prepare_features(team_a_avg, team_b_avg):
        """
        Combina promedios para proyectar el máximo y el total.
        """
        combined = {}
        for key in team_a_avg.keys():
            combined[f'{key}_a'] = team_a_avg[key]
            combined[f'{key}_b'] = team_b_avg[key]
            # Proyectar el máximo de ambos como métrica de techo
            combined[f'{key}_max'] = max(team_a_avg[key], team_b_avg[key])
            # Proyectar la suma para mercados de 'Over/Under'
            combined[f'{key}_total'] = team_a_avg[key] + team_b_avg[key]
        return combined
