"""Load Dispatch & Optimization page."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Load Dispatch", page_icon="⚖️", layout="wide")
st.title("⚖️ Load Dispatch & Optimization")
st.markdown("Intelligent load management, peak shaving, and demand response.")
st.markdown("---")

# Current demand overview
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Demand", "2,450 kW", "-120 kW")
col2.metric("Demand Limit", "3,000 kW", "")
col3.metric("Peak Today", "2,890 kW", "")
col4.metric("Load Factor", "78%", "+3%")

st.markdown("---")

# Load profile chart
st.subheader("📊 24-Hour Load Profile")
hours = list(range(24))
np.random.seed(42)
actual_load = [
    1800, 1750, 1700, 1680, 1720, 1850, 2100, 2400,
    2600, 2700, 2750, 2800, 2850, 2900, 2950, 2890,
    2800, 2700, 2500, 2300, 2100, 1950, 1850, 1800,
]
optimized_load = [x * 0.88 for x in actual_load]
baseline = [2200] * 24
demand_limit = [3000] * 24

load_df = pd.DataFrame({
    "Hour": hours,
    "Actual (kW)": actual_load,
    "Optimized (kW)": optimized_load,
    "Demand Limit (kW)": demand_limit,
})
st.line_chart(load_df.set_index("Hour"))

# Optimization recommendations
st.markdown("---")
st.subheader("💡 Active Optimization Strategies")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Load Shifting")
    shifting_data = pd.DataFrame({
        "Asset": ["Compressor-02", "Pump-04", "Chiller-02"],
        "Current (kW)": [85, 45, 120],
        "Shift To": ["22:00-06:00", "23:00-05:00", "21:00-07:00"],
        "Savings": ["$45/day", "$22/day", "$58/day"],
    })
    st.dataframe(shifting_data, use_container_width=True, hide_index=True)

with col_right:
    st.markdown("#### Peak Shaving")
    peak_data = pd.DataFrame({
        "Asset": ["HVAC-01", "HVAC-02", "Lighting-A"],
        "Reduce By": ["15%", "10%", "30%"],
        "Savings (kW)": [22, 18, 12],
        "Impact": ["Low", "Low", "None"],
    })
    st.dataframe(peak_data, use_container_width=True, hide_index=True)

# Demand response
st.markdown("---")
st.subheader("⚡ Demand Response Status")
col_dr1, col_dr2 = st.columns(2)

with col_dr1:
    st.markdown("""
    **Current Program:** Peak Demand Reduction  
    **Status:** 🟢 Active  
    **Target Reduction:** 200 kW  
    **Achieved:** 185 kW (92.5%)  
    **Event Window:** 14:00 - 20:00  
    """)

with col_dr2:
    st.markdown("#### Savings Summary")
    st.metric("Daily Savings", "$312.50")
    st.metric("Monthly Projected", "$9,375")
    st.metric("CO₂ Reduced", "156 kg/day")
