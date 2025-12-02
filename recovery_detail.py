# app.py — AUTO-LOADS EXCEL + PASSWORD PROTECTION
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Cartrack Recovery Dashboard", layout="wide")
st.title("Recovery Rate Dashboard")

# ——— PASSWORD PROTECTION ———
PASSWORD = "cartrack123"        # ← CHANGE THIS TO WHATEVER YOU WANT

if st.session_state.get("authenticated") != True:
    st.markdown("### Enter password to access the dashboard")
    pwd = st.text_input("Password", type="password")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Incorrect password")
    st.stop()

# ——— USER IS AUTHENTICATED ———
st.success("Access granted")
st.markdown("**Automatically loading your latest data**")

# === AUTO LOAD EXCEL FILE (same as before) ===
@st.cache_data(show_spinner="Loading data...")
def load_data():
    paths_to_try = [
        Path("Recovery Data Detail.xlsx"),
        Path(r"C:/Users/Anro.Vanesch/Desktop/Cartrack/Josh/Detailed Recovery Report/CT ZA Recovery Stats/Recovery Data Detail.xlsx"),
    ]
    for p in paths_to_try:
        if p.exists():
            df = pd.read_excel(p, sheet_name="Detail")
            st.success(f"Loaded **{len(df):,}** incidents from `{p.name}`")
            return df
    
    st.error("Recovery Data Detail.xlsx not found in usual locations!")
    st.info("Make sure the file is in the same folder as this app or in your usual path.")
    st.stop()

df = load_data()

# Ensure Recovered01 exists
if "Recovered01" not in df.columns:
    df["Recovered01"] = (df["recovered"].astype(str).str.strip().str.lower() == "yes").astype(int)

# === ALL YOUR FILTERS (unchanged) ===
with st.sidebar:
    st.header("Filters")
    st.subheader("Incident Date")
    year = st.multiselect("Year", options=sorted(df["Year"].dropna().unique()))
    month = st.multiselect("Month", options=sorted(df["Month"].dropna().unique()))
    day = st.multiselect("Day", options=sorted(df["Day"].dropna().unique()))
    hour = st.multiselect("Hour", options=sorted(df["Hour"].dropna().unique()))
    
    st.subheader("Contract Date")
    con_year = st.multiselect("Contract Year", options=sorted(df["ConYear"].dropna().unique()))
    con_month = st.multiselect("Contract Month", options=sorted(df["ConMonth"].dropna().unique()))
    
    st.subheader("Vehicle & Product")
    manufacturer = st.multiselect("Manufacturer", options=sorted(df["manufacturer"].dropna().unique()))
    model = st.multiselect("Model", options=sorted(df["model"].dropna().unique()))
    colour = st.multiselect("Colour", options=sorted(df["vehicle_colour"].dropna().unique()))
    vehicle_year = st.multiselect("Vehicle Year", options=sorted(df["vehicle_year"].dropna().unique()))
    package = st.multiselect("Product Package", options=sorted(df["product_package"].dropna().unique()))
    hardware = st.multiselect("Hardware Type", options=sorted(df["primary_hardware_type"].dropna().unique()))
    
    st.subheader("Incident Details")
    inc_type = st.multiselect("Incident Type", options=sorted(df["incident_type"].dropna().unique()))
    user_type = st.multiselect("User Type", options=sorted(df["user_type"].dropna().unique()))
    terminal = st.multiselect("Terminal Event", options=sorted(df["terminal_event_type_description"].dropna().unique()))
    tag = st.multiselect("Tag/Asset Track", options=sorted(df["tag_or_asset_track"].dropna().unique()))
    
    st.subheader("Exclusions & Flags")
    warranty = st.multiselect("Warranty Base", options=sorted(df["warranty_base"].dropna().unique()))
    device_ex = st.multiselect("Device Exclusion", options=sorted(df["device_exclusion"].dropna().unique()))
    bike_ex = st.multiselect("Bike Exclusion", options=sorted(df["bike_exclusion"].dropna().unique()))
    fraud = st.multiselect("Fraud", options=sorted(df["fraud"].dropna().unique()))
    exclude = st.multiselect("Exclude Flag", options=sorted(df["Exclude"].dropna().unique()))
    
    st.subheader("People & Sales")
    rep = st.multiselect("Business Source User", options=sorted(df["business_source_username"].dropna().unique()))
    client = st.text_input("Client Name (any part)")
    user = st.text_input("User Name (any part)")
    reg = st.text_input("Registration (any part)")

    calculate = st.button("CALCULATE RECOVERY RATE", type="primary", use_container_width=True)

# === CALCULATION (exactly the same) ===
if calculate:
    data = df.copy()
    filter_map = [
        (year, "Year"), (month, "Month"), (day, "Day"), (hour, "Hour"),
        (con_year, "ConYear"), (con_month, "ConMonth"),
        (inc_type, "incident_type"), (user_type, "user_type"),
        (terminal, "terminal_event_type_description"), (tag, "tag_or_asset_track"),
        (warranty, "warranty_base"), (device_ex, "device_exclusion"),
        (bike_ex, "bike_exclusion"), (fraud, "fraud"), (exclude, "Exclude"),
        (manufacturer, "manufacturer"), (model, "model"),
        (colour, "vehicle_colour"), (vehicle_year, "vehicle_year"),
        (package, "product_package"), (hardware, "primary_hardware_type"),
        (rep, "business_source_username"),
    ]
    for values, col in filter_map:
        if values:
            data = data[data[col].isin(values)]

    if client: data = data[data["client_name"].astype(str).str.contains(client, case=False, na=False)]
    if user:   data = data[data["user_name"].astype(str).str.contains(user, case=False, na=False)]
    if reg:    data = data[data["primary_registration"].astype(str).str.contains(reg, case=False, na=False)]

    total = len(data)
    recovered = int(data["Recovered01"].sum())
    rate = recovered / total if total > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", f"{total:,}")
    c2.metric("Recovered", f"{recovered:,}")
    c3.metric("Recovery Rate", f"{rate:.1%}")

    st.success(f"### Recovery Rate: **{rate:.1%}** → {recovered:,} of {total:,} incidents")
    st.balloons()
else:
    st.info("Select filters → click **CALCULATE RECOVERY RATE**")