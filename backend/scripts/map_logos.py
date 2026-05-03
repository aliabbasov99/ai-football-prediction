import os
import difflib
from pymongo import MongoClient

# Database setup
client = MongoClient("mongodb://localhost:27017/")
db = client["football_prediction"]
standings_collection = db["standings"]

# Mapping from DB league_name to public/imgs/logos folderName
LEAGUES_MAPPING = {
    'Premier League': 'England - Premier League',
    'La Liga': 'Spain - LaLiga',
    'Bundesliga': 'Germany - Bundesliga',
    'Serie A': 'Italy - Serie A',
    'Ligue 1': 'France - Ligue 1',
    'Primeira Liga': 'Portugal - Liga Portugal',
    'Eredivisie': 'Netherlands - Eredivisie',
    'Pro League': 'Belgium - Jupiler Pro League',
    'Super Lig': 'Türkiye - Süper Lig',
    'Czech First League': 'Czech Republic - Chance Liga',
    'Super League Greece': 'Greece - Super League 1',
    'Danish Superliga': 'Denmark - Superliga',
    'Ekstraklasa': 'Poland - PKO BP Ekstraklasa',
}

# Aliases for tricky teams
ALIASES = {
    'Spurs': 'Tottenham Hotspur',
    'Man City': 'Manchester City',
    'Man Utd': 'Manchester United',
    'Nott\'m Forest': 'Nottingham Forest',
    'Sheff Utd': 'Sheffield United',
    'Wolves': 'Wolverhampton Wanderers',
    'Newcastle': 'Newcastle United',
    'West Ham': 'West Ham United',
    'Aston Villa': 'Aston Villa',
    'Brighton': 'Brighton & Hove Albion',
    'Bournemouth': 'AFC Bournemouth',
    'Crystal Palace': 'Crystal Palace',
    'Luton': 'Luton Town',
    'Paris SG': 'Paris Saint-Germain',
    'Monaco': 'AS Monaco',
    'Marseille': 'Olympique de Marseille',
    'Lyon': 'Olympique Lyonnais',
    'Lille': 'LOSC Lille',
    'Inter': 'Inter Milan',
    'Milan': 'AC Milan',
    'Roma': 'AS Roma',
    'Napoli': 'SSC Napoli',
    'Juventus': 'Juventus',
    'Lazio': 'SS Lazio',
    'Fiorentina': 'ACF Fiorentina',
    'Bayer Leverkusen': 'Bayer 04 Leverkusen',
    'Bayern Munich': 'FC Bayern München',
    'Dortmund': 'Borussia Dortmund',
    'RB Leipzig': 'RB Leipzig',
    'Stuttgart': 'VfB Stuttgart',
    'Frankfurt': 'Eintracht Frankfurt',
    'Freiburg': 'SC Freiburg',
    'Real Madrid': 'Real Madrid',
    'Barcelona': 'FC Barcelona',
    'Girona': 'Girona FC',
    'Atletico Madrid': 'Atlético de Madrid',
    'Athletic Club': 'Athletic Club',
    'Real Sociedad': 'Real Sociedad',
    'Betis': 'Real Betis',
    'Valencia': 'Valencia CF',
    'Villarreal': 'Villarreal CF',
    'Galatasaray': 'Galatasaray',
    'Fenerbahce': 'Fenerbahce',
    'Besiktas': 'Besiktas JK',
    'Trabzonspor': 'Trabzonspor',
    'Sporting CP': 'Sporting CP',
    'Benfica': 'SL Benfica',
    'Porto': 'FC Porto',
    'Braga': 'SC Braga',
    'PSV Eindhoven': 'PSV',
    'Feyenoord': 'Feyenoord',
    'Ajax': 'Ajax',
    'AZ Alkmaar': 'AZ',
    'Twente': 'FC Twente',
}

LOGOS_BASE_DIR = r"c:\ali\projects\ai-football-prediction\frontend\public\imgs\logos"

def get_best_match(team_name, filenames):
    # Check alias first
    alias = ALIASES.get(team_name)
    if alias:
        for f in filenames:
            if alias.lower() in f.lower() or f.lower().replace('.png', '') == alias.lower():
                return f

    # Try simple substring match
    substr_matches = [f for f in filenames if team_name.lower() in f.lower() or f.lower().replace('.png', '') in team_name.lower()]
    if substr_matches:
        # Sort by length to get the most exact match
        substr_matches.sort(key=len)
        return substr_matches[0]

    # Try fuzzy match
    matches = difflib.get_close_matches(team_name, filenames, n=1, cutoff=0.3)
    if matches:
        return matches[0]

    return None

def main():
    updated_count = 0
    missing_count = 0

    for league_name, folder_name in LEAGUES_MAPPING.items():
        folder_path = os.path.join(LOGOS_BASE_DIR, folder_name)
        if not os.path.exists(folder_path):
            print(f"Directory not found for league: {league_name} -> {folder_path}")
            continue

        filenames = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        
        teams = list(standings_collection.find({'league_name': league_name}))
        
        for team in teams:
            team_name = team['team']
            best_match = get_best_match(team_name, filenames)
            
            if best_match:
                logo_path = f"/imgs/logos/{folder_name}/{best_match}"
                standings_collection.update_one(
                    {'_id': team['_id']},
                    {'$set': {'team_logo': logo_path}}
                )
                updated_count += 1
                # print(f"Mapped: {team_name} -> {best_match}")
            else:
                missing_count += 1
                print(f"NO MATCH FOUND: {team_name} in {league_name}")

    print(f"\n--- Summary ---")
    print(f"Updated {updated_count} team logos.")
    print(f"Failed to find {missing_count} team logos.")

if __name__ == "__main__":
    main()
