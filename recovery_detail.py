# app.py — FINAL: ALL FILTERS + SMART SEARCH + FOCUS MODE + PASSWORD
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
            st.success(f"Loaded **{len(df):,}** incidents from `{p.name}`")
            return df
    st.error("File not found!")
    st.stop()

df = load_data()

if "Recovered01" not in df.columns:
    df["Recovered01"] = (df["recovered"].astype(str).str.strip().str.lower() == "yes").astype(int)

# === SIDEBAR - ALL FILTERS BACK + SMART SEARCH ===
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

    st.subheader("Focus Mode")
    focus_mode = st.checkbox("Show % of selected group vs rest of period")

    st.subheader("Vehicle & Product - SMART SEARCH")
    # Manufacturer
    manu_search = st.text_input("Search Manufacturer (e.g. toyota, nissan)", "")
    manu_opts = sorted(df["manufacturer"].dropna().unique())
    manu_filtered = [x for x in manu_opts if manu_search.lower() in x.lower()] if manu_search else manu_opts
    manufacturer = st.multiselect("Manufacturer", options=manu_filtered, default=manu_filtered if manu_search else [])

    # Model
    model_search = st.text_input("Search Model (e.g. hilux, ranger, polo)", "")
    model_opts = sorted(df["model"].dropna().unique())
    model_filtered = [x for x in model_opts if model_search.lower() in x.lower()] if model_search else model_opts
    model = st.multiselect("Model", options=model_filtered, default=model_filtered if model_search else [])

    # Product Package
    pkg_search = st.text_input("Search Product Package (e.g. earlybird, beame)", "")
    pkg_opts = sorted(df["product_package"].dropna().unique())
    pkg_filtered = [x for x in pkg_opts if pkg_search.lower() in x.lower()] if pkg_search else pkg_opts
    product_package = st.multiselect("Product Package", options=pkg_filtered, default=pkg_filtered if pkg_search else [])

    colour = st.multiselect("Colour", options=sorted(df["vehicle_colour"].dropna().unique()))
    vehicle_year = st.multiselect("Vehicle Year", options=sorted(df["vehicle_year"].dropna().unique()))
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

# === CALCULATION ===
if calculate:
    data = df.copy()

    # All standard filters
    filter_map = [
        (year, "Year"), (month, "Month"), (day, "Day"), (hour, "Hour"),
        (con_year, "ConYear"), (con_month, "ConMonth"),
        (inc_type, "incident_type"), (user_type, "user_type"),
        (terminal, "terminal_event_type_description"), (tag, "tag_or_asset_track"),
        (warranty, "warranty_base"), (device_ex, "device_exclusion"),
        (bike_ex, "bike_exclusion"), (fraud, "fraud"), (exclude, "Exclude"),
        (manufacturer, "manufacturer"), (model, "model"),
        (colour, "vehicle_colour"), (vehicle_year, "vehicle_year"),
        (product_package, "product_package"), (hardware, "primary_hardware_type"),
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

    # === FOCUS MODE ===
    if focus_mode and (model or manufacturer or product_package or model_search or manu_search or pkg_search):
        period_df = df.copy()
        if year: period_df = period_df[period_df["Year"].isin(year)]
        if month: period_df = period_df[period_df["Month"].isin(month)]
        period_total = len(period_df)

        group_name = "Selected Group"
        if model_search: group_name = f"Models containing '{model_search.upper()}'"
        elif manu_search: group_name = f"{manu_search.upper()} vehicles"
        elif pkg_search: group_name = f"Package containing '{pkg_search.upper()}'"

        group_pct = total / period_total * 100 if period_total > 0 else 0
        overall_rate = period_df["Recovered01"].mean()

        st.subheader(f"Focus: {group_name}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Incidents in Group", f"{total:,}", f"{group_pct:.1f}% of period")
        col2.metric("Recovery Rate in Group", f"{rate:.1%}", delta=f"{rate - overall_rate:.1%}")
        col3.metric("Overall Rate (same period)", f"{overall_rate:.1%}")

    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Incidents", f"{total:,}")
        c2.metric("Recovered", f"{recovered:,}")
        c3.metric("Recovery Rate", f"{rate:.1%}")

    st.success(f"### Final Rate: **{rate:.1%}** ({recovered:,}/{total:,})")
    st.balloons()
else:
    st.info("Select filters → type in search boxes → click **CALCULATE**")