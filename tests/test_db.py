"""
tests/test_db.py — pytest integration tests for db.py
Uses a temporary SQLite database that is cleaned up after each test.
"""

import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Patch DB_PATH before importing db so tests use a temp file
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


class TestAddEntry:
    def test_add_returns_true(self):
        result = db_module.add_entry("2025-01-01", 10.0, "car", "meat_heavy", 8.0, 5.548)
        assert result is True

    def test_retrieve_after_add(self):
        db_module.add_entry("2025-01-02", 5.0, "bike", "vegan", 4.0, 1.264)
        rows = db_module.get_all_entries()
        assert len(rows) == 1
        assert rows[0]["commute_km"] == 5.0

    def test_multiple_entries(self):
        db_module.add_entry("2025-01-01", 10.0, "car", "meat_heavy", 8.0, 5.0)
        db_module.add_entry("2025-01-01", 2.0,  "bike", "vegan",     2.0, 1.2)
        rows = db_module.get_all_entries()
        assert len(rows) == 2


class TestGetAllEntries:
    def test_empty_returns_list_not_none(self):
        rows = db_module.get_all_entries()
        assert isinstance(rows, list)
        assert len(rows) == 0

    def test_ordered_desc_by_date(self):
        db_module.add_entry("2025-01-01", 10.0, "car", "meat_heavy", 8.0, 5.0)
        db_module.add_entry("2025-01-03", 5.0,  "bike", "vegan",     4.0, 1.0)
        db_module.add_entry("2025-01-02", 3.0,  "walk", "vegetarian", 6.0, 2.0)
        rows = db_module.get_all_entries()
        dates = [r["date"] for r in rows]
        assert dates == sorted(dates, reverse=True)


class TestGetDaysLoggedCount:
    def test_zero_on_empty_db(self):
        assert db_module.get_days_logged_count() == 0

    def test_counts_distinct_dates(self):
        db_module.add_entry("2025-01-01", 10.0, "car", "meat_heavy", 8.0, 5.0)
        db_module.add_entry("2025-01-01", 2.0,  "bike", "vegan",     2.0, 1.0)
        db_module.add_entry("2025-01-02", 5.0,  "walk", "vegetarian", 4.0, 2.0)
        # Two distinct dates: 2025-01-01 and 2025-01-02
        assert db_module.get_days_logged_count() == 2


class TestGetLastNDays:
    def test_empty_returns_list(self):
        rows = db_module.get_last_n_days(7)
        assert isinstance(rows, list)
        assert len(rows) == 0

    def test_respects_limit(self):
        for i in range(1, 12):
            db_module.add_entry(f"2025-01-{i:02d}", 10.0, "car", "meat_heavy", 8.0, 5.0)
        rows = db_module.get_last_n_days(7)
        assert len(rows) == 7


class TestGetTodayTotal:
    def test_returns_none_when_no_entry_today(self):
        # No entries → None
        result = db_module.get_today_total()
        assert result is None

    def test_returns_sum_of_todays_entries(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        db_module.add_entry(today, 10.0, "car", "meat_heavy", 8.0, 3.0)
        db_module.add_entry(today, 5.0,  "bike", "vegan",     4.0, 2.0)
        result = db_module.get_today_total()
        assert result == pytest.approx(5.0, rel=1e-4)
