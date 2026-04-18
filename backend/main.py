from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

from models import TeamXGStats, League, Match
from services import data_service
from scripts.scrapSeasonGames import run_all_scrapers
from scripts.getFixtureGames import run_all_fixture_scrapers

# Global flag for scraper status
is_scraping = False
is_scraping_fixtures = False

def run_scrapers_task():
    global is_scraping
    is_scraping = True
    try:
        run_all_scrapers()
    except Exception as e:
        print(f"Scraper task failed: {e}")
    finally:
        is_scraping = False

def run_fixture_scrapers_task():
    global is_scraping_fixtures
    is_scraping_fixtures = True
    try:
        run_all_fixture_scrapers()
    except Exception as e:
        print(f"Fixture scraper task failed: {e}")
    finally:
        is_scraping_fixtures = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await data_service.close()


app = FastAPI(
    title="AI Football Prediction API",
    description="xG analiz və futbol proqnozları üçün API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API işləyir"}


@app.get("/api/leagues", response_model=List[League])
async def get_leagues():
    return await data_service.get_leagues()


@app.get("/api/leagues/{league_id}/teams", response_model=List[TeamXGStats])
async def get_league_teams(league_id: str):
    return await data_service.get_teams_stats(league_id)


@app.get("/api/top-bottom/teams")
async def get_top_bottom_teams():
    top_teams, bottom_teams = await data_service.get_top_bottom_teams()
    return {
        "top_teams": top_teams,
        "bottom_teams": bottom_teams,
    }


@app.get("/api/top-bottom/matches")
async def get_top_bottom_matches(limit: int = 100):
    return await data_service.get_top_bottom_matches(limit)


@app.get("/api/teams/{team_id}", response_model=TeamXGStats)
async def get_team(team_id: str):
    team = await data_service.get_team_stats(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Komanda tapılmadı")
    return team


@app.get("/api/matches/live", response_model=List[Match])
async def get_live_matches():
    return await data_service.get_live_matches()


@app.post("/api/admin/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    global is_scraping
    if is_scraping:
        return {"status": "warning", "message": "Scraping already in progress."}
    
    background_tasks.add_task(run_scrapers_task)
    return {"status": "success", "message": "Scraping process started in background."}


@app.get("/api/admin/status")
async def get_scrape_status():
    return {"is_scraping": is_scraping}


@app.post("/api/admin/scrape-fixtures")
async def trigger_scrape_fixtures(background_tasks: BackgroundTasks):
    global is_scraping_fixtures
    if is_scraping_fixtures:
        return {"status": "warning", "message": "Fixtures scraping already in progress."}
    
    background_tasks.add_task(run_fixture_scrapers_task)
    return {"status": "success", "message": "Fixtures scraping process started in background."}


@app.get("/api/admin/status-fixtures")
async def get_scrape_fixtures_status():
    global is_scraping_fixtures
    return {"is_scraping": is_scraping_fixtures}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
