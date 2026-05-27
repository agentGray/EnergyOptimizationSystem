"""Asset Health & Monitoring page — Light Theme."""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Asset Health", page_icon="🏭", layout="wide")

st.title("🏭 Asset Health & Monitoring")
st.caption("Real-time asset status, health scores, and predictive maintenance.")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Assets", "18")
col2.metric("Avg Health Score", "87.3%", "+1.2%")
col3.metric("Maintenance Due", "2")
col4.metric("Faults", "1", "+1", delta_color="inverse")

st.markdown("---")

# Asset Inventory Table
st.subheader("📋 Asset Inventory")
assets_data = pd.DataFrame({
    "Asset": [
        "Chiller-01", "Chiller-02", "HVAC-01", "HVAC-02", "HVAC-03",
        "Compressor-01", "Compressor-02", "Pump-01", "Pump-02",
        "Furnace-01", "Motor-01", "Motor-05", "Lighting-A", "Lighting-B",
    ],
    "Type": [
        "Chiller", "Chiller", "HVAC", "HVAC", "HVAC",
        "Compressor", "Compressor", "Pump", "Pump",
        "Furnace", "Motor", "Motor", "Lighting", "Lighting",
    ],
    "Status": [
        "🟢 Running", "🟢 Running", "🟢 Running", "🟢 Running", "🟢 Running",
        "🔴 Fault", "🟢 Running", "🟢 Running", "🟢 Running",
        "🟢 Running", "🟢 Running", "🟡 Idle", "🟢 Running", "🟢 Running",
    ],
    "Power (kW)": [150, 145, 85, 78, 82, 0, 90, 45, 42, 200, 55, 0, 35, 32],
    "Health %": [92, 88, 95, 91, 72, 45, 87, 94, 79, 85, 90, 96, 98, 97],
    "Efficiency": [
        "94%", "91%", "96%", "93%", "78%",
        "N/A", "89%", "95%", "82%",
        "87%", "92%", "N/A", "99%", "98%",
    ],
    "Last Maintenance": [
        "15 days", "30 days", "7 days", "22 days", "45 days",
        "60 days", "12 days", "5 days", "38 days",
        "20 days", "10 days", "8 days", "90 days", "85 days",
    ],
})

st.dataframe(assets_data, use_container_width=True, hide_index=True)

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    # Health Distribution
    st.subheader("📊 Health Score Distribution")
    health_scores = assets_data["Health %"].values
    health_df = pd.DataFrame({
        "Range": ["90-100%", "80-89%", "70-79%", "60-69%", "Below 60%"],
        "Assets": [
            sum(1 for h in health_scores if h >= 90),
            sum(1 for h in health_scores if 80 <= h < 90),
            sum(1 for h in health_scores if 70 <= h < 80),
            sum(1 for h in health_scores if 60 <= h < 70),
            sum(1 for h in health_scores if h < 60),
        ],
    })
    st.bar_chart(health_df.set_index("Range"), use_container_width=True)

with col_right:
    # Maintenance Schedule
    st.subheader("🔧 Maintenance Schedule")
    maintenance_data = pd.DataFrame({
        "Asset": ["Compressor-01", "HVAC-03", "Pump-02"],
        "Issue": ["Bearing wear detected", "Filter replacement", "Seal inspection"],
        "Priority": ["🔴 Urgent", "🟠 High", "🟡 Medium"],
        "Due": ["Immediate", "3 days", "7 days"],
    })
    st.dataframe(maintenance_data, use_container_width=True, hide_index=True)

    st.warning("⚠️ **Compressor-01** requires immediate attention — Health at 45%, "
               "60 days since last maintenance.")

# Asset Detail
st.markdown("---")
st.subheader("🔍 Asset Detail View")
selected_asset = st.selectbox("Select Asset", assets_data["Asset"].tolist())

if selected_asset:
    asset_row = assets_data[assets_data["Asset"] == selected_asset].iloc[0]
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("Health Score", f"{asset_row['Health %']}%")
    col_d2.metric("Current Power", f"{asset_row['Power (kW)']} kW")
    col_d3.metric("Efficiency", asset_row["Efficiency"])
    col_d4.metric("Last Maintenance", asset_row["Last Maintenance"])
