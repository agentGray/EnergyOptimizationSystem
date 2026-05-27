"""Anomaly Detection page — Light Theme."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Anomaly Detection", page_icon="🔍", layout="wide")

st.title("🔍 Anomaly Detection")
st.caption("AI-powered detection of energy waste patterns and equipment issues.")
st.markdown("---")

# Filters
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
with col_f2:
    type_filter = st.selectbox(
        "Anomaly Type",
        ["All", "Phantom Load", "HVAC Overcooling", "Air Leak",
         "Voltage Imbalance", "Power Spike", "Motor Overload"],
    )
with col_f3:
    time_range = st.selectbox("Time Range", ["Last 24 Hours", "Last 7 Days", "Last 30 Days"])

# KPI Summary
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Anomalies", "7", "+2", delta_color="inverse")
col2.metric("Critical", "1", "+1", delta_color="inverse")
col3.metric("Energy Waste", "342 kWh/day", "+45 kWh")
col4.metric("Cost Impact", "$41.04/day", "+$5.40")

st.markdown("---")

# Anomaly Timeline
st.subheader("📈 Anomaly Detection Timeline")
np.random.seed(123)
hours = pd.date_range(start=datetime.now() - timedelta(hours=48), end=datetime.now(), freq="1h")
anomaly_scores = np.random.beta(2, 8, len(hours))
anomaly_scores[20:23] = 0.85 + np.random.random(3) * 0.1
anomaly_scores[40:42] = 0.9 + np.random.random(2) * 0.05

timeline_df = pd.DataFrame({
    "Time": hours,
    "Anomaly Score": anomaly_scores,
    "Threshold (0.85)": [0.85] * len(hours),
})
st.line_chart(timeline_df.set_index("Time"), use_container_width=True)
st.caption("🔴 Points above the threshold line indicate detected anomalies.")

# Active Anomalies Table
st.markdown("---")
st.subheader("🚨 Active Anomalies")

anomalies_data = pd.DataFrame({
    "ID": [1, 2, 3, 4, 5],
    "Asset": ["HVAC-03", "Compressor-01", "Pump-02", "Motor-05", "Lighting-B"],
    "Type": ["HVAC Overcooling", "Power Spike", "Efficiency Drop", "Phantom Load", "Unusual Pattern"],
    "Severity": ["🟠 High", "🔴 Critical", "🟡 Medium", "🟡 Medium", "🟢 Low"],
    "Confidence": ["92%", "96%", "85%", "88%", "78%"],
    "Energy Waste": ["45 kWh/d", "120 kWh/d", "28 kWh/d", "35 kWh/d", "12 kWh/d"],
    "Cost Impact": ["$5.40/d", "$14.40/d", "$3.36/d", "$4.20/d", "$1.44/d"],
    "Detected": ["2h ago", "30min ago", "5h ago", "1d ago", "3h ago"],
})

st.dataframe(anomalies_data, use_container_width=True, hide_index=True)

# Anomaly Detail
st.markdown("---")
st.subheader("📋 Anomaly Details")

with st.expander("🔴 Compressor-01: Power Spike (Critical)", expanded=True):
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.markdown("""
        **Root Cause:** Sudden load change, possible mechanical fault

        | Metric | Value |
        |--------|-------|
        | Baseline Power | 85 kW |
        | Current Power | 142 kW |
        | Deviation | +67% |
        | Duration | 30 minutes |
        | Confidence | 96% |
        | Estimated Waste | 120 kWh/day |

        **Recommended Action:** Reduce load by 20%, schedule maintenance inspection.
        """)
    with col_d2:
        st.button("✅ Approve Fix", key="approve_comp", type="primary", use_container_width=True)
        st.button("❌ Dismiss", key="dismiss_comp", use_container_width=True)

with st.expander("🟠 HVAC-03: Overcooling (High)"):
    st.markdown("""
    **Root Cause:** Setpoint too low or faulty thermostat

    - Zone B temperature: 16°C (threshold: 18°C)
    - Recommended setpoint: 22°C
    - Estimated savings: $5.40/day

    **Recommended Action:** Adjust setpoint to 22°C.
    """)
