"""Migrate existing ecotrace.db: convert active_hours from screen-hours to kWh."""
import sqlite3
from calc import calc_commute_kg, calc_diet_kg, calc_electricity_kg

DB_PATH = "ecotrace.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

rows = cursor.execute("SELECT * FROM entries").fetchall()
print(f"Migrating {len(rows)} rows: active_hours (screen hours) -> kWh")

for r in rows:
    old_hours = r["active_hours"]
    # Convert old screen hours to kWh: hours * 0.05 kWh/hr
    new_kwh = round(old_hours * 0.05, 4)

    # Recalculate total_kg with the new formula
    commute_kg = calc_commute_kg(r["commute_km"], r["commute_mode"])
    diet_kg = calc_diet_kg(r["diet_type"])
    elec_kg = calc_electricity_kg(new_kwh)
    new_total = round(commute_kg + diet_kg + elec_kg, 4)

    rid = r["id"]
    rdate = r["date"]
    old_total = r["total_kg"]
    print(f"  Row #{rid} | {rdate} | {old_hours}h -> {new_kwh} kWh | total: {old_total} -> {new_total}")

    cursor.execute(
        "UPDATE entries SET active_hours = ?, total_kg = ? WHERE id = ?",
        (new_kwh, new_total, rid),
    )

conn.commit()
print("Migration complete!")

# Verify
rows2 = cursor.execute("SELECT * FROM entries ORDER BY date").fetchall()
for r in rows2:
    rid = r["id"]
    rdate = r["date"]
    ekwh = r["active_hours"]
    tot = r["total_kg"]
    print(f"  Verified Row #{rid} | date={rdate} | elec_kwh={ekwh} | total={tot}")
conn.close()
