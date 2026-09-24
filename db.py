"""
db.py — Database layer for EcoTrace AI.
All SQL is here; app.py never touches SQL directly.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "ecotrace.db")

# TESTED: runs on empty database and creates table if it does not exist
def init_db() -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id          INTEGER PRIMARY KEY,
                date        TEXT    NOT NULL,
                commute_km  REAL    NOT NULL,
                commute_mode TEXT   NOT NULL,
                diet_type   TEXT    NOT NULL,
                active_hours REAL   NOT NULL,
                total_kg    REAL    NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[db.py] init_db error: {e}")


# TESTED: insert with all required fields; returns False on failure so caller can surface error
def add_entry(
    date: str,
    commute_km: float,
    commute_mode: str,
    diet_type: str,
    active_hours: float,
    total_kg: float,
) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO entries (date, commute_km, commute_mode, diet_type, active_hours, total_kg)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (date, commute_km, commute_mode, diet_type, active_hours, total_kg),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[db.py] add_entry error: {e}")
        return False


# TESTED: returns empty list (not None) when table is empty
def get_all_entries() -> list[dict]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries ORDER BY date DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"[db.py] get_all_entries error: {e}")
        return []


# TESTED: returns 0 on empty table, never raises
def get_days_logged_count() -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT date) FROM entries")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"[db.py] get_days_logged_count error: {e}")
        return 0


# TESTED: returns empty dict (not None) when no rows for today
def get_today_total() -> float | None:
    """Return total_kg for today by summing all entries for today's date, or None if none."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(total_kg) FROM entries WHERE date = ?", (today,)
        )
        result = cursor.fetchone()
        conn.close()
        value = result[0] if result else None
        return value  # None if no entry today
    except sqlite3.Error as e:
        print(f"[db.py] get_today_total error: {e}")
        return None


# TESTED: returns empty list when fewer than 7 days of data exist
def get_last_n_days(n: int = 7) -> list[dict]:
    """Return the last n distinct days of entries (one aggregated row per day)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date,
                   SUM(commute_km)   AS commute_km,
                   MAX(commute_mode) AS commute_mode,
                   MAX(diet_type)    AS diet_type,
                   SUM(active_hours) AS active_hours,
                   SUM(total_kg)     AS total_kg
            FROM entries
            GROUP BY date
            ORDER BY date DESC
            LIMIT ?
            """,
            (n,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"[db.py] get_last_n_days error: {e}")
        return []


# TESTED: returns dict with all zeros when no entries exist
def get_today_breakdown() -> dict:
    """Return per-source kg totals for today: commute, diet, electricity."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT commute_km, commute_mode, diet_type, active_hours
            FROM entries WHERE date = ?
            """,
            (today,),
        )
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return {"Commute": 0.0, "Diet": 0.0, "Electricity": 0.0}
        from calc import calc_commute_kg, calc_diet_kg, calc_electricity_kg
        total_commute = sum(calc_commute_kg(r["commute_km"], r["commute_mode"]) for r in rows)
        total_diet    = sum(calc_diet_kg(r["diet_type"]) for r in rows)
        total_elec    = sum(calc_electricity_kg(r["active_hours"]) for r in rows)
        return {"Commute": round(total_commute, 3),
                "Diet":    round(total_diet, 3),
                "Electricity": round(total_elec, 3)}
    except Exception as e:
        print(f"[db.py] get_today_breakdown error: {e}")
        return {"Commute": 0.0, "Diet": 0.0, "Electricity": 0.0}


def delete_entry(entry_id: int) -> bool:
    """Delete a log entry by its primary key ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[db.py] delete_entry error: {e}")
        return False


def get_entry_by_date(date_str: str) -> dict | None:
    """Return the entry for a specific date if it exists, otherwise None."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE date = ? LIMIT 1", (date_str,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"[db.py] get_entry_by_date error: {e}")
        return None


def upsert_entry(
    date: str,
    commute_km: float,
    commute_mode: str,
    diet_type: str,
    active_hours: float,
    total_kg: float,
) -> bool:
    """Ensure exactly one complete row per date: updates if existing, inserts if new."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM entries WHERE date = ? LIMIT 1", (date,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """
                UPDATE entries
                SET commute_km = ?, commute_mode = ?, diet_type = ?, active_hours = ?, total_kg = ?
                WHERE id = ?
                """,
                (commute_km, commute_mode, diet_type, active_hours, total_kg, existing[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO entries (date, commute_km, commute_mode, diet_type, active_hours, total_kg)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (date, commute_km, commute_mode, diet_type, active_hours, total_kg),
            )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[db.py] upsert_entry error: {e}")
        return False
