import httpx
import asyncio
import requests
import re
import json
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from models import TeamXGStats, GameStats, League, Match
from pymongo import MongoClient

def calculate_xg_from_results(results):
    """
    Calculate xG for teams based on their match results.
    """
    xg_data = {}
    for match in results:
        home_team = match.get("home_team")
        away_team = match.get("away_team")
        home_score = match.get("home_score", 0)
        away_score = match.get("away_score", 0)
        
        # Simple xG estimation: score * 0.9 + 0.1
        h_xg = home_score * 0.9 + 0.1
        a_xg = away_score * 0.9 + 0.1
        
        for team, xf, xa, gf, ga in [(home_team, h_xg, a_xg, home_score, away_score), 
                                     (away_team, a_xg, h_xg, away_score, home_score)]:
            if team not in xg_data:
                xg_data[team] = {"xG_for": 0, "xG_against": 0, "goals_for": 0, "goals_against": 0, "games": 0}
            stats = xg_data[team]
            stats["xG_for"] += xf
            stats["xG_against"] += xa
            stats["goals_for"] += gf
            stats["goals_against"] += ga
            stats["games"] += 1
    return xg_data

LEAGUE_SLUGS = {
    "PL": {
        "slug": "england/premier-league",
        "name": "Premier League",
        "country": "England",
    },
    "LaLiga": {"slug": "spain/laliga", "name": "La Liga", "country": "Spain"},
    "BL": {"slug": "germany/bundesliga", "name": "Bundesliga", "country": "Germany"},
    "SA": {"slug": "italy/serie-a", "name": "Serie A", "country": "Italy"},
    "L1": {"slug": "france/ligue-1", "name": "Ligue 1", "country": "France"},
    "ED": {
        "slug": "netherlands/eredivisie",
        "name": "Eredivisie",
        "country": "Netherlands",
    },
}

