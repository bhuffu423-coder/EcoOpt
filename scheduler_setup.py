"""
scheduler_setup.py — Registers a real Windows Task Scheduler job to launch EcoTrace AI daily.
Uses subprocess + schtasks.exe (built into Windows).
Prints the exact command that was run.
Run this script once as the user who will use EcoTrace AI.
"""

import subprocess
import sys
import os


# TESTED: prints meaningful error if schtasks fails instead of silently passing
def register_daily_task(
    task_name: str = "EcoTraceAI_DailyLaunch",
    start_time: str = "08:00",
    app_dir: str | None = None,
) -> None:
    """
    Register a Windows Task Scheduler job that launches EcoTrace AI every day at start_time.

    Parameters
    ----------
    task_name  : Name shown in Task Scheduler
    start_time : HH:MM 24-hour time for the daily trigger
    app_dir    : Path to the directory containing app.py; defaults to the directory of this script
    """
    if app_dir is None:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    python_exe  = sys.executable
    app_script  = os.path.join(app_dir, "app.py")
    run_command = f'cmd /c "cd /d {app_dir} && {python_exe} -m streamlit run {app_script}"'

    schtasks_cmd = [
        "schtasks",
        "/Create",
        "/F",                     # Force overwrite if task exists
        "/TN", task_name,
        "/TR", run_command,
        "/SC", "DAILY",
        "/ST", start_time,
        "/RL", "HIGHEST",         # Run with highest available privileges
    ]

    print(f"[scheduler_setup.py] Registering task '{task_name}' via:")
    print("  " + " ".join(schtasks_cmd))

    try:
        result = subprocess.run(
            schtasks_cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"[scheduler_setup.py] Task '{task_name}' registered successfully.")
            print(f"  Stdout: {result.stdout.strip()}")
        else:
            print(f"[scheduler_setup.py] schtasks failed (code {result.returncode}).")
            print(f"  Stderr: {result.stderr.strip()}")
    except FileNotFoundError:
        print("[scheduler_setup.py] Error: schtasks.exe not found. Are you on Windows?")
    except subprocess.TimeoutExpired:
        print("[scheduler_setup.py] Error: schtasks timed out after 30 seconds.")
    except Exception as e:
        print(f"[scheduler_setup.py] Unexpected error: {e}")


if __name__ == "__main__":
    register_daily_task()
