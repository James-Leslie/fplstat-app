import math

import pandas as pd
import streamlit as st

from data import fetch_stats, fetch_teams

# ── Filters ──────────────────────────────────────────────────────────────────

_all = fetch_stats(None)
_price_min = float(_all["price"].min()) if not _all.empty else 3.0
_price_max = float(_all["price"].max()) if not _all.empty else 16.0

col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])

# Gameweeks: controls which window is passed to the player_stats() RPC.
# All other filters are applied client-side on the returned DataFrame.
with col1:
    last_n_options = {
        "Full season": None,
        "Last 1 GW": 1,
        "Last 3 GWs": 3,
        "Last 5 GWs": 5,
        "Last 8 GWs": 8,
    }
    last_n_label = st.selectbox("Gameweeks", list(last_n_options.keys()), index=0)
    last_n = last_n_options[last_n_label]
    include_current = st.toggle("Include current GW", value=True)

# Team: populated from DB so it reflects the current season's clubs.
with col2:
    team_filter = st.selectbox("Team", ["All"] + fetch_teams(), index=0)

# Position: fixed FPL categories — GK, DEF, MID, FWD never change.
with col3:
    pos_filter = st.selectbox("Position", ["All", "GK", "DEF", "MID", "FWD"], index=0)

with col4:
    _price_steps = list(
        reversed(
            [
                round(p * 0.5, 1)
                for p in range(int(_price_min * 2), math.ceil(_price_max * 2) + 1)
            ]
        )
    )
    max_price = st.selectbox(
        "Max price (£)",
        options=_price_steps,
        index=0,
        format_func=lambda p: f"£{p:.1f}",
    )

with col5:
    min_mp_pct = st.number_input(
        "Minutes Played (%) ≥", min_value=0, max_value=100, value=50, step=5
    )

# ── Data ─────────────────────────────────────────────────────────────────────

df: pd.DataFrame = fetch_stats(last_n, include_current)

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
df = df.loc[df["mp_pct"] >= min_mp_pct]

# Build shirt image URL from team code.
df["shirt"] = df["team_code"].apply(
    lambda c: (
        f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{c}-66.webp"
    )
)

# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("## Player stats")
st.caption("Click on columns for sorting")

# Select and rename columns for display (internal snake_case → readable headers).
display = df.filter(
    items=[
        "shirt",
        "pos",
        "team",
        "player",
        "price",
        "st",
        "mp",
        "mp_pct",
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
        "shirt": " ",
        "pos": "Pos",
        "team": "Team",
        "player": "Player",
        "price": "£",
        "st": "ST",
        "mp": "MP",
        "mp_pct": "MP%",
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
        " ": st.column_config.ImageColumn(" ", width="small"),
        "£": st.column_config.NumberColumn(format="%.1f"),
        "TSB%": st.column_config.NumberColumn(format="%.1f"),
        "P90": st.column_config.NumberColumn(format="%.1f"),
        "MP%": st.column_config.NumberColumn(format="%.1f"),
    },
)
