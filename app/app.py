import os

import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="fplstat", layout="wide")


@st.cache_resource
def get_client():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


@st.cache_data(ttl=300)
def fetch_stats(last_n: int | None) -> pd.DataFrame:
    client = get_client()
    params = {"last_n": last_n} if last_n is not None else {}
    rows = client.rpc("player_stats", params).execute().data
    return pd.DataFrame(rows)


# ── Filters ──────────────────────────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])

with col1:
    team_filter = st.selectbox(
        "Team",
        ["All"]
        + sorted(
            [
                "ARS",
                "AVL",
                "BOU",
                "BRE",
                "BHA",
                "CHE",
                "CRY",
                "EVE",
                "FUL",
                "IPS",
                "LEI",
                "LIV",
                "MCI",
                "MUN",
                "NEW",
                "NFO",
                "SOU",
                "TOT",
                "WHU",
                "WOL",
            ]
        ),
        index=0,
    )

with col2:
    pos_filter = st.selectbox("Position", ["All", "GK", "DEF", "MID", "FWD"], index=0)

with col3:
    max_price = st.number_input(
        "Max price (£)",
        min_value=3.0,
        max_value=16.0,
        value=16.0,
        step=0.1,
        format="%.1f",
    )

with col4:
    min_minutes = st.number_input(
        "Minutes played ≥", min_value=0, max_value=3800, value=90, step=45
    )

with col5:
    last_n_options = {
        "Full season": None,
        "Last 1 GW": 1,
        "Last 3 GWs": 3,
        "Last 5 GWs": 5,
        "Last 8 GWs": 8,
    }
    last_n_label = st.selectbox("Gameweeks", list(last_n_options.keys()), index=0)
    last_n = last_n_options[last_n_label]

# ── Data ─────────────────────────────────────────────────────────────────────

df = fetch_stats(last_n)

if df.empty:
    st.info("No data available.")
    st.stop()

if team_filter != "All":
    df = df[df["team"] == team_filter]

if pos_filter != "All":
    df = df[df["pos"] == pos_filter]

df = df[df["price"] <= max_price]
df = df[df["mp"] >= min_minutes]

# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("## Player stats")
st.caption("Click on columns for sorting")

display = df[
    [
        "pos",
        "team",
        "player",
        "price",
        "st",
        "mp",
        "pts",
        "p90",
        "xp90",
        "gs90",
        "a90",
        "gi90",
        "xg90",
        "xa90",
        "xgi90",
        "cs",
        "xgc",
        "xgc90",
        "tsb",
    ]
].copy()

display.columns = [
    "Pos",
    "Team",
    "Player",
    "£",
    "ST",
    "MP",
    "Pts",
    "P90",
    "xP90",
    "GS90",
    "A90",
    "GI90",
    "xG90",
    "xA90",
    "xGI90",
    "CS",
    "xGC",
    "xGC90",
    "TSB%",
]

st.dataframe(
    display,
    width="stretch",
    hide_index=True,
    column_config={
        "£": st.column_config.NumberColumn(format="%.1f"),
        "TSB%": st.column_config.NumberColumn(format="%.1f"),
        "P90": st.column_config.NumberColumn(format="%.1f"),
    },
)
