# app.py — FINAL VERSION: Focus Mode + Smart Search + Password
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Cartrack Recovery Dashboard", layout="wide")
st.title("Recovery Rate Dashboard")

# ——— PASSWORD (CHANGE THIS!) ———
PASSWORD = "cartrack123"

if st.session_state.get("authenticated") != True:
    st.markdown("### Enter password")
    pwd = st.text_input("Password", type="password")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Wrong password")
    st.stop()

st.success("Access granted")
st.markdown("**Auto-loading your latest data**")

# === AUTO LOAD DATA ===
@st.cache_data(show_spinner="Loading data...")
def load_data():
    paths = [
        Path("Recovery Data Detail.xlsx"),
        Path(r"C:/Users/Anro.Vanesch/Desktop/Cartrack/Josh/Detailed Recovery Report/CT ZA Recovery Stats/Recovery Data Detail.xlsx"),
    ]
    for p in paths:
        if p.exists():
            df = pd.read_excel(p, sheet_name="Detail")
            st.success(f"Loaded **{len(df):,}** incidents")
            return df
    st.error("File not found!")
    st.stop()

df = load_data()

# Ensure Recovered01
if "Recovered01" not in df.columns:
    df["Recovered01"] = (df["recovered"].astype(str).str.strip().str.lower() == "yes").astype(int)

# === SIDEBAR FILTERS ===
with st.sidebar:
    st.header("Filters")

    # Date filters
    year = st.multiselect("Year", options=sorted(df["Year"].dropna().unique()), default=[])
    month = st.multiselect("Month", options=sorted(df["Month"].dropna().unique()), default=[])

    st.subheader("Focus Mode (optional)")
    focus_mode = st.checkbox("Show % of selected group vs rest")

    # Smart search + dropdown for key columns
    st.subheader("Vehicle & Product")

    # Manufacturer
    manu_search = st.text_input("Search Manufacturer (e.g. toyota)", "")
    manu_options = sorted(df["manufacturer"].dropna().unique())
    manu_filtered = [x for x in manu_options if manu_search.lower() in x.lower()] if manu_search else manu_options
    manufacturer = st.multiselect("Manufacturer", options=manu_filtered, default=manu_filtered if manu_search else [])

    # Model
    model_search = st.text_input("Search Model (e.g. hilux, ranger, polo)", "")
    model_options = sorted(df["model"].dropna().unique())
    model_filtered = [x for x in model_options if model_search.lower() in x.lower()] if model_search else model_options
    model = st.multiselect("Model", options=model_filtered, default=model_filtered if model_search else [])

    # Product Package
    pkg_search = st.text_input("Search Product Package (e.g. earlybird, fleet)", "")
    pkg_options = sorted(df["product_package"].dropna().unique())
    pkg_filtered = [x for x in pkg_options if pkg_search.lower() in x.lower()] if pkg_search else pkg_options
    product_package = st.multiselect("Product Package", options=pkg_filtered, default=pkg_filtered if pkg_search else [])

    # Other filters
    hardware = st.multiselect("Hardware Type", options=sorted(df["primary_hardware_type"].dropna().unique()))
    rep = st.multiselect("Business Source User", options=sorted(df["business_source_username"].dropna().unique()))
    
    client = st.text_input("Client Name (any part)")
    user = st.text_input("User Name (any part)")
    reg = st.text_input("Registration (any part)")

    calculate = st.button("CALCULATE RECOVERY RATE", type="primary", use_container_width=True)

# === CALCULATION ===
if calculate:
    data = df.copy()

    # Apply filters
    if year: data = data[data["Year"].isin(year)]
    if month: data = data[data["Month"].isin(month)]
    if manufacturer: data = data[data["manufacturer"].isin(manufacturer)]
    if model: data = data[data["model"].isin(model)]
    if product_package: data = data[data["product_package"].isin(product_package)]
    if hardware: data = data[data["primary_hardware_type"].isin(hardware)]
    if rep: data = data[data["business_source_username"].isin(rep)]
    if client: data = data[data["client_name"].astype(str).str.contains(client, case=False, na=False)]
    if user: data = data[data["user_name"].astype(str).str.contains(user, case=False, na=False)]
    if reg: data = data[data["primary_registration"].astype(str).str.contains(reg, case=False, na=False)]

    total = len(data)
    recovered = int(data["Recovered01"].sum())
    rate = recovered / total if total > 0 else 0

    # Focus Mode: % of selected group vs total in time period
    if focus_mode and (model or manufacturer or product_package):
        group_name = "Selected Group"
        if model_search: group_name = f"Models containing '{model_search}'"
        elif manu_search: group_name = f"{manu_search.upper()}"
        elif pkg_search: group_name = f"Package containing '{pkg_search}'"

        filtered_total = len(df)
        if year: filtered_total = len(df[df["Year"].isin(year)])
        if month: filtered_total = len(df[df["Month"].isin(month)])

        group_pct = (total / filtered_total * 100) if filtered_total > 0 else 0

        st.subheader(f"Focus Mode: {group_name}")
        col1, col2 = st.columns(2)
        col1.metric("Incidents in Group", f"{total:,}", f"{group_pct:.1f}% of period")
        col2.metric("Recovery Rate in Group", f"{rate:.1%}")

        # Comparison to overall
        overall_rate = df["Recovered01"].mean()
        if year: overall_rate = df[df["Year"].isin(year)]["Recovered01"].mean()
        if month: overall_rate = df[df["Month"].isin(month)]["Recovered01"].mean()

        st.metric("Overall Recovery Rate (same period)", f"{overall_rate:.1%}", delta=f"{rate - overall_rate:.1%}")

    else:
        # Normal view
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Incidents", f"{total:,}")
        c2.metric("Recovered", f"{recovered:,}")
        c3.metric("Recovery Rate", f"{rate:.1%}")

    st.success(f"### Final Recovery Rate: **{rate:.1%}** ({recovered:,} / {total:,})")
    st.balloons()
else:
    st.info("Select filters → type in search boxes → click **CALCULATE**")