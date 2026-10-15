"""
tests/test_db.py — pytest integration tests for multi-user db.py
Uses a temporary SQLite database that is cleaned up after each test.
"""

import pytest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db as db_module


@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    """Each test gets its own fresh database."""
    tmp_db = str(tmp_path / "test_ecotrace.db")
    original_path = db_module.DB_PATH
    db_module.DB_PATH = tmp_db
    db_module.init_db()
    yield tmp_db
    db_module.DB_PATH = original_path  # restore


class TestInitDb:
    def test_creates_db_file(self, isolated_db):
        assert os.path.exists(isolated_db)

    def test_idempotent(self, isolated_db):
        # Calling twice must not raise
        db_module.init_db()
        db_module.init_db()

    def test_migration_from_old_schema(self, tmp_path):
        """Verify automatic migration when an older table without user_id exists."""
        legacy_db = str(tmp_path / "legacy.db")
        with sqlite3.connect(legacy_db) as conn:
            conn.execute("""
                CREATE TABLE entries (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    commute_km REAL NOT NULL,
                    commute_mode TEXT NOT NULL,
                    diet_type TEXT NOT NULL,
                    active_hours REAL NOT NULL,
                    total_kg REAL NOT NULL
                )
            """)
            conn.execute("""
                INSERT INTO entries (date, commute_km, commute_mode, diet_type, active_hours, total_kg)
                VALUES ('2026-09-01', 10.0, 'car', 'meat_heavy', 5.0, 5.8)
            """)

        orig = db_module.DB_PATH
        db_module.DB_PATH = legacy_db
        try:
            db_module.init_db()
            with sqlite3.connect(legacy_db) as conn:
                cols = [r[1] for r in conn.execute("PRAGMA table_info(entries)").fetchall()]
                assert "user_id" in cols
                # Verify row was migrated
                count = conn.execute("SELECT count(*) FROM entries").fetchone()[0]
                assert count == 1
        finally:
            db_module.DB_PATH = orig


class TestUserAuth:
    def test_create_user_success(self):
        ok, msg = db_module.create_user("alice", "password123")
        assert ok is True
        assert "success" in msg.lower()

    def test_create_user_short_username(self):
        ok, msg = db_module.create_user("al", "password123")
        assert ok is False
        assert "3 characters" in msg

    def test_create_user_short_password(self):
        ok, msg = db_module.create_user("alice", "12345")
        assert ok is False
        assert "6 characters" in msg

    def test_create_user_duplicate(self):
        db_module.create_user("bob", "password123")
        ok, msg = db_module.create_user("bob", "different_pass")
        assert ok is False
        assert "already taken" in msg.lower()

    def test_authenticate_user_success(self):
        db_module.create_user("charlie", "mypassword")
        user = db_module.authenticate_user("charlie", "mypassword")
        assert user is not None
        assert user["username"] == "charlie"
        assert isinstance(user["id"], int)

    def test_authenticate_user_wrong_password(self):
        db_module.create_user("diana", "mypassword")
        user = db_module.authenticate_user("diana", "wrongpassword")
        assert user is None

    def test_authenticate_user_nonexistent(self):
        user = db_module.authenticate_user("nobody", "mypassword")
        assert user is None


