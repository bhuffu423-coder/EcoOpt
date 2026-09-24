# EcoTrace AI 🌿

Personal carbon footprint tracker with ML-powered prediction.
**Every displayed number comes from your real SQLite data — no hardcoded demo values.**

---

## Requirements

- Windows 10/11
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
| `app.py` | Streamlit UI — 3 tabs, no inline SQL or math |
| `db.py` | All SQLite access: init, read, write |
| `calc.py` | Pure emission factor functions |
| `model.py` | RandomForest predictor; returns None < 7 days |
| `notify.py` | Desktop toast: win10toast → plyer → console |
| `scheduler_setup.py` | Windows Task Scheduler daily launch registration |
| `tests/` | pytest tests (43 assertions) |
| `ecotrace.db` | Auto-created SQLite database |

---

## Emission Factors Used

| Source | Factor |
|---|---|
| Car | 0.17 kg CO₂/km (UK DEFRA 2023) |
| Public transit | 0.089 kg CO₂/km (UK DEFRA 2023) |
| Bike / Walk | 0.000 kg CO₂/km |
| Meat-heavy diet | 3.3 kg CO₂/day (Our World in Data) |
| Vegetarian diet | 1.7 kg CO₂/day |
| Vegan diet | 1.1 kg CO₂/day |
| Laptop electricity | 0.05 kWh/hr × 0.82 kg/kWh (CEA India 2023) |

*All values are estimates for personal awareness only.*

---

## Manual Test Checklist

1. **Empty state** — Open app with no database. All 3 tabs must show "No data yet" messages without crashing.
2. **Log first entry** — Tab "Log Data": enter `commute_km=10`, mode=`car`, diet=`meat_heavy`, screen hrs=`8`. Click Save. Verify success message shows `5.548 kg CO₂`.
3. **Breakdown arithmetic** — Commute: `10 × 0.17 = 1.920`, Diet: `3.3`, Electricity: `8 × 0.05 × 0.82 = 0.328`. Total = `5.548`. Confirm in success message.
4. **Dashboard metrics** — Switch to Tab "Dashboard". Verify `today_total_kg` matches entry just saved. Pie chart shows three slices.
5. **Under-7-days state** — Tab "Prediction & Prevention" must display `"Collecting data… Need 7 days, you have 1"`.
6. **Log 6 more distinct days** — Use the form 6 more times (or directly insert rows into `ecotrace.db` with different dates). Prediction tab should now train and display a predicted value.
7. **High-emission alert** — After 7 days, edit a row in the DB so total_kg > 7.0. Verify the orange alert card appears.
8. **Zero input** — Log `commute_km=0`, `walk`, `vegan`, `active_hours=0`. Verify total = `1.1` (vegan diet only).
9. **Recent entries table** — Tab "Log Data" bottom section shows the 10 most recent entries in correct order (newest first).
10. **Scheduler** — Run `python scheduler_setup.py` from the EcoOpt folder. Verify it prints the schtasks command and "registered successfully" (requires admin or appropriate account rights).

---

## Run Tests

```bash
cd "C:\Users\Sankaran\Desktop\EcoOpt"
python -m pytest tests/ -v
```

Expected: **43 passed**

---

## Optional: Desktop Notifications

```bash
pip install win10toast       # preferred
# OR
pip install plyer            # fallback
```

If neither is installed, notifications print to console (app never crashes).