class DataService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["football_prediction"]
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 600 # 10 minutes cache

    async def close(self):
        await self.client.aclose()
        self.mongo_client.close()

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_time:
            return False
        return (datetime.now() - self._cache_time[key]).seconds < self._cache_duration

    def _set_cache(self, key: str, data):
        self._cache[key] = data
        self._cache_time[key] = datetime.now()

    def _get_cache(self, key: str):
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None

    async def get_leagues(self) -> List[League]:
        return [
            League(id="PL", name="Premier League", country="England", logo="/logos/leagues/premier_league.svg"),
            League(id="LaLiga", name="La Liga", country="Spain", logo="/logos/leagues/laliga.png"),
            League(id="BL", name="Bundesliga", country="Germany", logo="/logos/leagues/bundlesliga.png"),
            League(id="SA", name="Serie A", country="Italy", logo="/logos/leagues/seria.png"),
            League(id="L1", name="Ligue 1", country="France", logo="/logos/leagues/ligue1.svg"),
            League(id="ED", name="Eredivisie", country="Netherlands", logo="/logos/leagues/eredivisie.svg"),
        ]

    async def get_teams_stats(self, league_id: str) -> List[TeamXGStats]:
        cache_key = f"teams_{league_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Fetch data from MongoDB
        print(f"Fetching data for {league_id} from MongoDB...")
        league_name = LEAGUE_SLUGS.get(league_id, {}).get("name")
        
        # Get standings and sort by rank (numerically)
        standings = list(self.db["standings"].find({"league_name": league_name}))
        standings.sort(key=lambda x: int(x.get("rank") or 0))
        
        # Get results (matches) from MongoDB - we'll implement match scraping next
        results = list(self.db["matches"].find({"league_name": league_name}).limit(300))
        xg_data = calculate_xg_from_results(results)

        teams = []
        for standing in standings:
            # Correct field mapping from WhoScored MongoDB documents (matching screenshot)
            team_name = standing.get("team", "Unknown Team")
            
            # Robust parsing for string or numeric values
            def to_int(val, default=0):
                if val is None: return default
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default

            played = to_int(standing.get("played"))
            gf = to_int(standing.get("goals_for"))
            ga = to_int(standing.get("goals_against"))
            pos = to_int(standing.get("rank"))
            pts = to_int(standing.get("points"))
            
            won = to_int(standing.get("won"))
            drawn = to_int(standing.get("drawn"))
            lost = to_int(standing.get("lost"))
            gd = str(standing.get("goal_difference", "0"))
            
            # Form logic (list to string)
            last_games = standing.get("last_games", [])
            form_str = "".join([str(g).upper() for g in last_games]) if last_games else "DDDDD"
            # Limit to 5 games as requested
            form_str = form_str[:5]
            if len(form_str) < 5:
                form_str = form_str.ljust(5, 'D')

            # Calculate xG based on user straightforward logic:
            # xG will be presented as total goals, so the frontend computes Average xG = Goals / Played
            xg_total_for = float(gf)
            xg_total_against = float(ga)

            teams.append(
                TeamXGStats(
                    team_id=str(pos),
                    team_name=team_name,
                    team_logo="", 
                    position=pos,
                    points=pts,
                    won=won,
                    drawn=drawn,
                    lost=lost,
                    goal_difference=gd,
                    form=form_str,
                    last_30_games=GameStats(
                        games=played,
                        xg_for=xg_total_for,
                        xg_against=xg_total_against,
                        goals_for=gf,
                        goals_against=ga,
                    ),
                    league_games=GameStats(
                        games=played,
                        xg_for=xg_total_for,
                        xg_against=xg_total_against,
                        goals_for=gf,
                        goals_against=ga,
                    ),
                    cup_games=GameStats(
                        games=0, xg_for=0, xg_against=0, goals_for=0, goals_against=0
                    ),
                )
            )

        print(f"Processed {len(teams)} teams for {league_id}")
        if not teams:
            return self._get_mock_teams(league_id)

        teams.sort(key=lambda x: x.position)
        self._set_cache(cache_key, teams)
        return teams

    async def get_all_teams_with_positions(self) -> Dict[str, List[Dict]]:
        cache_key = "all_teams_positions"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        result = {}
        for league_id in ["PL", "LaLiga", "BL", "SA", "L1", "ED"]:
            teams = await self.get_teams_stats(league_id)
            result[league_id] = [
                {
                    "team_id": t.team_id,
                    "team_name": t.team_name,
                    "position": t.position,
                    "league_id": league_id,
                    "xg_for": t.last_30_games.xg_for,
                    "xg_against": t.last_30_games.xg_against,
                    "played": t.last_30_games.games,
                }
                for t in teams
            ]

        self._set_cache(cache_key, result)
        return result

    async def get_top_bottom_teams(self) -> Tuple[List[Dict], List[Dict]]:
        all_teams = await self.get_all_teams_with_positions()
        top_teams = []
        bottom_teams = []

        for league_id, teams in all_teams.items():
            sorted_teams = sorted(teams, key=lambda x: x["position"])
            if len(sorted_teams) >= 5:
                top_teams.extend(sorted_teams[:5]) # Top 5
                bottom_teams.extend(sorted_teams[-5:]) # Bottom 5
        return top_teams, bottom_teams

    async def get_top_bottom_matches(self, limit: int = 100) -> List[Match]:
        """
        Real fixture-based top-vs-bottom detection.
        Read upcoming fixtures from MongoDB and check if each match is between
        a top-3 and bottom-3 team in the same league.
        """
        all_teams = await self.get_all_teams_with_positions()
        
        # Build a lookup: league_id -> {"team_name": position}
        league_position_map = {}
        league_sizes = {}
        for league_id, teams in all_teams.items():
            league_position_map[league_id] = {t["team_name"]: t["position"] for t in teams}
            league_sizes[league_id] = len(teams)

        # League name -> league_id map (reverse of LEAGUE_SLUGS)
        name_to_id = {v["name"]: k for k, v in LEAGUE_SLUGS.items()}

        # Read upcoming fixtures from MongoDB
        fixtures_col = self.db["fixtures"]
        all_fixtures = list(fixtures_col.find({}))

        matches = []
        match_id = 1

        TOP_N = 3
        BOTTOM_N = 3

        for fixture in all_fixtures:
            league_name = fixture.get("league_name", "")
            league_id = name_to_id.get(league_name)
            if not league_id:
                continue

            pos_map = league_position_map.get(league_id, {})
            total = league_sizes.get(league_id, 0)
            if total == 0:
                continue

            home_name = fixture.get("home_team", "")
            away_name = fixture.get("away_team", "")

            home_pos = pos_map.get(home_name)
            away_pos = pos_map.get(away_name)

            if home_pos is None or away_pos is None:
                # Try fuzzy: team names may differ slightly (e.g. "Man City" vs "Manchester City")
                for db_name, pos in pos_map.items():
                    if home_name and (home_name in db_name or db_name in home_name):
                        home_pos = pos
                    if away_name and (away_name in db_name or db_name in away_name):
                        away_pos = pos

            if home_pos is None or away_pos is None:
                continue

            is_home_top = home_pos <= TOP_N
            is_away_top = away_pos <= TOP_N
            is_home_bottom = home_pos > total - BOTTOM_N
            is_away_bottom = away_pos > total - BOTTOM_N

            # Only include if one is top and the other is bottom
            if not ((is_home_top and is_away_bottom) or (is_home_bottom and is_away_top)):
                continue

            # Fetch xG stats for the teams 
            home_team_data = next((t for t in all_teams.get(league_id, []) if t["team_name"] == home_name or home_name in t["team_name"]), None)
            away_team_data = next((t for t in all_teams.get(league_id, []) if t["team_name"] == away_name or away_name in t["team_name"]), None)

            home_xg = (home_team_data["xg_for"] / home_team_data["played"]) if home_team_data and home_team_data["played"] > 0 else 0.0
            away_xg = (away_team_data["xg_for"] / away_team_data["played"]) if away_team_data and away_team_data["played"] > 0 else 0.0

            match_date = f"{fixture.get('date', '')} {fixture.get('time', '')}".strip()

            matches.append(
                Match(
                    id=f"m{match_id}",
                    home_team=home_name,
                    away_team=away_name,
                    home_logo="",
                    away_logo="",
                    home_xg=home_xg,
                    away_xg=away_xg,
                    score=None,
                    date=match_date or "Sıradakı",
                    league=league_id,
                )
            )
            match_id += 1

        return matches[:limit]

    def _get_mock_teams(self, league_id: str) -> List[TeamXGStats]:
        # Minimal mock version for fallback
        return []

    async def get_team_stats(self, team_id: str) -> Optional[TeamXGStats]:
        for league_id in ["PL", "LaLiga", "BL", "SA", "L1", "ED"]:
            teams = await self.get_teams_stats(league_id)
            for team in teams:
                if team.team_id == team_id:
                    return team
        return None

    async def get_live_matches(self) -> List[Match]:
        return []

data_service = DataService()
