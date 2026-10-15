# EcoTrace AI 🌿

Personal carbon footprint tracker with ML-powered forecasting and multi-user telemetry.
**Every displayed number comes from your real SQLite data — no hardcoded demo values.**

---

## Key Features

- **🔐 Multi-User Authentication:** Secure user registration and login powered by salted PBKDF2-HMAC-SHA256 password hashing. Every user's data, baseline metrics, and ML forecasts are strictly isolated.
- **⚡ Direct Household Electricity (kWh):** Direct tracking in kilowatt-hours (kWh) reflecting actual meter readings or bill averages, calibrated to the regional electric grid factor (0.82 kg CO₂/kWh).
- **⚡ Instant Reactive Telemetry:** Tab 1 provides immediate real-time arithmetic feedback as you change mobility, diet, or electricity inputs.
- **🔮 Time-Series ML Forecasting:** `RandomForestRegressor` with continuous-calendar lag windows and regularization (`max_depth=4`, `min_samples_leaf=2`) predicting 24-hour emissions.
- **🛡️ Actionable Prevention Matrix:** Interactive simulator modeling the impact of tomorrow's habit changes in real-time, plus exportable executive audit reports.

---

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10+

---

## Installation

```bash
# Clone / download the EcoOpt folder then:
pip install streamlit pandas scikit-learn plotly pytest
```

---

## Run the App

```bash
cd "C:\Users\Sankaran\Desktop\EcoOpt"
python -m streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## File Structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI — Google Stitch Design, Auth Gate, 3 tabs, reactive live telemetry |
| `db.py` | Multi-user SQLite layer with safe context managers, auth hashing, and user isolation |
| `calc.py` | Pure emission factor calculation functions |
| `model.py` | Regularized RandomForest predictor with continuous-calendar interpolation |
| `notify.py` | Desktop notifications wrapper: win10toast → plyer → console |
| `scheduler_setup.py` | Windows Task Scheduler daily launch registration |
| `tests/` | Comprehensive pytest test suite (61 assertions across 4 test modules) |
| `ecotrace.db` | Auto-created SQLite database (ignored by git) |

---

## Emission Factors Used

| Source | Factor | Reference |
|---|---|---|
| Car | 0.170 kg CO₂/km | UK DEFRA 2023 average petrol car |
| Public transit | 0.089 kg CO₂/km | UK DEFRA 2023 average bus |
| Bike / Walk | 0.000 kg CO₂/km | Zero-emission active transit |
| Meat-heavy diet | 3.300 kg CO₂/day | Our World in Data global benchmark |
| Vegetarian diet | 1.700 kg CO₂/day | Our World in Data plant-forward benchmark |
| Vegan diet | 1.100 kg CO₂/day | Our World in Data vegan benchmark |
| Household Electricity | 0.820 kg CO₂/kWh | CEA India 2023 grid emission factor |

*All values are estimates for personal awareness and optimization.*

---

## Manual Test Checklist

1. **Authentication Gate** — Launch the app. If unauthenticated, the Stitch login card appears with "Sign In" and "Create Account" tabs. Main tabs are protected.
2. **Account Creation** — Create an account (e.g., username `testuser`, password `password123`). The app authenticates immediately and loads the user profile with dynamic avatar badge and username pill.
3. **Log First Entry** — Tab 1 ("Log Data"): choose today's date, enter `commute_km=10.0`, mode=`car`, diet=`meat_heavy`, and electricity=`5.0 kWh`.
4. **Live Arithmetic Preview** — Observe the live summary bar before saving:
   - Mobility: `10.0 × 0.170 = 1.700 kg`
   - Diet: `3.300 kg`
   - Electricity: `5.0 × 0.820 = 4.100 kg`
   - **Est. Total: `9.100 kg CO₂e`**
5. **Save Entry & Upsert** — Click "Save Activity Entry". A confirmation toast appears, and the submission log updates. Change a value on the same date and click "Update Day's Entry" — verify the existing row updates without creating a duplicate.
6. **Multi-User Data Isolation** — Click "Logout". Create a second user account (e.g., `user2`). Verify 0 days logged and empty submission history. Log back into `testuser` and verify all entries persist intact.
7. **Dashboard Telemetry** — Switch to Tab 2 ("Dashboard"). Today's total metric card displays `9.10 kg CO₂e`, and the categorical donut chart displays proportional shares.
8. **Cold Start & 7-Day Forecasting** — Tab 3 ("Prediction & Prevention") displays the Cold Start Safeguard until 7 distinct days are recorded. With 7+ days, the RandomForest model trains and outputs tomorrow's predicted emission, feature importances, and prevention simulator.
9. **Executive Audit Report** — Click "Generate Audit Report" in Tab 3. Verify the report preview generates complete telemetry, ML attribution, and prevention plans, and download the `.txt` report.

---

## Run Automated Tests

Run the complete 61-test suite:

```bash
python -m pytest tests/ -v
```

Expected output: **61 passed in ~20s**
- `tests/test_calc.py`: 20 unit tests for emission factors and zero-handling
- `tests/test_db.py`: 18 tests for schema, context managers, and query isolation
- `tests/test_ecotrace.py`: 12 integration tests for auth security, multi-user isolation, and gap handling
- `tests/test_model.py`: 11 tests for continuous-calendar interpolation and regressor fitting
