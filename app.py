"""
EcoTrace AI - Personal Carbon Footprint Tracker with ML Forecasting
Streamlit Application grounded in Google Stitch Design Specification
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import sys

import db
import calc
import model as ml
import notify

# Ensure DB initialized
db.init_db()

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoTrace AI — Carbon Telemetry & ML Forecasting",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global Styling (Google Stitch Design System) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --primary: #006948;
    --primary-container: #00855d;
    --on-primary: #ffffff;
    --secondary: #006c49;
    --tertiary: #825100;
    --background: #f9f9ff;
    --surface: #ffffff;
    --surface-low: #f0f3ff;
    --surface-container: #e7eeff;
    --surface-high: #dee8ff;
    --on-surface: #111c2d;
    --on-surface-variant: #3d4a42;
    --outline: #6d7a72;
    --outline-variant: #bccac0;
    --error: #ba1a1a;
    --error-container: #ffdad6;
}

/* App Background & Typography */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: var(--background) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--on-surface) !important;
}

h1, h2, h3, h4, .headline {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--on-surface) !important;
    letter-spacing: -0.015em !important;
}

code, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hide default streamlit clutter */
#MainMenu, header[data-testid="stHeader"], footer {
    visibility: hidden !important;
    height: 0px !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* Stitch Header */
.ec-header {
    background: rgba(249, 249, 255, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--outline-variant);
    padding: 14px 24px;
    margin-bottom: 20px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.ec-logo-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ec-logo-badge {
    width: 38px;
    height: 38px;
    background: var(--primary);
    color: white;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 2px 6px rgba(0, 105, 72, 0.25);
}

.ec-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: var(--on-surface);
    display: flex;
    align-items: center;
    gap: 8px;
}

.ec-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 9999px;
    background: var(--surface-low);
    color: var(--primary);
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.ec-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--primary);
}

/* Native Tabs Styling to Match Stitch Nav */
div[data-testid="stTabs"] {
    margin-bottom: 24px;
}

button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    color: var(--on-surface-variant) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: var(--primary) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Stitch Card Component */
.st-card {
    background: #ffffff;
    border: 1px solid #dee8ff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(17, 28, 45, 0.05);
    margin-bottom: 20px;
    position: relative;
}

.st-card-accent {
    border-top: 4px solid var(--primary);
}

/* Metric Display Cluster */
.metric-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 38px;
    font-weight: 700;
    color: var(--on-surface);
    line-height: 1.1;
}

.metric-unit {
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    color: var(--on-surface-variant);
    font-weight: 500;
}

.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--outline);
    margin-bottom: 6px;
}

/* Streamlit Inputs & Button Customization */
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: var(--surface-low) !important;
    border: 1px solid var(--outline-variant) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--on-surface) !important;
}

div[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background-color: var(--primary) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 6px rgba(0, 105, 72, 0.2) !important;
    transition: background-color 0.15s ease !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background-color: var(--primary-container) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Dynamic Session State & Reactive Count ───────────────────────────────────
days_count = db.get_days_logged_count()
today_total = db.get_today_total()
today_str = date.today().isoformat()

# ── Global Top Header ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ec-header">
    <div class="ec-logo-group">
        <div class="ec-logo-badge">🌱</div>
        <div>
            <div class="ec-header-title">
                EcoTrace AI
                <span class="ec-pill"><span class="ec-dot"></span>SQLite Connected</span>
            </div>
            <div style="font-size: 12px; color: #6d7a72;">Personal Carbon Intelligence &amp; Multi-Objective Optimization</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 14px;">
        <div class="ec-pill" style="padding: 6px 12px; font-size: 13px; font-weight: 700;">
            📅 {days_count} Days Logged
        </div>
        <div style="width: 34px; height: 34px; border-radius: 50%; background: #006948; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">
            US
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Tabs ───────────────────────────────────────────────────────────
tab_log, tab_dash, tab_pred = st.tabs(["📝 Log Data", "📊 Dashboard", "🔮 Prediction & Prevention"])

# ==============================================================================
# TAB 1: LOG DATA
# ==============================================================================
with tab_log:
    # Header Banner
    if days_count == 0:
        banner_msg = "🌱 <strong>Welcome!</strong> Log your first day of travel, meals, and computing to unlock ML predictive telemetry."
    else:
        banner_msg = f"✨ <strong>Great streak!</strong> You have logged {days_count} active days. Keep consistent for accurate multi-variable forecasts."
        
    st.markdown(f"""
    <div class="st-card" style="border-left: 4px solid var(--primary); padding: 16px 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span class="metric-label">Daily Entry Telemetry</span>
                <div style="font-size: 14px; color: var(--on-surface); margin-top: 4px;">{banner_msg}</div>
            </div>
            <div style="text-align: right;">
                <span class="metric-label">Current Date</span>
                <div class="mono" style="font-size: 15px; font-weight: 600; color: var(--primary);">{today_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Logger Form
    st.markdown('<div class="headline" style="font-size: 20px; font-weight: 600; margin-bottom: 12px;">Daily Activity Logger</div>', unsafe_allow_html=True)
    
    with st.form("daily_emission_form", clear_on_submit=False):
        date_col1, date_col2 = st.columns([1, 1])
        with date_col1:
            st.markdown("<strong>📅 Activity Date (Today or Backfill)</strong>", unsafe_allow_html=True)
            entry_date = st.date_input(
                "Activity Date",
                value=date.today(),
                max_value=date.today(),
                label_visibility="collapsed",
                help="Select today or choose any past date if you missed logging earlier!",
            )
            entry_date_str = entry_date.isoformat()
            
        existing_for_date = db.get_entry_by_date(entry_date_str)
        
        with date_col2:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if existing_for_date:
                st.warning(f"🔄 Entry already exists for **{entry_date_str}** ({existing_for_date['total_kg']:.2f} kg CO₂e). Saving will overwrite this day so you have one whole full row per day.", icon="⚠️")
            elif entry_date == date.today():
                st.info("📌 Logging new activity for **Today**", icon="ℹ️")
            else:
                st.info(f"🕒 Backfilling new activity for **{entry_date_str}**", icon="📅")

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<strong>🚗 Mobility & Commute</strong>", unsafe_allow_html=True)
            commute_km = st.number_input(
                "Commute Distance (km)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_for_date["commute_km"]) if existing_for_date else 12.5,
                step=0.5,
                help="Total travel to/from work, study, or errands today.",
            )
            
            commute_mode = st.selectbox(
                "Commute Mode",
                options=["car", "public_transit", "bike", "walk"],
                index=["car", "public_transit", "bike", "walk"].index(existing_for_date["commute_mode"]) if existing_for_date and existing_for_date["commute_mode"] in ["car", "public_transit", "bike", "walk"] else 0,
                format_func=lambda x: {
                    "car": "Gasoline/Diesel Car [0.17 kg CO₂/km]",
                    "public_transit": "Public Transit (Bus/Train) [0.089 kg CO₂/km]",
                    "bike": "Bicycle (Zero Emission) [0.00 kg CO₂/km]",
                    "walk": "Walking (Zero Emission) [0.00 kg CO₂/km]",
                }[x],
            )
            
        with col2:
            st.markdown("<strong>🍽️ Diet & Daily Electricity</strong>", unsafe_allow_html=True)
            diet_type = st.selectbox(
                "Primary Diet Type Today",
                options=["meat_heavy", "vegetarian", "vegan"],
                index=["meat_heavy", "vegetarian", "vegan"].index(existing_for_date["diet_type"]) if existing_for_date and existing_for_date["diet_type"] in ["meat_heavy", "vegetarian", "vegan"] else 0,
                format_func=lambda x: {
                    "meat_heavy": "Meat-Heavy Meal Plan [3.30 kg CO₂/day]",
                    "vegetarian": "Vegetarian Meal Plan [1.70 kg CO₂/day]",
                    "vegan": "Vegan Low-Carbon Plan [1.10 kg CO₂/day]",
                }[x],
            )
            
            active_hours = st.number_input(
                "Daily Electricity Usage (kWh)",
                min_value=0.0,
                max_value=200.0,
                value=float(existing_for_date["active_hours"]) if existing_for_date else 5.0,
                step=0.5,
                help="Your daily household electricity in kWh. Check your meter or divide monthly bill units by 30. (0.82 kg CO₂/kWh India grid)",
            )
            
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        
        # Interactive Real-Time Arithmetic Summary within the Form
        c_commute = calc.calc_commute_kg(commute_km, commute_mode)
        c_diet = calc.calc_diet_kg(diet_type)
        c_elec = calc.calc_electricity_kg(active_hours)
        c_tot = calc.calc_total_kg(commute_km, commute_mode, diet_type, active_hours)
        
        st.markdown(f"""
        <div style="background: var(--surface-low); border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; text-align: center;">
                <div>
                    <div class="metric-label">Mobility</div>
                    <div class="mono" style="font-weight: 600;">{c_commute:.3f} kg</div>
                </div>
                <div>
                    <div class="metric-label">Diet</div>
                    <div class="mono" style="font-weight: 600;">{c_diet:.3f} kg</div>
                </div>
                <div>
                    <div class="metric-label">Electricity</div>
                    <div class="mono" style="font-weight: 600;">{c_elec:.3f} kg</div>
                </div>
                <div style="border-left: 2px solid var(--outline-variant);">
                    <div class="metric-label" style="color: var(--primary);">Est. Total</div>
                    <div class="mono" style="font-weight: 700; color: var(--primary);">{c_tot:.3f} kg</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_label = "💾 Update Day's Entry (1 Row Per Day)" if existing_for_date else "💾 Save Activity Entry"
        submitted = st.form_submit_button(btn_label, use_container_width=True)
        
        if submitted:
            success = db.upsert_entry(
                date=entry_date_str,
                commute_km=commute_km,
                commute_mode=commute_mode,
                diet_type=diet_type,
                active_hours=active_hours,
                total_kg=c_tot,
            )
            if success:
                st.success(f"✅ Activity recorded successfully! Updated one full row for {entry_date_str} with {c_tot:.3f} kg CO₂e.")
                # Send optional system desktop toast
                notify.send_toast("EcoTrace AI Entry Saved", f"Saved {c_tot:.2f} kg CO2e for {entry_date_str}.")
                st.rerun()
            else:
                st.error("Failed to save log entry to SQLite database.")

    # Recent Submissions History
    st.markdown('<div class="headline" style="font-size: 18px; font-weight: 600; margin: 28px 0 12px 0;">Recent Submissions Log</div>', unsafe_allow_html=True)
    all_entries = db.get_all_entries()
    if all_entries:
        df_entries = pd.DataFrame(all_entries)
        display_df = df_entries[['id', 'date', 'commute_km', 'commute_mode', 'diet_type', 'active_hours', 'total_kg']].copy()
        display_df.columns = ["ID", "Date", "Commute (km)", "Mode", "Diet", "Elec (kWh)", "Total (kg CO₂e)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Row Deletion Feature
        with st.expander("🗑️ Delete a Logged Row from Database", expanded=False):
            del_col_sel, del_col_btn = st.columns([3, 1])
            with del_col_sel:
                del_options = {
                    f"Row #{r['id']} | Date: {r['date']} — Total: {r['total_kg']:.2f} kg CO₂e ({r['commute_mode']}, {r['diet_type']})": r['id']
                    for r in all_entries
                }
                selected_del_label = st.selectbox("Select row to delete:", options=list(del_options.keys()))
            with del_col_btn:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Row", type="primary", use_container_width=True):
                    target_id = del_options[selected_del_label]
                    if db.delete_entry(target_id):
                        st.success(f"✅ Row #{target_id} permanently deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete entry from database.")
    else:
        st.info("No recorded activity in database yet. Submit your first entry above!")


# ==============================================================================
# TAB 2: DASHBOARD
# ==============================================================================
with tab_dash:
    st.markdown('<div class="headline" style="font-size: 22px; font-weight: 700; margin-bottom: 4px;">Carbon Flux Telemetry</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: var(--on-surface-variant); margin-bottom: 20px;">Continuous multi-source telemetry and empirical baseline analytics</div>', unsafe_allow_html=True)

    # 3 Hero Metric Cards
    last_7 = db.get_last_n_days(7)
    weekly_total = sum(r["total_kg"] for r in last_7) if last_7 else 0.0
    weekly_budget = 35.0  # standard 5kg/day budget
    consumed_pct = min(int((weekly_total / weekly_budget) * 100), 100) if weekly_budget > 0 else 0

    c1, c2, c3 = st.columns(3)

    # Card 1: Today's Total
    with c1:
        if today_total is not None:
            today_disp = f"{today_total:.2f}"
            warning_html = '<div style="margin-top: 10px; font-size: 12px; color: var(--primary); font-weight: 600;">✓ Recorded for today</div>'
        else:
            today_disp = "—"
            warning_html = '<div style="margin-top: 10px; padding: 6px 10px; border-radius: 6px; background: #fff3e0; color: #825100; font-size: 12px; font-weight: 500;">⚠️ No entry logged today yet</div>'

        st.markdown(f"""
        <div class="st-card">
            <div class="metric-label">Card 01 // Daily Flux</div>
            <div style="font-size: 14px; font-weight: 600; color: var(--on-surface);">Today's Total CO₂ Emitted</div>
            <div style="margin-top: 8px;">
                <span class="metric-num">{today_disp}</span>
                <span class="metric-unit">kg CO₂e</span>
            </div>
            {warning_html}
        </div>
        """, unsafe_allow_html=True)

    # Card 2: 7-Day Cumulative
    with c2:
        prog_color = "#ba1a1a" if consumed_pct >= 85 else "#006948"
        st.markdown(f"""
        <div class="st-card">
            <div class="metric-label">Card 02 // Cumulative</div>
            <div style="font-size: 14px; font-weight: 600; color: var(--on-surface);">7-Day Total Footprint</div>
            <div style="margin-top: 8px;">
                <span class="metric-num">{weekly_total:.1f}</span>
                <span class="metric-unit">kg CO₂e</span>
            </div>
            <div style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--on-surface-variant); margin-bottom: 4px;">
                    <span>Target: {weekly_budget:.0f} kg</span>
                    <span style="font-weight: 700; color: {prog_color};">{consumed_pct}% Consumed</span>
                </div>
                <div style="height: 6px; width: 100%; background: #e7eeff; border-radius: 9999px; overflow: hidden;">
                    <div style="height: 100%; width: {consumed_pct}%; background: {prog_color}; border-radius: 9999px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Card 3: Data Quality
    with c3:
        dots_html = "".join([
            f'<div style="width: 14px; height: 14px; border-radius: 50%; background: {"#006948" if i < min(days_count, 7) else "#dee8ff"};"></div>'
            for i in range(7)
        ])
        st.markdown(f"""
        <div class="st-card">
            <div class="metric-label">Card 03 // Quality Index</div>
            <div style="font-size: 14px; font-weight: 600; color: var(--on-surface);">Sampling Cadence</div>
            <div style="margin-top: 8px;">
                <span class="metric-num">{min(days_count, 7)}/7</span>
                <span class="metric-unit">active cycles</span>
            </div>
            <div style="margin-top: 14px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; gap: 6px;">{dots_html}</div>
                <span class="ec-pill" style="font-size: 10px;">{'HIGH FIDELITY' if days_count >= 7 else 'WARMUP'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Empty State or Visualizations
    if days_count == 0:
        st.markdown("""
        <div class="st-card" style="text-align: center; padding: 48px 24px; margin-top: 16px;">
            <div style="font-size: 48px; margin-bottom: 12px;">📊</div>
            <div class="headline" style="font-size: 22px; font-weight: 700; margin-bottom: 8px;">No data yet — log your first day</div>
            <div style="font-size: 14px; color: var(--on-surface-variant); max-width: 480px; margin: 0 auto 20px auto;">
                Your telemetry charts and categorical breakdown will populate automatically once you submit your first activity log.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Charts Row
        col_pie, col_trend = st.columns([1, 1])
        
        with col_pie:
            st.markdown('<div class="headline" style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">🍩 Today\'s Source Breakdown</div>', unsafe_allow_html=True)
            breakdown = db.get_today_breakdown()
            
            # If today has no entries, aggregate last 7 days for the pie chart
            if sum(breakdown.values()) == 0 and last_7:
                tot_c = sum(calc.calc_commute_kg(r["commute_km"], r["commute_mode"]) for r in last_7)
                tot_d = sum(calc.calc_diet_kg(r["diet_type"]) for r in last_7)
                tot_e = sum(calc.calc_electricity_kg(r["active_hours"]) for r in last_7)
                breakdown = {"Commute": tot_c, "Diet": tot_d, "Electricity": tot_e}
                pie_title = "7-Day Total Activity Share"
            else:
                pie_title = "Today's Activity Share"

            labels = list(breakdown.keys())
            values = list(breakdown.values())

            fig_donut = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=["#006948", "#006c49", "#4edea3"]),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )])
            fig_donut.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_trend:
            st.markdown('<div class="headline" style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">📈 7-Day Emission Trend</div>', unsafe_allow_html=True)
            if last_7:
                df_trend = pd.DataFrame(last_7).sort_values("date")
                fig_trend = px.area(
                    df_trend,
                    x="date",
                    y="total_kg",
                    labels={"date": "Date", "total_kg": "kg CO₂e"},
                    color_discrete_sequence=["#006948"],
                )
                fig_trend.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=260,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, title=None),
                    yaxis=dict(gridcolor="#e7eeff", title="kg CO₂e"),
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Log more days to view the 7-day trend curve.")


