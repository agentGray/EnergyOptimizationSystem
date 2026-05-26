"""Main Streamlit dashboard application."""

import streamlit as st

st.set_page_config(
    page_title="Energy Optimization Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.title("⚡ Energy Platform")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- 🏠 Live Dashboard
- 🔍 Anomaly Detection
- ⚖️ Load Dispatch
- 🏭 Asset Health
- 🌱 ESG & ISO 50001
""")
st.sidebar.markdown("---")
st.sidebar.markdown("**Status:** 🟢 Connected")
st.sidebar.markdown("**Last Update:** Real-time")

# Main page content
st.title("🏭 Industrial AI Energy Optimization")
st.markdown("### Real-Time Factory Energy Dashboard")
st.markdown("---")

# Top KPI metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Power",
        value="2,450 kW",
        delta="-120 kW",
        delta_color="inverse",
    )

with col2:
    st.metric(
        label="Energy Today",
        value="18,200 kWh",
        delta="-890 kWh",
        delta_color="inverse",
    )

with col3:
    st.metric(
        label="Active Anomalies",
        value="3",
        delta="+1",
        delta_color="inverse",
    )

with col4:
    st.metric(
        label="Savings Today",
        value="$245.30",
        delta="+$32.10",
    )

st.markdown("---")

# Energy consumption chart
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("⚡ Real-Time Energy Consumption")
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta

    # Generate sample data
    hours = pd.date_range(
        start=datetime.now() - timedelta(hours=24),
        end=datetime.now(),
        freq="15min",
    )
    np.random.seed(42)
    base_load = 1800
    power_data = base_load + 400 * np.sin(
        np.linspace(0, 2 * np.pi, len(hours))
    ) + np.random.normal(0, 50, len(hours))

    chart_df = pd.DataFrame({
        "Time": hours,
        "Power (kW)": power_data,
        "Baseline (kW)": [base_load] * len(hours),
    })
    chart_df = chart_df.set_index("Time")
    st.line_chart(chart_df)

with col_right:
    st.subheader("🏭 Asset Status")
    status_data = {
        "Status": ["Running", "Idle", "Maintenance", "Offline"],
        "Count": [12, 3, 2, 1],
    }
    st.bar_chart(pd.DataFrame(status_data).set_index("Status"))

    st.subheader("🔔 Recent Alerts")
    st.warning("⚠️ HVAC-03: Overcooling detected")
    st.error("🔴 Compressor-01: Power spike")
    st.info("ℹ️ Pump-02: Efficiency drop 12%")

# Bottom section
st.markdown("---")
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("💡 Top Recommendations")
    recommendations = [
        {"action": "Shift Compressor-02 to off-peak", "savings": "$45/day"},
        {"action": "Adjust HVAC-03 setpoint to 23°C", "savings": "$28/day"},
        {"action": "Schedule Lighting-Zone-B shutdown", "savings": "$15/day"},
    ]
    for rec in recommendations:
        st.markdown(f"• **{rec['action']}** — {rec['savings']}")

with col_b2:
    st.subheader("📊 Energy Mix")
    mix_data = pd.DataFrame({
        "Source": ["Grid", "Solar", "Battery"],
        "Percentage": [65, 25, 10],
    })
    st.bar_chart(mix_data.set_index("Source"))
