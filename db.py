"""
db.py — Database layer for EcoTrace AI.
Multi-user SQLite schema with password hashing and safe context managers.
All SQL is here; app.py never touches SQL directly.
"""

import sqlite3
import os
import hashlib
import hmac
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "ecotrace.db")


def _hash_password(password: str) -> str:
    """Generate salt and hash password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{pwd_hash.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plain password against the stored salt:hash string."""
    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(pwd_hash.hex(), hash_hex)
    except Exception:
        return False


def init_db() -> None:
    """Initialize database tables and run migration if older schema exists."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            # 1. Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL UNIQUE,
                    password_hash TEXT    NOT NULL,
                    created_at    TEXT    NOT NULL
                )
            """)

            # 2. Check if entries table exists and if it has user_id column
            cursor.execute("PRAGMA table_info(entries)")
            cols = [row[1] for row in cursor.fetchall()]

            if cols and "user_id" not in cols:
                # Older schema detected without user_id: migrate safely
                cursor.execute("SELECT id FROM users LIMIT 1")
                first_user = cursor.fetchone()
                if not first_user:
                    # Create default demo user to own existing historical entries
                    now_str = datetime.now().isoformat()
                    default_hash = _hash_password("admin123")
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                        ("default_user", default_hash, now_str),
                    )
                    default_uid = cursor.lastrowid
                else:
                    default_uid = first_user[0]

                cursor.execute("ALTER TABLE entries RENAME TO entries_old")
                cursor.execute("""
                    CREATE TABLE entries (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id      INTEGER NOT NULL,
                        date         TEXT    NOT NULL,
                        commute_km   REAL    NOT NULL,
                        commute_mode TEXT    NOT NULL,
                        diet_type    TEXT    NOT NULL,
                        active_hours REAL    NOT NULL,
                        total_kg     REAL    NOT NULL,
                        UNIQUE(user_id, date),
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)

                cursor.execute("""
                    INSERT OR IGNORE INTO entries (user_id, date, commute_km, commute_mode, diet_type, active_hours, total_kg)
                    SELECT ?, date, commute_km, commute_mode, diet_type, active_hours, total_kg
                    FROM entries_old
                """, (default_uid,))
                cursor.execute("DROP TABLE entries_old")
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id      INTEGER NOT NULL,
                        date         TEXT    NOT NULL,
                        commute_km   REAL    NOT NULL,
                        commute_mode TEXT    NOT NULL,
                        diet_type    TEXT    NOT NULL,
                        active_hours REAL    NOT NULL,
                        total_kg     REAL    NOT NULL,
                        UNIQUE(user_id, date),
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
    except sqlite3.Error as e:
        print(f"[db.py] init_db error: {e}")


def create_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Validates username >= 3 chars, password >= 6 chars.
    Handles duplicates gracefully.
    """
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters."

    username_clean = username.strip()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username_clean, _hash_password(password), datetime.now().isoformat()),
            )
            return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def authenticate_user(username: str, password: str) -> dict | None:
    """Authenticate username and password; returns dict or None."""
    if not username or not password:
        return None
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username.strip(),))
            row = cursor.fetchone()
            if row and _verify_password(password, row["password_hash"]):
                return {"id": row["id"], "username": row["username"]}
            return None
    except sqlite3.Error as e:
        print(f"[db.py] authenticate_user error: {e}")
        return None


def upsert_entry(
    user_id: int,
    date: str,
    commute_km: float,
    commute_mode: str,
    diet_type: str,
    active_hours: float,
    total_kg: float,
) -> bool:
    """Ensure exactly one complete row per (user_id, date)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO entries (user_id, date, commute_km, commute_mode, diet_type, active_hours, total_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    commute_km = excluded.commute_km,
                    commute_mode = excluded.commute_mode,
                    diet_type = excluded.diet_type,
                    active_hours = excluded.active_hours,
                    total_kg = excluded.total_kg
                """,
                (user_id, date, commute_km, commute_mode, diet_type, active_hours, total_kg),
            )
            return True
    except sqlite3.Error as e:
        print(f"[db.py] upsert_entry error: {e}")
        return False


def get_all_entries(user_id: int) -> list[dict]:
    """Return all entries for a specific user ordered by date descending."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE user_id = ? ORDER BY date DESC", (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[db.py] get_all_entries error: {e}")
        return []


def get_days_logged_count(user_id: int) -> int:
    """Return distinct calendar days logged by this user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT date) FROM entries WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"[db.py] get_days_logged_count error: {e}")
        return 0


def get_today_total(user_id: int) -> float | None:
    """Return total_kg for today by summing all entries for today's date for this user, or None."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT SUM(total_kg) FROM entries WHERE user_id = ? AND date = ?",
                (user_id, today),
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else None
    except sqlite3.Error as e:
        print(f"[db.py] get_today_total error: {e}")
        return None


def get_last_n_days(user_id: int, n: int = 7) -> list[dict]:
    """Return the last n distinct days of entries for this user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
                WHERE user_id = ?
                GROUP BY date
                ORDER BY date DESC
                LIMIT ?
                """,
                (user_id, n),
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[db.py] get_last_n_days error: {e}")
        return []


def get_today_breakdown(user_id: int) -> dict:
    """Return per-source kg totals for today for this user: commute, diet, electricity."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT commute_km, commute_mode, diet_type, active_hours
                FROM entries WHERE user_id = ? AND date = ?
                """,
                (user_id, today),
            )
            rows = cursor.fetchall()
            if not rows:
                return {"Commute": 0.0, "Diet": 0.0, "Electricity": 0.0}
            from calc import calc_commute_kg, calc_diet_kg, calc_electricity_kg
            total_commute = sum(calc_commute_kg(r["commute_km"], r["commute_mode"]) for r in rows)
            total_diet = sum(calc_diet_kg(r["diet_type"]) for r in rows)
            total_elec = sum(calc_electricity_kg(r["active_hours"]) for r in rows)
            return {
                "Commute": round(total_commute, 3),
                "Diet": round(total_diet, 3),
                "Electricity": round(total_elec, 3),
            }
    except Exception as e:
        print(f"[db.py] get_today_breakdown error: {e}")
        return {"Commute": 0.0, "Diet": 0.0, "Electricity": 0.0}


def get_entry_by_date(user_id: int, date_str: str) -> dict | None:
    """Return the entry for a specific date and user if it exists, otherwise None."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM entries WHERE user_id = ? AND date = ? LIMIT 1",
                (user_id, date_str),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"[db.py] get_entry_by_date error: {e}")
        return None


def delete_entry(user_id: int, entry_id: int) -> bool:
    """Delete a log entry by primary key ID and user ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[db.py] delete_entry error: {e}")
        return False
