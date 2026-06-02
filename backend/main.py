from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from models import TeamXGStats, League, Match
from services import data_service
from scripts.scrapeFootyStats import scrape_all_footystats as run_footystats_stats_scraper
from scripts.scrapeFootyStatsGames import scrape_all as run_footystats_games_scraper
from scripts.god_mode import run_god_mode

# Global flag for scraper status
is_scraping = False

# Pipeline state
pipeline = {
    "is_running": False,
    "current_step": "",
    "current_step_index": 0,
    "total_steps": 0,
    "progress": 0,
    "step_status": "idle",
    "error": "",
    "report": None,
}

fs_stats_pipeline = {
    "is_running": False,
    "progress": 0,
    "current_page": "",
}


class ScrapeToggles(BaseModel):
    footystats_games: bool = True
    misli: bool = True
    oddslot: bool = True
    wincomparator_links: bool = True
    wincomparator_predictions: bool = True
    footystats_links: bool = True
    footystats_predictions: bool = True
    betimate_links: bool = True
    betimate_predictions: bool = True
    sportsgambler_links: bool = True
    sportsgambler_predictions: bool = True


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
    return {"status": "ok", "message": "API isleyir"}


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
        raise HTTPException(status_code=404, detail="Komanda tapilmadi")
    return team


@app.get("/api/footystats/pages")
async def get_footystats_pages():
    return await data_service.get_footystats_pages()


@app.get("/api/footystats/page/{slug}")
async def get_footystats_page(slug: str):
    page = await data_service.get_footystats_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Sehife tapilmadi")
    return page


@app.get("/api/predictions")
async def get_predictions():
    return await data_service.get_predictions()


@app.get("/api/admin/status-live")
async def admin_status_live():
    return pipeline


@app.post("/api/admin/scrape-start")
async def admin_scrape_start(toggles: ScrapeToggles, background_tasks: BackgroundTasks):
    if pipeline["is_running"]:
        return {"status": "warning", "message": "Pipeline already running."}

    toggles_dict = toggles.model_dump()
    selected_steps = [k for k, v in toggles_dict.items() if v]
    pipeline["is_running"] = True
    pipeline["current_step"] = selected_steps[0] if selected_steps else ""
    pipeline["current_step_index"] = 0
    pipeline["total_steps"] = len(selected_steps)
    pipeline["progress"] = 0
    pipeline["step_status"] = "running"
    pipeline["error"] = ""
    pipeline["report"] = None

    def run_pipeline():
        def progress_callback(percent: int, text: str):
            pipeline["progress"] = percent
            pipeline["current_step"] = text

        report = None
        try:
            report = run_god_mode(toggles=toggles_dict, progress_callback=progress_callback)
            pipeline["progress"] = 100
            pipeline["step_status"] = "completed"
        except Exception as e:
            pipeline["error"] = str(e)
            pipeline["step_status"] = "error"
        finally:
            if report:
                pipeline["report"] = report
            pipeline["is_running"] = False
            pipeline["current_step"] = ""
            pipeline["current_step_index"] = 0
            pipeline["total_steps"] = 0

    background_tasks.add_task(run_pipeline)
    return {"status": "success", "message": f"Pipeline started with {len(selected_steps)} steps."}


