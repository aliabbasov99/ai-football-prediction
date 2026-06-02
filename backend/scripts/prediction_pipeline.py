import os
import sys
import subprocess

# Scripts directory for subprocess calls
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPTS_DIR)

def _run_subprocess(script_name):
    """Run a script from scripts/ as a subprocess."""
    abs_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n[Prediction Pipeline] STARTING: {script_name}")
    try:
        process = subprocess.Popen(
            [sys.executable, abs_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=BACKEND_DIR
        )
        for line in process.stdout:
            print(f"    {line}", end="")
        process.wait()
        print(f"[Prediction Pipeline] COMPLETED: {script_name}")
    except Exception as e:
        print(f"[!] Subprocess error: {e}")

def run_full_prediction_pipeline():
    print("="*50)
    print("STARTING STATS SCRAPING (Using Existing Links)")
    print("="*50)
    
    _run_subprocess("scrape_betimate_details.py")
    _run_subprocess("scrape_sportsgambler_details.py")
    
    print("\n" + "="*50)
    print("PREDICTION PIPELINE FINISHED.")
    print("="*50)

if __name__ == "__main__":
    run_full_prediction_pipeline()
