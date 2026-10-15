"""
tests/test_ecotrace.py — Comprehensive end-to-end unit test suite for EcoTrace AI.
Tests Auth & Security, Multi-User Isolation, Upsert & Unique Date constraints,
Emission Math (calc.py), and ML Forecasting (model.py).

All database tests use an isolated temporary SQLite database via monkeypatch.
"""

import os
import sys
import sqlite3
from datetime import datetime
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db
import calc
from model import train_model


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    """Isolate database so tests never touch production ecotrace.db."""
    test_db = str(tmp_path / "test_ecotrace.db")
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()
    yield test_db


# ─────────────────────────────────────────────────────────────────────────────
# 1. Auth & Security Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestAuthAndSecurity:
    def test_create_valid_user_and_duplicate_fails(self):
        # Valid user creation succeeds
        ok, msg = db.create_user("ecouser", "securepass123")
        assert ok is True
        assert "success" in msg.lower()

        # Duplicate username fails cleanly
        dup_ok, dup_msg = db.create_user("ecouser", "differentpass")
        assert dup_ok is False
        assert "already taken" in dup_msg.lower()

    def test_short_username_or_password_rejected(self):
        # Username < 3 chars rejected
        ok_u, msg_u = db.create_user("ab", "validpass123")
        assert ok_u is False
        assert "3 characters" in msg_u

        # Password < 6 chars rejected
        ok_p, msg_p = db.create_user("validuser", "12345")
        assert ok_p is False
        assert "6 characters" in msg_p

    def test_authenticate_user_scenarios(self):
        db.create_user("tester_auth", "correct_secret")

        # Success with correct credentials
        user = db.authenticate_user("tester_auth", "correct_secret")
        assert user is not None
        assert user["username"] == "tester_auth"
        assert isinstance(user["id"], int)

        # Returns None on wrong password
        assert db.authenticate_user("tester_auth", "wrong_password") is None

        # Returns None on nonexistent user
        assert db.authenticate_user("nonexistent_user", "correct_secret") is None

    def test_password_hash_is_salted_and_never_plaintext(self, isolated_db):
        raw_password = "MySuperSecretPassword!"
        db.create_user("crypto_user", raw_password)

        with sqlite3.connect(isolated_db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.cursor().execute("SELECT password_hash FROM users WHERE username = 'crypto_user'").fetchone()

        assert row is not None
        stored_hash = row["password_hash"]

        # Never equal plaintext
        assert stored_hash != raw_password
        assert raw_password not in stored_hash

        # Must be in salt_hex:hash_hex format
        assert ":" in stored_hash
        salt_hex, hash_hex = stored_hash.split(":", 1)
        assert len(salt_hex) == 32  # 16 bytes in hex
        assert len(hash_hex) == 64  # sha256 output in hex


# ─────────────────────────────────────────────────────────────────────────────
# 2. Multi-User Data Isolation Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestMultiUserDataIsolation:
    def test_multi_user_isolation_and_delete_protection(self):
        # Create User A and User B
        db.create_user("user_a", "password_a")
        db.create_user("user_b", "password_b")

        user_a = db.authenticate_user("user_a", "password_a")
        user_b = db.authenticate_user("user_b", "password_b")
        uid_a = user_a["id"]
        uid_b = user_b["id"]

        today_str = datetime.now().strftime("%Y-%m-%d")

        # Log entry for User A (10km, car, meat_heavy, 5.0 kWh)
        # 10*0.17 (1.7) + 3.3 (diet) + 5.0*0.82 (4.1) = 9.1 kg
        db.upsert_entry(
            user_id=uid_a,
            date=today_str,
            commute_km=10.0,
            commute_mode="car",
            diet_type="meat_heavy",
            active_hours=5.0,
            total_kg=9.1,
        )

        # User B must have no data
        assert db.get_all_entries(uid_b) == []
        assert db.get_days_logged_count(uid_b) == 0
        assert db.get_today_total(uid_b) is None

        # User A must have exactly their entry
        entries_a = db.get_all_entries(uid_a)
        assert len(entries_a) == 1
        assert db.get_days_logged_count(uid_a) == 1
        assert db.get_today_total(uid_a) == pytest.approx(9.1)

        # User B cannot delete User A's entry
        user_a_entry_id = entries_a[0]["id"]
        delete_attempt = db.delete_entry(user_id=uid_b, entry_id=user_a_entry_id)
        assert delete_attempt is False

        # Entry for User A must remain intact
        assert len(db.get_all_entries(uid_a)) == 1


# ─────────────────────────────────────────────────────────────────────────────
# 3. Upsert & Unique Date Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestUpsertAndUniqueDate:
    def test_upsert_same_date_updates_row_without_duplicate(self):
        db.create_user("upsert_user", "password123")
        uid = db.authenticate_user("upsert_user", "password123")["id"]

        date_target = "2026-10-15"

        # First insert
        db.upsert_entry(
            user_id=uid,
            date=date_target,
            commute_km=10.0,
            commute_mode="car",
            diet_type="meat_heavy",
            active_hours=5.0,
            total_kg=9.1,
        )

        # Second upsert on identical (user_id, date) with updated data
        db.upsert_entry(
            user_id=uid,
            date=date_target,
            commute_km=25.0,
            commute_mode="public_transit",
            diet_type="vegan",
            active_hours=2.0,
            total_kg=4.965,
        )

        rows = db.get_all_entries(uid)
        assert len(rows) == 1
        assert db.get_days_logged_count(uid) == 1

        updated_row = rows[0]
        assert updated_row["commute_km"] == 25.0
        assert updated_row["commute_mode"] == "public_transit"
        assert updated_row["diet_type"] == "vegan"
        assert updated_row["active_hours"] == 2.0
        assert updated_row["total_kg"] == pytest.approx(4.965)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Emission Math (calc.py) Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestEmissionMath:
    def test_calc_commute_kg(self):
        assert calc.calc_commute_kg(10.0, "car") == pytest.approx(1.70, rel=1e-4)
        assert calc.calc_commute_kg(20.0, "public_transit") == pytest.approx(1.78, rel=1e-3)
        assert calc.calc_commute_kg(50.0, "bike") == 0.0
        assert calc.calc_commute_kg(15.0, "walk") == 0.0
        assert calc.calc_commute_kg(0.0, "car") == 0.0
        # Unknown mode returns 0.0 without KeyError
        assert calc.calc_commute_kg(100.0, "hyperloop") == 0.0

    def test_calc_diet_kg(self):
        assert calc.calc_diet_kg("meat_heavy") == 3.3
        assert calc.calc_diet_kg("vegetarian") == 1.7
        assert calc.calc_diet_kg("vegan") == 1.1
        # Unknown diet returns 0.0 without KeyError
        assert calc.calc_diet_kg("unknown_diet") == 0.0

    def test_calc_electricity_kg(self):
        assert calc.calc_electricity_kg(0.0) == 0.0
        assert calc.calc_electricity_kg(1.0) == pytest.approx(0.82, rel=1e-3)
        assert calc.calc_electricity_kg(5.0) == pytest.approx(4.10, rel=1e-4)
        assert calc.calc_electricity_kg(10.0) == pytest.approx(8.20, rel=1e-4)

    def test_calc_total_kg(self):
        # 10km car (1.7) + meat_heavy (3.3) + 5.0 kWh (4.1) = 9.1
        total = calc.calc_total_kg(10.0, "car", "meat_heavy", 5.0)
        assert total == pytest.approx(9.1, rel=1e-3)

        # 0km walk (0.0) + vegan (1.1) + 0.0 kWh (0.0) = 1.1
        zero_commute = calc.calc_total_kg(0.0, "walk", "vegan", 0.0)
        assert zero_commute == pytest.approx(1.1, rel=1e-4)

        # All unknown / zeroes return 0.0
        unknown_total = calc.calc_total_kg(0.0, "unknown", "unknown", 0.0)
        assert unknown_total == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 5. ML Forecasting (model.py) Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestMLForecasting:
    def test_train_model_under_seven_days_returns_none(self):
        # 6 days of data
        dates = pd.date_range("2026-10-01", periods=6, freq="D").strftime("%Y-%m-%d")
        df_small = pd.DataFrame({"date": dates, "total_kg": [5.0, 4.8, 6.1, 5.5, 4.9, 5.2]})
        model_obj, pred = train_model(df_small)
        assert model_obj is None
        assert pred is None

    def test_train_model_seven_or_more_days_with_calendar_gap(self):
        # 8 distinct days with a 1-day calendar gap (missing 2026-10-05)
        dates = [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
            "2026-10-04",
            "2026-10-06",  # Gap: Oct 5 skipped
            "2026-10-07",
            "2026-10-08",
            "2026-10-09",
        ]
        totals = [5.1, 4.9, 5.8, 6.2, 5.0, 4.7, 5.3, 5.6]
        df = pd.DataFrame({"date": dates, "total_kg": totals})

        model_obj, pred = train_model(df)
        assert model_obj is not None
        assert hasattr(model_obj, "feature_importances_")
        assert len(model_obj.feature_importances_) == 5
        assert isinstance(pred, float)
        assert pred >= 0.0
