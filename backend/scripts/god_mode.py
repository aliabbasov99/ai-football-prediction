import sys
import os
import subprocess
import datetime
from pymongo import MongoClient

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPTS_DIR)


# Her skript ucun loga kecirilecek maksimum satir sayi (UI logu sonsuz boyumasin)
MAX_SCRIPT_LOG_LINES = 40


def _run_subprocess(script_name, extra_args=None, log=None):
    """Skripti subprocess ile calistirir.

    Doner: (ok, captured_lines). `log` verilirse cekilen her satir
    pipeline loguna yazilir — daha once bu melumat yalnizca stdout-a dusurdu
    ve UI-da "hec ne olmur" goruntusu yaratiyordu.
    """
    abs_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [sys.executable, abs_path]
    if extra_args:
        cmd.extend(extra_args)
    print(f"  [subprocess] Running: {' '.join(cmd)}")
    pretty = " ".join([os.path.basename(script_name)] + list(extra_args or []))
    if log:
        log(f"$ python {pretty}")

    captured = []
    omitted = 0
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=BACKEND_DIR,
            encoding="utf-8",
            errors="replace"
        )
        for line in process.stdout:
            text = line.rstrip()
            print(f"    {line}", end="")
            if not text.strip():
                continue
            if len(captured) < MAX_SCRIPT_LOG_LINES:
                captured.append(text)
                if log:
                    log(f"  {text}")
            else:
                omitted += 1
        process.wait()
        if omitted and log:
            log(f"  ... (+{omitted} setir daha)")
        ok = process.returncode == 0
        if not ok and log:
            log(f"  [X] {os.path.basename(script_name)} xetti: exit={process.returncode}")
        return ok, captured
    except Exception as e:
        print(f"  [!] Subprocess error: {e}")
        if log:
            log(f"  [X] {os.path.basename(script_name)} xidmet xetasi: {e}")
        return False, captured


def _get_valid_dates():
    dates = []
    for delta in [0, 1]:
        d = datetime.datetime.now() + datetime.timedelta(days=delta)
        dates.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")
    return dates


SCRAPER_FIELDS = {
    "oddslot": {"prediction": "oddslot_stats"},
    "wincomparator": {"link": "wincomparator_link", "prediction": "wincomparator_stats"},
    "footystats": {"link": "footystats_h2h_link", "prediction": "footystats_stats"},
    "betimate": {"link": "betimate_link", "prediction": "betimate_stats"},
    "sportsgambler": {"link": "sportsgambler_link", "prediction": "sportsgambler_stats"},
    "misli": {"prediction": "misli_odds"},
}


def _count_field(db, valid_dates, field_path):
    query = {"date": {"$in": valid_dates}}
    query[f"predictions.{field_path}"] = {"$exists": True, "$ne": ""}
    return db.fixtures.count_documents(query)


def _snapshot_counts(db, valid_dates):
    snapshot = {}
    for name, flds in SCRAPER_FIELDS.items():
        stats = {}
        if "link" in flds:
            stats["link"] = _count_field(db, valid_dates, flds["link"])
        if "prediction" in flds:
            stats["prediction"] = _count_field(db, valid_dates, flds["prediction"])
        snapshot[name] = stats
    return snapshot


def _compute_deltas(after, before):
    deltas = {}
    for name in after:
        delta = {}
        for key in after[name]:
            d = after[name][key] - before.get(name, {}).get(key, 0)
            if d > 0:
                delta[key] = d
        if delta:
            deltas[name] = delta
    return deltas


def _build_report(db, valid_dates, before_snapshot=None):
    report = {
        "total_fixtures": db.fixtures.count_documents({"date": {"$in": valid_dates}}),
        "per_scraper": {},
    }
    for name, flds in SCRAPER_FIELDS.items():
        stats = {}
        if "link" in flds:
            stats["with_link"] = _count_field(db, valid_dates, flds["link"])
        if "prediction" in flds:
            stats["with_prediction"] = _count_field(db, valid_dates, flds["prediction"])
        report["per_scraper"][name] = stats
    if before_snapshot:
        after = _snapshot_counts(db, valid_dates)
        deltas = _compute_deltas(after, before_snapshot)
        for name, delta in deltas.items():
            report["per_scraper"][name]["this_run"] = delta
    return report


