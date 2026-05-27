"""ESG & ISO 50001 Reporting page — Light Theme."""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ESG & ISO 50001", page_icon="🌱", layout="wide")

st.title("🌱 ESG & ISO 50001 Reporting")
st.caption("Sustainability metrics, carbon tracking, and compliance reporting.")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("CO₂ Emissions", "4,250 kg", "-320 kg", delta_color="inverse")
col2.metric("Energy Intensity", "0.42 kWh/unit", "-0.03", delta_color="inverse")
col3.metric("Renewable %", "25%", "+3%")
col4.metric("ISO 50001 Score", "78.5%", "+2.1%")

st.markdown("---")

# Carbon Emissions Trend
st.subheader("📈 Carbon Emissions Trend (Monthly)")
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
emissions = [5200, 4900, 4800, 4600, 4500, 4400,
             4350, 4300, 4250, 4200, 4150, 4100]

emissions_df = pd.DataFrame({
    "Month": months,
    "Actual (kg CO₂)": emissions,
    "Target (kg CO₂)": [5000] * 12,
})
st.line_chart(emissions_df.set_index("Month"), use_container_width=True)
st.caption("🟢 Green line = Actual emissions (declining) | 🟡 Yellow line = Target")

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    # Energy Sources
    st.subheader("⚡ Energy Sources")
    sources_df = pd.DataFrame({
        "Source": ["Grid Electricity", "Solar PV", "Battery Storage", "Natural Gas"],
        "Percentage": [60, 25, 10, 5],
        "CO₂ Factor (kg/kWh)": [0.4, 0.0, 0.0, 0.2],
    })
    st.dataframe(sources_df, use_container_width=True, hide_index=True)
    st.bar_chart(sources_df.set_index("Source")["Percentage"], use_container_width=True)

with col_right:
    # ISO 50001 Compliance
    st.subheader("🎯 ISO 50001 Compliance")
    compliance_items = pd.DataFrame({
        "Requirement": [
            "Energy Policy", "Energy Review", "Energy Baseline",
            "EnPIs Defined", "Action Plans", "Monitoring System",
            "Internal Audit", "Management Review",
        ],
        "Status": [
            "✅ Complete", "✅ Complete", "✅ Complete",
            "✅ Complete", "⚠️ In Progress", "✅ Complete",
            "⚠️ Scheduled", "❌ Pending",
        ],
        "Score": [100, 95, 90, 85, 70, 95, 60, 40],
    })
    st.dataframe(compliance_items, use_container_width=True, hide_index=True)

# Year-over-Year
st.markdown("---")
st.subheader("📊 Year-over-Year Improvements")
col_y1, col_y2, col_y3 = st.columns(3)

with col_y1:
    st.metric("Energy Reduction", "12.3%", "vs. last year")
    st.caption("Target: 15%")
    st.progress(82)

with col_y2:
    st.metric("CO₂ Reduction", "18.5%", "vs. last year")
    st.caption("Target: 20%")
    st.progress(92)

with col_y3:
    st.metric("Cost Savings", "$142,500", "vs. last year")
    st.caption("Target: $150K")
    st.progress(95)

# Report Generation
st.markdown("---")
st.subheader("📄 Report Generation")
col_r1, col_r2 = st.columns(2)

with col_r1:
    report_type = st.selectbox(
        "Report Type",
        ["Monthly ESG Summary", "ISO 50001 Audit Report",
         "Carbon Footprint Report", "Energy Performance Report"],
    )
    report_period = st.selectbox(
        "Period", ["Last Month", "Last Quarter", "Last Year", "Custom"]
    )

with col_r2:
    st.info(
        f"📊 **{report_type}** for {report_period}\n\n"
        "Includes: Energy consumption, carbon emissions, "
        "compliance scores, and improvement recommendations."
    )
    if st.button("📥 Generate Report", type="primary", use_container_width=True):
        st.success("✅ Report generated successfully! Download ready.")
