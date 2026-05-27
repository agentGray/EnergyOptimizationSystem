"""Main Streamlit dashboard application — Light Theme."""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Energy Optimization Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for light theme styling
st.markdown("""
<style>
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1a1a1a;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚡ Energy Platform")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- 🏠 **Live Dashboard**
- 🔍 Anomaly Detection
- ⚖️ Load Dispatch
- 🏭 Asset Health
- 🌱 ESG & ISO 50001
""")
st.sidebar.markdown("---")
st.sidebar.success("Status: 🟢 Connected")
st.sidebar.caption("Last Update: Real-time")
st.sidebar.caption(f"Time: {datetime.now().strftime('%H:%M:%S')}")

# Title
st.title("🏭 Industrial AI Energy Optimization")
st.caption("Real-Time Factory Energy Dashboard")
st.markdown("---")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Power", value="2,450 kW", delta="-120 kW", delta_color="inverse")

with col2:
    st.metric(label="Energy Today", value="18,200 kWh", delta="-890 kWh", delta_color="inverse")

with col3:
    st.metric(label="Active Anomalies", value="3", delta="+1", delta_color="inverse")

with col4:
    st.metric(label="Savings Today", value="$245.30", delta="+$32.10")

st.markdown("---")

# Main content area
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("⚡ Real-Time Energy Consumption")

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
    st.line_chart(chart_df, use_container_width=True)

with col_right:
    st.subheader("🏭 Asset Status")
    status_df = pd.DataFrame({
        "Status": ["Running", "Idle", "Maintenance", "Offline"],
        "Count": [12, 3, 2, 1],
    })
    st.bar_chart(status_df.set_index("Status"), use_container_width=True)

    st.subheader("🔔 Recent Alerts")
    st.warning("⚠️ HVAC-03: Overcooling detected (Zone B at 16°C)")
    st.error("🔴 Compressor-01: Power spike (+67% above baseline)")
    st.info("ℹ️ Pump-02: Efficiency drop 12% — seal inspection recommended")

# Bottom section
st.markdown("---")
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("💡 Top Recommendations")
    recommendations = [
        {"action": "Shift Compressor-02 to off-peak (22:00-06:00)", "savings": "$45/day", "confidence": "82%"},
        {"action": "Adjust HVAC-03 setpoint from 18°C to 23°C", "savings": "$28/day", "confidence": "90%"},
        {"action": "Schedule Lighting-Zone-B shutdown after 22:00", "savings": "$15/day", "confidence": "95%"},
    ]
    for i, rec in enumerate(recommendations, 1):
        st.markdown(
            f"**{i}.** {rec['action']}  \n"
            f"   💰 Savings: **{rec['savings']}** | Confidence: {rec['confidence']}"
        )

with col_b2:
    st.subheader("📊 Energy Mix")
    mix_data = pd.DataFrame({
        "Source": ["Grid (65%)", "Solar (25%)", "Battery (10%)"],
        "Percentage": [65, 25, 10],
    })
    st.bar_chart(mix_data.set_index("Source"), use_container_width=True)

# Footer
st.markdown("---")
st.caption("Industrial AI Energy Optimization Platform v1.0 | Powered by FastAPI + Streamlit")
