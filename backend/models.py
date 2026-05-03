from pydantic import BaseModel
from typing import Optional


class GameStats(BaseModel):
    games: int
    xg_for: float
    xg_against: float
    goals_for: int
    goals_against: int


class TeamXGStats(BaseModel):
    team_id: str
    team_name: str
    team_logo: str
    position: int
    points: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goal_difference: str = "0"
    form: str
    last_30_games: GameStats
    league_games: GameStats
    cup_games: GameStats


class League(BaseModel):
    id: str
    name: str
    country: str
    logo: str


class Last5Game(BaseModel):
    opponent: str
    opponent_logo: str = ""
    home_away: str
    score: Optional[str] = None
    xg_for: float = 0.0
    xg_against: float = 0.0
    date: str = ""


class Match(BaseModel):
    id: str
    home_team: str
    home_team_id: str = ""
    home_team_position: int = 0
    away_team: str
    away_team_id: str = ""
    away_team_position: int = 0
    home_logo: str
    away_logo: str
    home_xg: float
    away_xg: float
    score: Optional[str] = None
    date: str
    league: str
    league_name: str = ""
    home_last5: list[Last5Game] = []
    away_last5: list[Last5Game] = []


class Prediction(BaseModel):
    match_id: str
    over_15: dict
    over_25: dict
    over_35: dict
    btts_yes: dict
    btts_no: dict
    winner: dict
