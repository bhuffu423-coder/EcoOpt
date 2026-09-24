"""
model.py — ML prediction layer for EcoTrace AI.
Trains a RandomForestRegressor on historical daily totals.
Returns None when fewer than 7 days of data are available.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import streamlit as st

# TESTED: returns (None, None) when df has fewer than 7 rows; never raises
@st.cache_data
def train_model(df: pd.DataFrame) -> tuple[object, float] | tuple[None, None]:
    """
    Train a RandomForestRegressor on daily total_kg values.

    Parameters
    ----------
    df : pd.DataFrame with columns [date, total_kg] (one row per distinct day).
         Caller must pass at least 7 rows; otherwise (None, None) is returned.

    Returns
    -------
    (model, predicted_value_for_tomorrow) or (None, None)
    """
    if df is None or len(df) < 7:
        return None, None

    try:
        from sklearn.ensemble import RandomForestRegressor

        # Build time-series features: lag-1 to lag-3, day-of-week, rolling mean
        df = df.sort_values("date").reset_index(drop=True)
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date_parsed"])

        if len(df) < 7:
            return None, None

        df["lag1"] = df["total_kg"].shift(1)
        df["lag2"] = df["total_kg"].shift(2)
        df["lag3"] = df["total_kg"].shift(3)
        df["roll3"] = df["total_kg"].rolling(3).mean()
        df["dow"]  = df["date_parsed"].dt.dayofweek

        # Drop rows that have NaN due to shifts
        df_model = df.dropna(subset=["lag1", "lag2", "lag3", "roll3"])

        if len(df_model) < 3:
            return None, None

        feature_cols = ["lag1", "lag2", "lag3", "roll3", "dow"]
        X = df_model[feature_cols].values
        y = df_model["total_kg"].values

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Predict tomorrow using latest available data
        last_row = df.iloc[-1]
        last3 = df["total_kg"].iloc[-3:].values
        lag1  = float(last3[-1]) if len(last3) >= 1 else 0.0
        lag2  = float(last3[-2]) if len(last3) >= 2 else lag1
        lag3  = float(last3[-3]) if len(last3) >= 3 else lag2
        roll3 = float(np.mean(last3))
        tomorrow_dow = (last_row["date_parsed"].dayofweek + 1) % 7

        X_pred = np.array([[lag1, lag2, lag3, roll3, tomorrow_dow]])
        predicted = float(model.predict(X_pred)[0])
        predicted = max(predicted, 0.0)  # clamp to non-negative

        return model, round(predicted, 3)

    except Exception as e:
        print(f"[model.py] train_model error: {e}")
        return None, None


# TESTED: returns ("Unknown", 0.0) when df is empty
def get_biggest_contributor(df_today_breakdown: dict) -> tuple[str, float]:
    """
    Given a breakdown dict {'Commute': kg, 'Diet': kg, 'Electricity': kg},
    return the biggest contributor name and its value.
    """
    if not df_today_breakdown:
        return "Unknown", 0.0
    biggest = max(df_today_breakdown, key=lambda k: df_today_breakdown[k])
    return biggest, df_today_breakdown[biggest]


SUGGESTIONS: dict[str, str] = {
    "Commute": (
        "Try switching to public transit or cycling for your commute — "
        "even 2 days per week can cut your transport emissions by 40 %."
    ),
    "Diet": (
        "Consider one meat-free day this week. Replacing one meat-heavy meal "
        "with a vegetarian option saves ~1.6 kg CO₂."
    ),
    "Electricity": (
        "Cut daily electricity use by 1–2 kWh (switch off idle appliances, "
        "use energy-efficient lighting). Each kWh saved cuts ~0.82 kg CO₂."
    ),
    "Unknown": "Log more data to receive personalised suggestions.",
}


# TESTED: returns suggestion string for every valid key; never raises
def get_suggestion(contributor: str) -> str:
    return SUGGESTIONS.get(contributor, SUGGESTIONS["Unknown"])
