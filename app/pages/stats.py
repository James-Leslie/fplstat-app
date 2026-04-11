import pandas as pd
import streamlit as st

from data import fetch_stats, fetch_teams

# ── Filters ──────────────────────────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])

# Team: populated from DB so it reflects the current season's clubs.
with col1:
    team_filter = st.selectbox("Team", ["All"] + fetch_teams(), index=0)

# Position: fixed FPL categories — GK, DEF, MID, FWD never change.
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

# Gameweeks: controls which window is passed to the player_stats() RPC.
# All other filters are applied client-side on the returned DataFrame.
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

df: pd.DataFrame = fetch_stats(last_n)

if df.empty:
    st.info("No data available.")
    st.stop()

# Client-side filtering — team, position, price, and minutes are not pushed
# to the DB because the full dataset is small enough to filter in-process.
if team_filter != "All":
    df = df.loc[df["team"] == team_filter]

if pos_filter != "All":
    df = df.loc[df["pos"] == pos_filter]

df = df.loc[df["price"] <= max_price]
df = df.loc[df["mp"] >= min_minutes]

# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("## Player stats")
st.caption("Click on columns for sorting")

# Select and rename columns for display (internal snake_case → readable headers).
display = df.filter(
    items=[
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
).rename(
    columns={
        "pos": "Pos",
        "team": "Team",
        "player": "Player",
        "price": "£",
        "st": "ST",
        "mp": "MP",
        "pts": "Pts",
        "p90": "P90",
        "xp90": "xP90",
        "gs90": "GS90",
        "a90": "A90",
        "gi90": "GI90",
        "xg90": "xG90",
        "xa90": "xA90",
        "xgi90": "xGI90",
        "cs": "CS",
        "xgc": "xGC",
        "xgc90": "xGC90",
        "tsb": "TSB%",
    }
)

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
