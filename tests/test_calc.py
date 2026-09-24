"""
tests/test_calc.py — pytest unit tests for calc.py
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calc import (
    calc_commute_kg,
    calc_diet_kg,
    calc_electricity_kg,
    calc_total_kg,
    COMMUTE_FACTORS,
    DIET_FACTORS,
)


# ──────────────────────── commute ────────────────────────
class TestCalcCommuteKg:
    def test_car_known_distance(self):
        assert calc_commute_kg(10, "car") == pytest.approx(1.7, rel=1e-4)

    def test_bike_zero_emissions(self):
        assert calc_commute_kg(50, "bike") == 0.0

    def test_walk_zero_emissions(self):
        assert calc_commute_kg(5, "walk") == 0.0

    def test_public_transit(self):
        assert calc_commute_kg(20, "public_transit") == pytest.approx(1.78, rel=1e-3)

    def test_zero_distance_all_modes(self):
        for mode in COMMUTE_FACTORS:
            assert calc_commute_kg(0.0, mode) == 0.0

    def test_unknown_mode_returns_zero(self):
        # Should not raise KeyError; returns 0
        assert calc_commute_kg(100, "hoverboard") == 0.0


# ──────────────────────── diet ────────────────────────
class TestCalcDietKg:
    def test_meat_heavy(self):
        assert calc_diet_kg("meat_heavy") == 3.3

    def test_vegetarian(self):
        assert calc_diet_kg("vegetarian") == 1.7

    def test_vegan(self):
        assert calc_diet_kg("vegan") == 1.1

    def test_unknown_diet_returns_zero(self):
        # Should not raise; returns 0
        assert calc_diet_kg("fruitarian") == 0.0

    def test_all_diet_keys_positive(self):
        for k in DIET_FACTORS:
            assert calc_diet_kg(k) > 0


# ──────────────────────── electricity (kWh input) ────────────────────────
class TestCalcElectricityKg:
    def test_zero_kwh(self):
        assert calc_electricity_kg(0.0) == 0.0

    def test_five_kwh(self):
        # 5 kWh × 0.82 kg/kWh = 4.10
        assert calc_electricity_kg(5.0) == pytest.approx(4.10, rel=1e-4)

    def test_one_kwh(self):
        # 1 kWh × 0.82 = 0.82
        assert calc_electricity_kg(1.0) == pytest.approx(0.82, rel=1e-3)

    def test_eight_kwh(self):
        # 8 kWh × 0.82 = 6.56
        assert calc_electricity_kg(8.0) == pytest.approx(6.56, rel=1e-4)

    def test_non_negative_output(self):
        result = calc_electricity_kg(0.0)
        assert result >= 0.0


# ──────────────────────── total ────────────────────────
class TestCalcTotalKg:
    def test_all_zero(self):
        # 0 commute + vegan 1.1 + 0 elec = 1.1
        assert calc_total_kg(0.0, "bike", "vegan", 0.0) == pytest.approx(1.1, rel=1e-4)

    def test_car_meat_heavy_with_electricity(self):
        # 10km car=1.7 + meat_heavy=3.3 + 5 kWh × 0.82=4.1 = 9.1
        result = calc_total_kg(10.0, "car", "meat_heavy", 5.0)
        assert result == pytest.approx(9.1, rel=1e-3)

    def test_walk_vegan_no_electricity(self):
        # 0 + 1.1 + 0 = 1.1
        assert calc_total_kg(0.0, "walk", "vegan", 0.0) == pytest.approx(1.1, rel=1e-4)

    def test_result_is_float(self):
        result = calc_total_kg(5, "car", "vegetarian", 2.0)
        assert isinstance(result, float)
