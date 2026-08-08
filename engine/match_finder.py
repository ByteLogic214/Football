import sys
from engine.api_client import FootballDataClient

def main():
    if len(sys.argv) < 2:
        print("Uso: python -m engine.match_finder YYYY-MM-DD")
        return

    date_str = sys.argv[1]
    client = FootballDataClient()
    matches = client.get_matches_by_date(date_str)

    if not matches:
        print("No se encontraron partidos para esa fecha.")
        return

    print(f"\n{'MATCH_ID':<12} | {'HOME TEAM':<20} vs {'AWAY TEAM':<20}")
    print("-" * 60)
    for m in matches:
        m_id = m.get('id')
        home = m.get('home_team', {}).get('name', 'N/A')
        away = m.get('away_team', {}).get('name', 'N/A')
        print(f"{m_id:<12} | {home:<20} vs {away:<20}")

if __name__ == "__main__":
    main()
