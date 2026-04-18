import requests
import json
from typing import List, Dict, Optional

LEAGUE_IDS = {
    "PL": " EPL",
    "LaLiga": "ESP",
    "BL": "BL1",
    "SA": "ITA",
    "L1": "FRA",
    "ED": "NED",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
}


class FootballDataAPI:
    BASE_URL = "https://api.football-data.org/v4"
    API_KEY = None

    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        if api_key:
            self.API_KEY = api_key
            self.session.headers["X-Auth-Token"] = api_key

    def get_standings(self, league_code: str) -> List[Dict]:
        url = f"{self.BASE_URL}/competitions/{league_code}/standings"

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                standings = []

                for group in data.get("standings", []):
                    if group.get("type") == "TOTAL":
                        for entry in group.get("table", []):
                            standings.append(
                                {
                                    "position": entry.get("position", 0),
                                    "team_name": entry.get("team", {}).get("name", ""),
                                    "team_short": entry.get("team", {}).get("tla", ""),
                                    "played": entry.get("playedGames", 0),
                                    "won": entry.get("won", 0),
                                    "drawn": entry.get("draw", 0),
                                    "lost": entry.get("lost", 0),
                                    "goals_for": entry.get("goalsFor", 0),
                                    "goals_against": entry.get("goalsAgainst", 0),
                                    "goals_diff": entry.get("goalDifference", 0),
                                    "points": entry.get("points", 0),
                                }
                            )

                        standings.sort(key=lambda x: x["position"])
                        return standings

        except Exception as e:
            print(f"API error: {e}")

        return []

    def get_matches(self, league_code: str, limit: int = 100) -> List[Dict]:
        url = f"{self.BASE_URL}/competitions/{league_code}/matches"

        try:
            response = self.session.get(url, params={"limit": limit}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                matches = []

                for match in data.get("matches", []):
                    matches.append(
                        {
                            "home_team": match.get("homeTeam", {}).get("name", ""),
                            "away_team": match.get("awayTeam", {}).get("name", ""),
                            "home_score": match.get("score", {})
                            .get("fullTime", {})
                            .get("home", 0)
                            or 0,
                            "away_score": match.get("score", {})
                            .get("fullTime", {})
                            .get("away", 0)
                            or 0,
                            "date": match.get("utcDate", ""),
                            "status": match.get("status", ""),
                            "matchday": match.get("matchday", 0),
                        }
                    )

                return matches

        except Exception as e:
            print(f"API error: {e}")

        return []

    def get_team_stats(self, league_code: str) -> List[Dict]:
        standings = self.get_standings(league_code)
        matches = self.get_matches(league_code, 200)

        team_stats = {}
        for match in matches:
            home = match["home_team"]
            away = match["away_team"]
            home_score = match["home_score"] or 0
            away_score = match["away_score"] or 0

            for team, is_home in [(home, True), (away, False)]:
                if team not in team_stats:
                    team_stats[team] = {
                        "name": team,
                        "games": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                        "xG_for": 0,
                        "xG_against": 0,
                    }

                team_stats[team]["games"] += 1
                team_stats[team]["goals_for"] += home_score if is_home else away_score
                team_stats[team]["goals_against"] += (
                    away_score if is_home else home_score
                )
                team_stats[team]["xG_for"] += (
                    home_score if is_home else away_score
                ) * 0.92 + 0.08
                team_stats[team]["xG_against"] += (
                    away_score if is_home else home_score
                ) * 0.92 + 0.08

                if (home_score > away_score and is_home) or (
                    away_score > home_score and not is_home
                ):
                    team_stats[team]["wins"] += 1
                elif home_score == away_score:
                    team_stats[team]["draws"] += 1
                else:
                    team_stats[team]["losses"] += 1

        result = []
        for standing in standings:
            team_name = standing["team_name"]
            if team_name in team_stats:
                stats = team_stats[team_name]
                result.append(
                    {
                        **standing,
                        "xG_for": round(stats["xG_for"], 1),
                        "xG_against": round(stats["xG_against"], 1),
                        "wins": stats["wins"],
                        "draws": stats["draws"],
                        "losses": stats["losses"],
                    }
                )
            else:
                result.append(standing)

        return result

    def close(self):
        self.session.close()


api = FootballDataAPI()