def run_god_mode(toggles=None, progress_callback=None, log_callback=None):
    def log(text):
        if log_callback:
            log_callback(text)

    failed_steps = []
    notes = []

    def update(percent, text):
        if progress_callback:
            progress_callback(percent, text)
        log(f"[{percent}%] {text}")
        print(f"\n[God Mode] {percent}% - {text}")
        print("=" * 40)

    step_order = [
        ("footystats_games", "Cedvel ve oyunlar (FootyStats)"),
        ("oddslot", "Oddslot faizleri"),
        ("wincomparator_links", "WinComparator linkleri"),
        ("wincomparator_predictions", "WinComparator proqnozlari"),
        ("footystats_links", "FootyStats linkleri"),
        ("footystats_predictions", "FootyStats proqnozlari"),
        ("betimate_links", "Betimate linkleri"),
        ("betimate_predictions", "Betimate proqnozlari"),
        ("sportsgambler_links", "SportsGambler linkleri"),
        ("sportsgambler_predictions", "SportsGambler proqnozlari"),
        ("misli", "Misli emsallari"),
    ]

    if toggles is None:
        toggles = {k: True for k, _ in step_order}

    active = [(k, lbl) for k, lbl in step_order if toggles.get(k)]
    total = len(active)

    if total == 0:
        update(100, "Hec bir addim secilmeyib.")
        return {
            "total_fixtures": 0,
            "per_scraper": {},
            "failed_steps": [],
            "notes": ["Hec bir addim secilmemisdi."],
        }

    def step_pct(idx):
        return int((idx / total) * 95) if total > 0 else 0

    def run_step(label, script_name, extra_args=None):
        """Skripti ishledir, ugursuzluq halini qeyd edir."""
        ok, _ = _run_subprocess(script_name, extra_args=extra_args, log=log)
        if not ok:
            failed_steps.append(label)
            log(f"  [!] Addim ugursuz oldu: {label}")
        return ok

    idx = 0

    before_snapshot = None

    # ---- Standings & Fixtures (FootyStats) ----
    if toggles.get("footystats_games"):
        update(step_pct(idx), "FootyStats cedvel ve oyunlar cekilir...")
        run_step("Cedvel ve oyunlar (FootyStats)", "scrapeFootyStatsGames.py")

        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["football_prediction"]
            valid_dates = _get_valid_dates()
            count = db.fixtures.count_documents({"date": {"$in": valid_dates}})
            if count == 0:
                client.close()
                reason = "Bugun ve sabah icin hec bir oyun tapilmadi. Proses dayandirildi."
                note = (
                    "Bu, demek olmur ki xeta var: pipeline sirf DB-de bu iki tarixe aid "
                    "olan oyunlarla isleyir. `/admin/leagues` bolmesinde lig teyin "
                    "edilmemişse skriptler hec ne tapa bilmir."
                )
                notes.append(note)
                update(100, reason)
                return {
                    "total_fixtures": 0,
                    "per_scraper": {},
                    "failed_steps": failed_steps,
                    "notes": notes,
                    "aborted": reason,
                }
            if before_snapshot is None:
                before_snapshot = _snapshot_counts(db, valid_dates)
            client.close()
        except Exception as e:
            print(f"  [!] Fixtures check error: {e}")
            log(f"  [!] Oyun yoxlamasinda xeta: {e}")
            notes.append(f"Oyun yoxlamasinda xeta: {e}")

        idx += 1

    # If footystats_games wasn't run, take snapshot before scraping steps
    if before_snapshot is None and any(toggles.get(k) for k, _ in step_order if k != "footystats_games"):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["football_prediction"]
            valid_dates = _get_valid_dates()
            before_snapshot = _snapshot_counts(db, valid_dates)
            client.close()
        except Exception as e:
            print(f"  [!] Before snapshot error: {e}")

    # ---- Link steps (combined into one browser session) ----
    link_map = {
        "wincomparator_links": "wincomparator",
        "betimate_links": "betimate",
        "sportsgambler_links": "sportsgambler",
        "footystats_links": "footystats",
    }
    enabled_link_steps = [v for k, v in link_map.items() if toggles.get(k)]

    external_map = {
        "wincomparator_predictions": "wincomparator",
        "footystats_predictions": "footystats",
    }
    has_external = any(toggles.get(k) for k in external_map)

    if enabled_link_steps:
        idx += 1
        update(step_pct(idx - 1), "Proqnoz linkleri yenilenir...")
        run_step(
            "Proqnoz linkleri",
            "update_prediction_links.py",
            extra_args=["--step"] + enabled_link_steps,
        )

    # ---- Oddslot Predictions (percentages from listing page) ----
    if toggles.get("oddslot"):
        idx += 1
        update(step_pct(idx - 1), "Oddslot faizleri cekilir...")
        run_step(
            "Oddslot faizleri",
            "scrape_external_details.py",
            extra_args=["--step", "oddslot"],
        )

    # ---- Betimate Predictions ----
    if toggles.get("betimate_predictions"):
        idx += 1
        update(step_pct(idx - 1), "Betimate proqnoz detallari cekilir...")
        run_step("Betimate proqnoz detallari", "scrape_betimate_details.py")

    # ---- SportsGambler Predictions ----
    if toggles.get("sportsgambler_predictions"):
        idx += 1
        update(step_pct(idx - 1), "SportsGambler proqnoz detallari cekilir...")
        run_step("SportsGambler proqnoz detallari", "scrape_sportsgambler_details.py")

    # ---- External predictions (WinComparator, FootyStats detail H2H) ----
    if has_external:
        idx += 1
        update(step_pct(idx - 1), "Xarici menbelerden proqnoz detallari cekilir...")
        ext_steps = [v for k, v in external_map.items() if toggles.get(k)]
        run_step(
            "Xarici proqnoz detallari",
            "scrape_external_details.py",
            extra_args=["--step"] + ext_steps,
        )

    # ---- Misli ----
    if toggles.get("misli"):
        idx += 1
        update(step_pct(idx - 1), "Misli emsallari cekilir...")
        run_step("Misli emsallari", "scrape_misli_all.py")

    # ---- Report ----
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        valid_dates = _get_valid_dates()
        report = _build_report(db, valid_dates, before_snapshot)
        client.close()
    except Exception as e:
        print(f"  [!] Report error: {e}")
        log(f"  [!] Hesabat xetasi: {e}")
        notes.append(f"Hesabat qurulmadi: {e}")
        report = {"total_fixtures": 0, "per_scraper": {}}

    report["failed_steps"] = failed_steps
    report["notes"] = notes

    if failed_steps:
        msg = f"Tamamlandi, amma {len(failed_steps)} addim ugursuz oldu."
        notes.append(
            "Ugursuz addimlar: " + ", ".join(failed_steps) +
            ". Backend logunda (`backend.err.log`) sebebini tapa bilersiniz."
        )
    else:
        msg = "Tamamlandi! Butun secilmis addimlar ugurla icra olundu."

    update(100, msg)

    print("\n" + "=" * 50)
    print("HESABAT")
    print("=" * 50)
    print(f"  Cemi oyun: {report['total_fixtures']}")
    for name, stats in report["per_scraper"].items():
        parts = []
        if stats.get("with_link") is not None:
            link_str = f"Link: {stats['with_link']}"
            if stats.get("this_run", {}).get("link"):
                link_str += f" (+{stats['this_run']['link']})"
            parts.append(link_str)
        if stats.get("with_prediction") is not None:
            pred_str = f"Proqnoz: {stats['with_prediction']}"
            if stats.get("this_run", {}).get("prediction"):
                pred_str += f" (+{stats['this_run']['prediction']})"
            parts.append(pred_str)
        print(f"  {name}: {', '.join(parts)}")
    print("=" * 50)

    return report


if __name__ == "__main__":
    run_god_mode()
