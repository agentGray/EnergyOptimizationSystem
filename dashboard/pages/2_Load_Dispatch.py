"""Load Dispatch & Optimization page — Light Theme."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Load Dispatch", page_icon="⚖️", layout="wide")

st.title("⚖️ Load Dispatch & Optimization")
st.caption("Intelligent load management, peak shaving, and demand response.")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Demand", "2,450 kW", "-120 kW", delta_color="inverse")
col2.metric("Demand Limit", "3,000 kW")
col3.metric("Peak Today", "2,890 kW")
col4.metric("Load Factor", "78%", "+3%")

st.markdown("---")

# Load Profile Chart
st.subheader("📊 24-Hour Load Profile")

hours = list(range(24))
actual_load = [
    1800, 1750, 1700, 1680, 1720, 1850, 2100, 2400,
    2600, 2700, 2750, 2800, 2850, 2900, 2950, 2890,
    2800, 2700, 2500, 2300, 2100, 1950, 1850, 1800,
]
optimized_load = [int(x * 0.88) for x in actual_load]

load_df = pd.DataFrame({
    "Hour": hours,
    "Actual (kW)": actual_load,
    "Optimized (kW)": optimized_load,
    "Demand Limit (kW)": [3000] * 24,
})
st.line_chart(load_df.set_index("Hour"), use_container_width=True)

col_legend1, col_legend2, col_legend3 = st.columns(3)
col_legend1.caption("🔵 Blue = Actual consumption")
col_legend2.caption("🟢 Green = Optimized target")
col_legend3.caption("🔴 Red = Demand limit (contract max)")

# Optimization strategies
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💡 Load Shifting")
    st.caption("Move flexible loads to off-peak hours (22:00-06:00)")
    shifting_data = pd.DataFrame({
        "Asset": ["Compressor-02", "Pump-04", "Chiller-02"],
        "Current (kW)": [85, 45, 120],
        "Shift To": ["22:00-06:00", "23:00-05:00", "21:00-07:00"],
        "Daily Savings": ["$45", "$22", "$58"],
    })
    st.dataframe(shifting_data, use_container_width=True, hide_index=True)
    st.info(f"💰 **Total Load Shifting Savings: $125/day**")

with col_right:
    st.subheader("⚡ Peak Shaving")
    st.caption("Reduce non-critical loads during peak hours (14:00-20:00)")
    peak_data = pd.DataFrame({
        "Asset": ["HVAC-01", "HVAC-02", "Lighting-A"],
        "Reduce By": ["15%", "10%", "30%"],
        "Savings (kW)": [22, 18, 12],
        "Comfort Impact": ["Low", "Low", "None"],
    })
    st.dataframe(peak_data, use_container_width=True, hide_index=True)
    st.info(f"⚡ **Total Peak Reduction: 52 kW**")

# Demand Response
st.markdown("---")
st.subheader("📡 Demand Response Status")

col_dr1, col_dr2 = st.columns([2, 1])

with col_dr1:
    st.success("🟢 **Program Active:** Peak Demand Reduction")
    st.markdown("""
    | Parameter | Value |
    |-----------|-------|
    | Target Reduction | 200 kW |
    | Achieved | 185 kW |
    | Achievement | 92.5% |
    | Event Window | 14:00 - 20:00 |
    """)
    st.progress(92)

with col_dr2:
    st.subheader("💰 Savings Summary")
    st.metric("Daily Savings", "$312.50")
    st.metric("Monthly Projected", "$9,375")
    st.metric("CO₂ Reduced", "156 kg/day")