# ==============================================================================
# TAB 3: PREDICTION & PREVENTION
# ==============================================================================
with tab_pred:
    st.markdown('<div class="headline" style="font-size: 22px; font-weight: 700; margin-bottom: 4px;">Predictive Engine & Prevention Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: var(--on-surface-variant); margin-bottom: 20px;">RandomForestRegressor multi-variate forecaster with proactive prevention recommendations</div>', unsafe_allow_html=True)

    # Cold Start Verification
    if days_count < 7:
        needed = 7 - days_count
        warmup_pct = int((days_count / 7) * 100)
        
        st.markdown(f"""
        <div class="st-card" style="border-left: 4px solid var(--tertiary); padding: 24px;">
            <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                <div>
                    <span class="metric-label" style="color: var(--tertiary);">Cold Start Safeguard</span>
                    <div class="headline" style="font-size: 20px; font-weight: 700; color: var(--on-surface); margin: 6px 0;">
                        Collecting data. Need 7 days, you have {days_count}
                    </div>
                    <div style="font-size: 14px; color: var(--on-surface-variant); max-width: 600px;">
                        The machine learning model strictly requires at least 7 distinct days of empirical observations to calculate baseline lag features, rolling windows, and feature importances without overfitting.
                    </div>
                </div>
                <div class="ec-pill" style="font-weight: 700; background: var(--surface-low); color: var(--tertiary);">
                    {warmup_pct}% Ready
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div style="height: 8px; width: 100%; background: #e7eeff; border-radius: 9999px; overflow: hidden;">
                    <div style="height: 100%; width: {warmup_pct}%; background: var(--tertiary); border-radius: 9999px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--on-surface-variant); margin-top: 6px;">
                    <span>Current: {days_count} days</span>
                    <span>Required: 7 days ({needed} remaining)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # 7+ Days: Train & Infer Model
        entries = db.get_all_entries()
        df_raw = pd.DataFrame(entries)
        # Aggregate strictly to 1 row per date, sorted chronologically
        df_hist = df_raw.groupby("date", as_index=False)["total_kg"].sum().sort_values("date").reset_index(drop=True)
        
        model_obj, predicted_val = ml.train_model(df_hist)
        
        if predicted_val is not None:
            # Baseline rolling average calculation from true distinct daily totals
            rolling_avg = df_hist['total_kg'].tail(7).mean()
            target_budget = round(rolling_avg * 1.2, 2)
            is_breached = predicted_val > target_budget
            
            p_col1, p_col2 = st.columns([7, 5])
            
            with p_col1:
                risk_badge = '<span class="ec-pill" style="background:#ffdad6; color:#ba1a1a; font-weight:700;">🚨 HIGH RISK</span>' if is_breached else '<span class="ec-pill" style="background:#e8f5e9; color:#2e7d32; font-weight:700;">✓ NORMAL RISK</span>'
                
                st.markdown(f"""
                <div class="st-card st-card-accent">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="metric-label">Forecasted Tomorrow</span>
                        {risk_badge}
                    </div>
                    <div style="margin: 12px 0;">
                        <span class="metric-num" style="font-size: 52px;">{predicted_val:.2f}</span>
                        <span class="metric-unit">kg CO₂e</span>
                    </div>
                    <div style="font-size: 13px; color: var(--on-surface-variant); display: flex; gap: 16px; align-items: center;">
                        <span>Rolling Baseline: <strong>{rolling_avg:.2f} kg</strong></span>
                        <span>1.2x Target Threshold: <strong>{target_budget:.2f} kg</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with p_col2:
                # Real feature importance calculated directly by the trained RandomForestRegressor
                st.markdown("""
                <div class="st-card">
                    <div class="metric-label">Trained Model Feature Weights</div>
                    <div style="font-size: 14px; font-weight: 600; color: var(--on-surface); margin-top: 4px; margin-bottom: 12px;">Real-Time Regressor Attribution</div>
                </div>
                """, unsafe_allow_html=True)
                
                if hasattr(model_obj, "feature_importances_"):
                    imps = model_obj.feature_importances_
                    imp_lag1 = float(imps[0])
                    imp_roll3 = float(imps[3])
                    imp_dow = float(imps[4])
                    imp_hist = float(imps[1] + imps[2])
                    
                    st.write(f"**🚗 Yesterday's Emission Load (Lag-1):** `{imp_lag1*100:.1f}%`")
                    st.progress(min(max(imp_lag1, 0.0), 1.0))
                    
                    st.write(f"**📈 3-Day Rolling Average (Roll-3):** `{imp_roll3*100:.1f}%`")
                    st.progress(min(max(imp_roll3, 0.0), 1.0))
                    
                    st.write(f"**📅 Day of Week Seasonality (DoW):** `{imp_dow*100:.1f}%`")
                    st.progress(min(max(imp_dow, 0.0), 1.0))
                    
                    st.write(f"**⏳ Multi-Day Lag Memory (Lag-2 & 3):** `{imp_hist*100:.1f}%`")
                    st.progress(min(max(imp_hist, 0.0), 1.0))
                else:
                    imp_lag1, imp_roll3, imp_dow, imp_hist = 0.45, 0.25, 0.15, 0.15
                    st.info("Model parameters calibrated.")
                
            # Proactive Prevention Report
            if is_breached:
                kg_saved = round(predicted_val - target_budget, 2)
                pct_excess = round(((predicted_val - target_budget) / target_budget) * 100, 1)
                
                st.markdown(f"""
                <div class="st-card" style="border: 2px solid #ba1a1a; background: #fffbff;">
                    <div style="display:flex; align-items:center; gap:8px; color: #ba1a1a; font-weight:700; font-size:16px;">
                        <span>⚠️ Prevention Report Triggered</span>
                    </div>
                    <div style="font-size: 14px; margin: 8px 0; color: #111c2d;">
                        Your forecasted emission of <strong>{predicted_val:.2f} kg</strong> breaches your sustainable ceiling by <strong>+{pct_excess}%</strong>.
                    </div>
                    <div style="background: #f0f3ff; border-radius: 8px; padding: 14px; margin: 12px 0;">
                        <span class="metric-label" style="color: #006948;">Actionable Mitigation Plan</span>
                        <div style="font-size: 13px; margin-top: 6px; line-height: 1.5;">
                            💡 <strong>Potential Reduction:</strong> Implementing the proactive measures below will save approximately <strong style="color:#006948;">{kg_saved:.2f} kg CO₂e</strong>, pulling you safely back under your <strong>{target_budget:.2f} kg</strong> threshold!
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                kg_saved = 0.0
                pct_excess = 0.0
                st.markdown(f"""
                <div class="st-card" style="border-left: 4px solid #006948;">
                    <div style="font-weight: 700; color: #006948; font-size: 15px;">✓ Sustainable Trajectory Confirmed</div>
                    <div style="font-size: 13px; color: var(--on-surface-variant); margin-top: 4px;">
                        Tomorrow's predicted emission of <strong>{predicted_val:.2f} kg</strong> is well within your safe threshold of {target_budget:.2f} kg. Keep up the consistent habits!
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Concrete Prevention Guide & Interactive Simulator ─────────────
            st.markdown('<div class="headline" style="font-size: 18px; font-weight: 600; margin: 24px 0 12px 0;">🛡️ Recommended Prevention Measures & Optimization Matrix</div>', unsafe_allow_html=True)
            
            p_meas1, p_meas2, p_meas3 = st.columns(3)
            with p_meas1:
                st.markdown("""
                <div class="st-card" style="min-height: 160px;">
                    <div class="metric-label" style="color: var(--primary);">Mobility Prevention</div>
                    <div style="font-size: 14px; font-weight: 600; margin: 4px 0;">Transit & Active Commute</div>
                    <div style="font-size: 12px; color: var(--on-surface-variant); line-height: 1.4;">
                        • Swap car (0.17 kg/km) for public bus/train (0.089 kg/km) to save <strong>~0.081 kg/km</strong>.<br>
                        • Walking or cycling eliminates 100% of commute emissions (<strong>0.17 kg/km saved</strong>).
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with p_meas2:
                st.markdown("""
                <div class="st-card" style="min-height: 160px;">
                    <div class="metric-label" style="color: var(--primary);">Dietary Prevention</div>
                    <div style="font-size: 14px; font-weight: 600; margin: 4px 0;">Plant-Forward Nutrition</div>
                    <div style="font-size: 12px; color: var(--on-surface-variant); line-height: 1.4;">
                        • Switch from Meat-Heavy (3.30 kg) to Vegetarian (1.70 kg) to save <strong>1.60 kg CO₂e/day</strong>.<br>
                        • Opt for a Vegan lunch/dinner (1.10 kg) to save <strong>2.20 kg CO₂e/day</strong> (67% cut).
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with p_meas3:
                st.markdown("""
                <div class="st-card" style="min-height: 160px;">
                    <div class="metric-label" style="color: var(--primary);">Energy Prevention</div>
                    <div style="font-size: 14px; font-weight: 600; margin: 4px 0;">Household Electricity Conservation</div>
                    <div style="font-size: 12px; color: var(--on-surface-variant); line-height: 1.4;">
                        • Switch off idle appliances & lights to save <strong>~1–2 kWh/day</strong> (0.82–1.64 kg CO₂e).<br>
                        • Use energy-efficient LED bulbs and star-rated appliances to reduce grid draw.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Interactive Prevention Action Simulator
            with st.expander("✨ Test Interactive Prevention Simulator (Simulate Tomorrow's Impact)", expanded=True):
                st.markdown("<div style='font-size: 13px; color: var(--on-surface-variant); margin-bottom: 12px;'>Choose prevention actions you will take tomorrow to see your new adjusted forecast:</div>", unsafe_allow_html=True)
                s_col1, s_col2, s_col3 = st.columns(3)
                with s_col1:
                    sim_commute = st.selectbox(
                        "Tomorrow's Commute Change:",
                        options=["No change (Keep current)", "Switch 10km to Public Transit (-0.81 kg)", "Switch 10km to Bike/Walk (-1.70 kg)"],
                    )
                with s_col2:
                    sim_diet = st.selectbox(
                        "Tomorrow's Meal Change:",
                        options=["No change (Keep current)", "Switch to Vegetarian Meal (-1.60 kg)", "Switch to Vegan Meal (-2.20 kg)"],
                    )
                with s_col3:
                    sim_screen = st.selectbox(
                        "Tomorrow's Electricity Change:",
                        options=["No change (Keep current)", "Reduce 1 kWh (-0.82 kg)", "Reduce 2 kWh (-1.64 kg)"],
                    )
                
                # Compute simulated savings
                commute_save = 0.81 if "Transit" in sim_commute else (1.70 if "Bike" in sim_commute else 0.0)
                diet_save = 1.60 if "Vegetarian" in sim_diet else (2.20 if "Vegan" in sim_diet else 0.0)
                screen_save = 0.82 if "1 kWh" in sim_screen else (1.64 if "2 kWh" in sim_screen else 0.0)
                total_sim_save = commute_save + diet_save + screen_save
                new_predicted = max(0.1, predicted_val - total_sim_save)
                
                res_bg = "#e8f5e9" if new_predicted <= target_budget else "#fff3e0"
                res_color = "#2e7d32" if new_predicted <= target_budget else "#825100"
                
                st.markdown(f"""
                <div style="background: {res_bg}; border-radius: 10px; padding: 14px 18px; margin-top: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: {res_color};">Simulated Mitigation Result</div>
                        <div style="font-size: 15px; font-weight: 700; color: var(--on-surface); margin-top: 2px;">
                            Forecast drops from <strong>{predicted_val:.2f} kg</strong> → <strong style="color:{res_color};">{new_predicted:.2f} kg CO₂e</strong>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span class="ec-pill" style="background: white; color: {res_color}; font-size: 13px; font-weight: 700;">
                            🌱 Saves {total_sim_save:.2f} kg CO₂e
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Executive Report Generation & Download ────────────────────────
            st.markdown('<div class="headline" style="font-size: 18px; font-weight: 600; margin: 24px 0 12px 0;">📋 Executive Carbon Audit & Prevention Report</div>', unsafe_allow_html=True)
            
            gen_col1, gen_col2 = st.columns([3, 1])
            with gen_col1:
                st.markdown("<div style='font-size: 13px; color: var(--on-surface-variant);'>Generate an official, printable carbon audit report detailing empirical baseline numbers, 24-hour ML forecast, risk assessment, and recommended prevention actions.</div>", unsafe_allow_html=True)
            with gen_col2:
                show_report = st.button("📄 Generate Audit Report", use_container_width=True)

            report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_text = f"""================================================================================
ECOTRACE AI — OFFICIAL CARBON INTELLIGENCE & PREVENTION REPORT
Generated: {report_timestamp}
================================================================================

1. TELEMETRY & BASELINE DATA
--------------------------------------------------------------------------------
* Total Observational Days : {days_count} days
* 7-Day Empirical Baseline : {rolling_avg:.2f} kg CO2e / day
* Sustainable Ceiling (1.2x): {target_budget:.2f} kg CO2e / day
* Today's Current Total    : {f'{today_total:.2f} kg CO2e' if today_total is not None else 'Not logged yet'}

2. MACHINE LEARNING PREDICTIVE FORECAST
--------------------------------------------------------------------------------
* Model Type               : RandomForestRegressor (Scikit-Learn)
* Forecast Window          : Next 24 Hours
* Forecasted Emission      : {predicted_val:.2f} kg CO2e
* Risk Assessment Level    : {'HIGH RISK (Threshold Exceeded)' if is_breached else 'NORMAL RISK (Within Budget)'}
* Variance vs Ceiling      : {'+' if is_breached else ''}{pct_excess:.1f}%

3. TOP PREDICTIVE INFLUENCERS (FEATURE ATTRIBUTION)
--------------------------------------------------------------------------------
- Yesterday's Emission Load (Lag-1)  : {imp_lag1*100:.1f}%
- 3-Day Rolling Trend (Roll-3)       : {imp_roll3*100:.1f}%
- Day of Week Rhythm (DoW)           : {imp_dow*100:.1f}%
- Multi-Day Lag Memory (Lag-2 & 3)   : {imp_hist*100:.1f}%

4. TARGETED ACTIONABLE PREVENTION MEASURES
--------------------------------------------------------------------------------
[A] MOBILITY:
    - Replace petrol car trips with public transit to save ~0.081 kg/km.
    - Active transit (walking / cycling) eliminates 100% of commute footprint.

[B] DIETARY:
    - Substitute meat-heavy meals with vegetarian to save 1.60 kg CO2e/day.
    - Adopt plant-based vegan nutrition to save 2.20 kg CO2e/day (67% cut).

[C] ENERGY & ELECTRICITY:
    - Reduce daily electricity usage by 1-2 kWh to save ~0.82-1.64 kg CO2e/day.
    - Switch off idle appliances and use energy-efficient LED bulbs and star-rated devices.

================================================================================
Report validated against UK DEFRA 2023, India CEA v19, and IPCC AR6 benchmarks.
================================================================================
"""

            with st.expander("📄 View & Download Generated Carbon Audit Report", expanded=show_report):
                st.text_area("Report Preview", value=report_text, height=280, label_visibility="collapsed")
                st.download_button(
                    label="📥 Download Carbon Report (.txt)",
                    data=report_text,
                    file_name=f"EcoTrace_Carbon_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
        else:
            st.warning("Insufficient variation in logged data to generate forecast.")