class TestUpsertAndIsolation:
    def test_upsert_and_retrieve(self):
        _, _ = db_module.create_user("user1", "pass123")
        u1 = db_module.authenticate_user("user1", "pass123")
        uid = u1["id"]

        ok = db_module.upsert_entry(uid, "2026-10-01", 10.0, "car", "meat_heavy", 5.0, 5.8)
        assert ok is True

        entry = db_module.get_entry_by_date(uid, "2026-10-01")
        assert entry is not None
        assert entry["commute_km"] == 10.0
        assert entry["total_kg"] == 5.8

    def test_upsert_updates_existing_date(self):
        _, _ = db_module.create_user("user1", "pass123")
        u1 = db_module.authenticate_user("user1", "pass123")
        uid = u1["id"]

        db_module.upsert_entry(uid, "2026-10-01", 10.0, "car", "meat_heavy", 5.0, 5.8)
        # Update same date with new values
        db_module.upsert_entry(uid, "2026-10-01", 20.0, "car", "vegan", 2.0, 4.5)

        rows = db_module.get_all_entries(uid)
        assert len(rows) == 1
        assert rows[0]["commute_km"] == 20.0
        assert rows[0]["diet_type"] == "vegan"
        assert rows[0]["total_kg"] == 4.5

    def test_user_data_isolation(self):
        db_module.create_user("alice", "pass123")
        db_module.create_user("bob", "pass456")
        u_alice = db_module.authenticate_user("alice", "pass123")
        u_bob = db_module.authenticate_user("bob", "pass456")

        # Both log on same date
        db_module.upsert_entry(u_alice["id"], "2026-10-01", 15.0, "car", "meat_heavy", 5.0, 6.0)
        db_module.upsert_entry(u_bob["id"], "2026-10-01", 5.0, "bike", "vegan", 1.0, 1.92)

        alice_entries = db_module.get_all_entries(u_alice["id"])
        bob_entries = db_module.get_all_entries(u_bob["id"])

        assert len(alice_entries) == 1
        assert len(bob_entries) == 1
        assert alice_entries[0]["commute_km"] == 15.0
        assert bob_entries[0]["commute_km"] == 5.0

    def test_delete_entry_isolation(self):
        db_module.create_user("alice", "pass123")
        db_module.create_user("bob", "pass456")
        u_alice = db_module.authenticate_user("alice", "pass123")
        u_bob = db_module.authenticate_user("bob", "pass456")

        db_module.upsert_entry(u_alice["id"], "2026-10-01", 10.0, "car", "vegan", 2.0, 2.8)
        alice_entry = db_module.get_all_entries(u_alice["id"])[0]

        # Bob tries to delete Alice's entry
        deleted_by_bob = db_module.delete_entry(u_bob["id"], alice_entry["id"])
        assert deleted_by_bob is False
        assert len(db_module.get_all_entries(u_alice["id"])) == 1

        # Alice deletes her own entry
        deleted_by_alice = db_module.delete_entry(u_alice["id"], alice_entry["id"])
        assert deleted_by_alice is True
        assert len(db_module.get_all_entries(u_alice["id"])) == 0


class TestMetrics:
    def test_get_days_logged_count(self):
        db_module.create_user("user1", "pass123")
        uid = db_module.authenticate_user("user1", "pass123")["id"]

        assert db_module.get_days_logged_count(uid) == 0
        db_module.upsert_entry(uid, "2026-10-01", 10.0, "car", "vegan", 2.0, 2.8)
        db_module.upsert_entry(uid, "2026-10-02", 12.0, "car", "vegan", 2.0, 3.1)
        assert db_module.get_days_logged_count(uid) == 2

    def test_get_today_total(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        db_module.create_user("user1", "pass123")
        uid = db_module.authenticate_user("user1", "pass123")["id"]

        assert db_module.get_today_total(uid) is None
        db_module.upsert_entry(uid, today, 10.0, "car", "meat_heavy", 4.0, 5.0)
        assert db_module.get_today_total(uid) == pytest.approx(5.0)

    def test_get_last_n_days_limit(self):
        db_module.create_user("user1", "pass123")
        uid = db_module.authenticate_user("user1", "pass123")["id"]

        for i in range(1, 10):
            db_module.upsert_entry(uid, f"2026-10-{i:02d}", 5.0, "bike", "vegan", 1.0, 1.92)

        rows = db_module.get_last_n_days(uid, 5)
        assert len(rows) == 5

    def test_get_today_breakdown(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        db_module.create_user("user1", "pass123")
        uid = db_module.authenticate_user("user1", "pass123")["id"]

        breakdown = db_module.get_today_breakdown(uid)
        assert breakdown == {"Commute": 0.0, "Diet": 0.0, "Electricity": 0.0}

        db_module.upsert_entry(uid, today, 10.0, "car", "meat_heavy", 2.0, 5.0)
        breakdown = db_module.get_today_breakdown(uid)
        assert breakdown["Commute"] > 0
        assert breakdown["Diet"] > 0
        assert breakdown["Electricity"] > 0
