"""
tests/test_model.py — pytest tests for model.py
"""

import pytest
import sys, os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from model import train_model, get_biggest_contributor, get_suggestion


class TestTrainModel:
    def _make_df(self, n: int) -> pd.DataFrame:
        """Create a synthetic daily dataframe with n rows."""
        dates = pd.date_range("2025-01-01", periods=n, freq="D").strftime("%Y-%m-%d")
        totals = np.random.default_rng(42).uniform(3.0, 10.0, n)
        return pd.DataFrame({"date": dates, "total_kg": totals})

    def test_returns_none_when_fewer_than_7_rows(self):
        df = self._make_df(5)
        m, pred = train_model(df)
        assert m is None
        assert pred is None

    def test_returns_none_on_none_input(self):
        m, pred = train_model(None)
        assert m is None

    def test_returns_none_on_empty_df(self):
        m, pred = train_model(pd.DataFrame({"date": [], "total_kg": []}))
        assert m is None

    def test_trains_with_7_rows(self):
        df = self._make_df(7)
        m, pred = train_model(df)
        assert m is not None
        assert isinstance(pred, float)

    def test_trains_with_30_rows(self):
        df = self._make_df(30)
        m, pred = train_model(df)
        assert m is not None
        assert pred >= 0.0  # must be non-negative

    def test_prediction_is_float(self):
        df = self._make_df(10)
        _, pred = train_model(df)
        assert isinstance(pred, float)


class TestGetBiggestContributor:
    def test_identifies_largest_value(self):
        breakdown = {"Commute": 5.0, "Diet": 1.5, "Electricity": 0.3}
        name, val = get_biggest_contributor(breakdown)
        assert name == "Commute"
        assert val == 5.0

    def test_empty_dict_returns_unknown(self):
        name, val = get_biggest_contributor({})
        assert name == "Unknown"
        assert val == 0.0

    def test_diet_largest(self):
        breakdown = {"Commute": 0.5, "Diet": 3.3, "Electricity": 0.4}
        name, val = get_biggest_contributor(breakdown)
        assert name == "Diet"


class TestGetSuggestion:
    def test_returns_string_for_all_valid_keys(self):
        for key in ["Commute", "Diet", "Electricity", "Unknown"]:
            s = get_suggestion(key)
            assert isinstance(s, str)
            assert len(s) > 10

    def test_unknown_key_returns_default(self):
        s = get_suggestion("Flying")  # not in dict
        assert "Unknown" in s or "Log more" in s or len(s) > 5