@app.post("/api/admin/clear-db")
async def admin_clear_db():
    try:
        from services import data_service
        data_service.db["standings"].delete_many({})
        data_service.db["fixtures"].delete_many({})
        data_service.db["matches"].delete_many({})
        data_service.db["footystats_pages"].delete_many({})
        data_service.db["footystats_all"].delete_many({})
        return {"status": "success", "message": "Database cleared."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/admin/scrape-footystats-games")
async def admin_scrape_footystats_games(background_tasks: BackgroundTasks):
    global is_scraping
    if is_scraping:
        return {"status": "warning", "message": "Scraping already in progress."}
    background_tasks.add_task(run_footystats_games_scraper)
    return {"status": "success", "message": "FootyStats games scraping started."}


@app.post("/api/admin/scrape-footystats-stats")
async def admin_scrape_footystats_stats(background_tasks: BackgroundTasks):
    if fs_stats_pipeline["is_running"]:
        return {"status": "warning", "message": "FootyStats scraping already running."}

    def task():
        fs_stats_pipeline["is_running"] = True
        fs_stats_pipeline["progress"] = 0
        fs_stats_pipeline["current_page"] = ""
        try:
            run_footystats_stats_scraper()
            fs_stats_pipeline["progress"] = 100
        except Exception as e:
            print(f"FootyStats scraper error: {e}")
        finally:
            fs_stats_pipeline["is_running"] = False

    background_tasks.add_task(task)
    return {"status": "success", "message": "FootyStats scraping started."}


@app.get("/api/admin/scrape-footystats-stats/status")
async def admin_footystats_stats_status():
    return fs_stats_pipeline


# Admin leagues & teams CRUD
@app.get("/api/admin/leagues")
async def admin_get_leagues():
    from services import data_service
    from services import LEAGUE_SLUGS
    name_to_slug = {v["name"]: k for k, v in LEAGUE_SLUGS.items()}
    configs = list(data_service.db["leagues_config"].find({}))
    result = []
    for c in configs:
        name = c.get("name", "")
        slug = c.get("slug") or name_to_slug.get(name) or name
        league_id = str(c.get("_id")) or slug
        result.append({
            "id": league_id,
            "slug": slug,
            "name": name,
            "country": c.get("country", ""),
            "logo": c.get("logo") or "",
            "sort_order": c.get("sort_order", 0),
            "misli_link": c.get("misli_link", ""),
            "wincomparator_link": c.get("wincomparator_link", ""),
            "oddslot_link": c.get("oddslot_link", ""),
            "betimate_link": c.get("betimate_link", ""),
            "footystats_link": c.get("footystats_link", ""),
            "sportsgambler_link": c.get("sportsgambler_link", ""),
        })
    return result


@app.post("/api/admin/leagues")
async def admin_create_league(data: dict):
    from services import data_service
    data.pop("_id", None)
    data_service.db["leagues_config"].insert_one(data)
    return {"status": "success"}


@app.put("/api/admin/leagues/{league_id}")
async def admin_update_league(league_id: str, data: dict):
    from services import data_service
    from bson.objectid import ObjectId
    query = {"_id": ObjectId(league_id)} if ObjectId.is_valid(league_id) else {"slug": league_id}
    data_service.db["leagues_config"].update_one(query, {"$set": data})
    return {"status": "success"}


@app.delete("/api/admin/leagues/{league_id}")
async def admin_delete_league(league_id: str):
    from services import data_service
    from bson.objectid import ObjectId
    query = {"_id": ObjectId(league_id)} if ObjectId.is_valid(league_id) else {"slug": league_id}
    data_service.db["leagues_config"].delete_one(query)
    return {"status": "success"}


@app.get("/api/admin/teams")
async def admin_get_teams(league_id: str = Query("")):
    from services import data_service
    from bson.objectid import ObjectId

    if not league_id:
        return {"teams": []}

    teams = list(data_service.db["teams"].find({"league_id": league_id}))
    if not teams:
        # Try by leagues_config _id (the admin page sends MongoDB _id as league id)
        config = data_service.db["leagues_config"].find_one({"_id": ObjectId(league_id)})
        if config:
            teams = list(data_service.db["teams"].find({"league_id": league_id}))

    for t in teams:
        t["_id"] = str(t["_id"])

    return {"teams": teams}


@app.post("/api/admin/teams")
async def admin_create_team(data: dict):
    from services import data_service
    data_service.db["teams"].insert_one(data)
    return {"status": "success"}


@app.put("/api/admin/teams/{team_id}")
async def admin_update_team(team_id: str, data: dict):
    from services import data_service
    from bson.objectid import ObjectId
    data_service.db["teams"].update_one({"_id": ObjectId(team_id)}, {"$set": data})
    return {"status": "success"}


@app.delete("/api/admin/teams/{team_id}")
async def admin_delete_team(team_id: str):
    from services import data_service
    from bson.objectid import ObjectId
    data_service.db["teams"].delete_one({"_id": ObjectId(team_id)})
    return {"status": "success"}


@app.post("/api/admin/teams/sync")
async def admin_sync_teams(data: dict):
    from services import data_service
    from bson.objectid import ObjectId
    league_id = data.get("league_id")
    if not league_id:
        return {"status": "error", "message": "league_id required"}
    # Look up league name from leagues_config
    config = data_service.db["leagues_config"].find_one({"_id": ObjectId(league_id)} if ObjectId.is_valid(league_id) else {"slug": league_id})
    league_name = config.get("name", "") if config else ""
    if not league_name:
        return {"status": "error", "message": "Liga tapilmadi"}
    # Pull teams from standings into teams collection
    standings = list(data_service.db["standings"].find({"league_name": league_name}))
    count = 0
    for s in standings:
        name = s.get("team") or s.get("team_name") or ""
        if not name:
            continue
        exists = data_service.db["teams"].find_one({"name": name, "league_id": league_id})
        if not exists:
            data_service.db["teams"].insert_one({"name": name, "league_id": league_id, "logo": s.get("team_logo", "") or "", "aliases": []})
            count += 1
    return {"status": "success", "synced": count}


@app.post("/api/admin/teams/bulk-update")
async def admin_bulk_update_teams(data: dict):
    from services import data_service
    league_id = data.get("league_id")
    aliases = data.get("aliases", {})
    logos = data.get("logos", {})
    not_found = []
    aliases_updated = 0
    logos_updated = 0

    def _ensure_list(v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        return []

    for name in set(list(aliases.keys()) + list(logos.keys())):
        team = data_service.db["teams"].find_one({"name": name, "league_id": league_id})
        if not team:
            import re
            team = data_service.db["teams"].find_one({"name": {"$regex": re.escape(name), "$options": "i"}, "league_id": league_id})
        if not team:
            not_found.append(name)
            continue
        update = {}
        if name in logos:
            update["logo"] = logos[name]
        if name in aliases:
            update["aliases"] = _ensure_list(aliases[name])
        if update:
            data_service.db["teams"].update_one({"_id": team["_id"]}, {"$set": update})
            if name in logos:
                logos_updated += 1
            if name in aliases and aliases[name]:
                aliases_updated += 1
    return {"status": "success", "aliases_updated": aliases_updated, "logos_updated": logos_updated, "not_found": not_found}


@app.get("/api/matches/live", response_model=List[Match])
async def get_live_matches():
    return await data_service.get_live_matches()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7999)
