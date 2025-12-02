# app.py — PRIVATE & SHAREABLE VERSION (no Excel in repo)
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cartrack Recovery Dashboard", layout="wide")
st.title("Recovery Rate Dashboard")
st.markdown("**Private & secure** – upload the latest Excel file to continue")

# Simple password (change this to whatever you want)
PASSWORD = "cartrack2025"   # ← change this!

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Wrong password")
    st.stop()

# ——— USER IS NOW AUTHENTICATED ———
st.success("Authenticated – upload your latest file")

uploaded = st.file_uploader(
    "Upload **Recovery Data Detail.xlsx** (Detail sheet)",
    type=["xlsx"],
    help="Only you and trusted people have this file"
)

if uploaded:
    try:
        df = pd.read_excel(uploaded, sheet_name="Detail")
        st.success(f"Loaded {len(df):,} incidents")

        # Ensure Recovered01 exists
        if "Recovered01" not in df.columns:
            df["Recovered01"] = (df["recovered"].astype(str).str.strip().str.lower() == "yes").astype(int)

        # ——— ALL FILTERS (same as before) ———
        with st.sidebar:
            st.header("Filters")
            year = st.multiselect("Year", options=sorted(df["Year"].dropna().unique()))
            month = st.multiselect("Month", options=sorted(df["Month"].dropna().unique()))
            manufacturer = st.multiselect("Manufacturer", options=sorted(df["manufacturer"].dropna().unique()))
            model = st.multiselect("Model", options=sorted(df["model"].dropna().unique()))
            # ... (add more filters if you want – but these are the main ones people use)

            client = st.text_input("Client Name (any part)")
            user = st.text_input("User Name (any part)")
            reg = st.text_input("Registration (any part)")

            calculate = st.button("CALCULATE RECOVERY RATE", type="primary", use_container_width=True)

        if calculate:
            data = df.copy()
            if year: data = data[data["Year"].isin(year)]
            if month: data = data[data["Month"].isin(month)]
            if manufacturer: data = data[data["manufacturer"].isin(manufacturer)]
            if model: data = data[data["model"].isin(model)]
            if client: data = data[data["client_name"].astype(str).str.contains(client, case=False, na=False)]
            if user: data = data[data["user_name"].astype(str).str.contains(user, case=False, na=False)]
            if reg: data = data[data["primary_registration"].astype(str).str.contains(reg, case=False, na=False)]

            total = len(data)
            recovered = int(data["Recovered01"].sum())
            rate = recovered / total if total else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Incidents", f"{total:,}")
            c2.metric("Recovered", f"{recovered:,}")
            c3.metric("Recovery Rate", f"{rate:.1%}")
            st.balloons()

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Upload the Excel file → enter password → filter → calculate")