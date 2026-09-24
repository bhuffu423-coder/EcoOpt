"""
calc.py — Pure emission-calculation functions for EcoTrace AI.

Emission factors (documented sources):
  - Car:           0.17  kg CO₂/km  (UK DEFRA 2023 average petrol car)
  - Motorbike:     0.000 kg CO₂/km  (bike = bicycle, zero emissions)
  - Public transit: 0.089 kg CO₂/km (UK DEFRA average bus)
  - Walk:          0.000 kg CO₂/km
  - Meat-heavy diet: 3.3  kg CO₂/meal (Our World in Data global average)
  - Vegetarian:    1.7  kg CO₂/meal
  - Vegan:         1.1  kg CO₂/meal
  - Electricity:   0.82 kg CO₂/kWh  (India grid average, CEA 2023)

Users enter daily electricity consumption in kWh (read from meter or estimate
from monthly bill ÷ 30).  No intermediate laptop-draw conversion is needed.

All values are ESTIMATES for personal carbon awareness. They are NOT certified
for regulatory or scientific reporting.
"""

COMMUTE_FACTORS: dict[str, float] = {
    "car":            0.17,
    "bike":           0.000,
    "public_transit": 0.089,
    "walk":           0.000,
}

DIET_FACTORS: dict[str, float] = {
    "meat_heavy":  3.3,
    "vegetarian":  1.7,
    "vegan":       1.1,
}

ELECTRICITY_KG_PER_KWH: float = 0.82


# TESTED: returns 0.0 for unknown mode (no KeyError)
def calc_commute_kg(km: float, mode: str) -> float:
    """kg CO₂ from commuting distance and transport mode."""
    factor = COMMUTE_FACTORS.get(mode, 0.0)
    return round(km * factor, 4)


# TESTED: returns 0.0 for unknown diet type (no KeyError)
def calc_diet_kg(diet_type: str) -> float:
    """kg CO₂ from one day's diet."""
    return DIET_FACTORS.get(diet_type, 0.0)


# TESTED: electricity_kwh=0 returns 0.0; never raises
def calc_electricity_kg(electricity_kwh: float) -> float:
    """kg CO₂ from daily household electricity consumption in kWh."""
    return round(electricity_kwh * ELECTRICITY_KG_PER_KWH, 4)


# TESTED: sum of all three components; all inputs 0 returns 0.0
def calc_total_kg(
    commute_km: float,
    commute_mode: str,
    diet_type: str,
    electricity_kwh: float,
) -> float:
    """Total kg CO₂ for one day log entry."""
    commute  = calc_commute_kg(commute_km, commute_mode)
    diet     = calc_diet_kg(diet_type)
    elec     = calc_electricity_kg(electricity_kwh)
    return round(commute + diet + elec, 4)
