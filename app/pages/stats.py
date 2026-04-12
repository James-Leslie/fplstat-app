import math

import pandas as pd
import streamlit as st

from data import (
    fetch_fixtures,
    fetch_gameweek_info,
    fetch_stats,
    fetch_team_id_map,
    fetch_teams,
)
from style import FDR_COLOURS

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
df = df.reset_index(drop=True)

df["shirt"] = df["team_code"].apply(
    lambda c: (
        f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{c}-66.webp"
    )
)

# ── Player detail modal ──────────────────────────────────────────────────────


def _build_fdr_strip(team_short_name: str, num_gws: int = 8) -> list[dict]:
    """Build upcoming fixture difficulty data for a team."""
    team_id_map = fetch_team_id_map()
    name_to_id = {v: k for k, v in team_id_map.items()}
    team_id = name_to_id.get(team_short_name)
    if team_id is None:
        return []

    gw_info = fetch_gameweek_info()
    next_gw = gw_info["next_gw"]
    max_gw = gw_info["max_gw"]
    end_gw = min(next_gw + num_gws - 1, max_gw)

    fixtures = fetch_fixtures()
    fx = fixtures[
        (~fixtures["finished"])
        & (fixtures["gameweek_id"] >= next_gw)
        & (fixtures["gameweek_id"] <= end_gw)
    ].copy()

    # Split into home/away rows for this team.
    home = fx.loc[
        fx["team_h_id"] == team_id,
        ["gameweek_id", "team_a_id", "team_h_difficulty"],
    ].rename(columns={"team_a_id": "opponent_id", "team_h_difficulty": "fdr"})
    home["venue"] = "H"

    away = fx.loc[
        fx["team_a_id"] == team_id,
        ["gameweek_id", "team_h_id", "team_a_difficulty"],
    ].rename(columns={"team_h_id": "opponent_id", "team_a_difficulty": "fdr"})
    away["venue"] = "A"

    team_fx = pd.concat([home, away], ignore_index=True)
    team_fx["opponent"] = team_fx["opponent_id"].map(team_id_map)
    team_fx["fragment"] = team_fx["opponent"] + " (" + team_fx["venue"] + ")"

    grouped = team_fx.groupby("gameweek_id").agg(
        opponents=("fragment", " ".join),
        fdr=("fdr", "max"),
    ).reset_index()

    gw_data = grouped.set_index("gameweek_id")
    result = []
    for gw in range(next_gw, end_gw + 1):
        if gw in gw_data.index:
            row = gw_data.loc[gw]
            result.append({"gw": gw, "opponents": row["opponents"], "fdr": int(row["fdr"])})
        else:
            result.append({"gw": gw, "opponents": "", "fdr": 0})
    return result


@st.dialog("Player Details", width="large")
def _show_player_detail(player_row: pd.Series) -> None:
    """Modal showing detailed player stats and upcoming FDR strip."""
    # ── Header ──
    col_shirt, col_info = st.columns([1, 4])
    with col_shirt:
        shirt_url = (
            f"https://fantasy.premierleague.com/dist/img/shirts/standard/"
            f"shirt_{int(player_row['team_code'])}-66.webp"
        )
        st.image(shirt_url, width=80)
    with col_info:
        st.subheader(player_row["player"])
        st.caption(
            f"{player_row['pos']}  ·  {player_row['team']}  ·  £{player_row['price']:.1f}"
        )

    # ── Stats ──
    st.markdown("##### Key Stats")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Points", int(player_row["pts"]))
    s2.metric("P90", f"{player_row['p90']:.1f}")
    s3.metric("xP90", f"{player_row['xp90']:.1f}")
    s4.metric("TSB%", f"{player_row['tsb']:.1f}%")

    s5, s6, s7, s8 = st.columns(4)
    s5.metric("Starts", int(player_row["st"]))
    s6.metric("Minutes", int(player_row["mp"]))
    s7.metric("MP%", f"{player_row['mp_pct']:.1f}%")
    s8.metric("Clean Sheets", int(player_row["cs"]))

    s9, s10, s11, s12 = st.columns(4)
    s9.metric("GS90", f"{player_row['gs90']:.2f}")
    s10.metric("A90", f"{player_row['a90']:.2f}")
    s11.metric("xG90", f"{player_row['xg90']:.2f}")
    s12.metric("xA90", f"{player_row['xa90']:.2f}")

    # ── FDR Strip ──
    st.markdown("##### Upcoming Fixtures")
    strip = _build_fdr_strip(player_row["team"])
    if not strip:
        st.caption("No upcoming fixture data available.")
        return

    html_parts = []
    for entry in strip:
        gw = entry["gw"]
        opponents = entry["opponents"]
        fdr = entry["fdr"]
        if fdr in FDR_COLOURS:
            bg, fg = FDR_COLOURS[fdr]
        else:
            bg, fg = "#e7e7e8", "#999"
            opponents = "-"
        html_parts.append(
            f'<div style="display:inline-block;text-align:center;margin:2px;">'
            f'<div style="font-size:0.7em;color:#666;">GW{gw}</div>'
            f'<div style="background:{bg};color:{fg};padding:6px 10px;'
            f'border-radius:6px;font-size:0.85em;font-weight:600;'
            f'min-width:70px;">{opponents}</div>'
            f"</div>"
        )
    st.html(
        '<div style="display:flex;flex-wrap:wrap;gap:4px;">'
        + "".join(html_parts)
        + "</div>"
    )


# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("## Player stats")
st.caption("Click a row to see player details · Click column headers to sort")

# Select and rename columns for display (internal snake_case → readable headers).
display = df.filter(
    items=[
        "shirt",
        "pos",
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
        "shirt": "Team",
        "pos": "Pos",
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

display.insert(0, "ℹ️", "ℹ️")

event = st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "ℹ️": st.column_config.TextColumn("ℹ️", width="small"),
        "Team": st.column_config.ImageColumn("Team", width="small"),
        "£": st.column_config.NumberColumn(format="%.1f"),
        "TSB%": st.column_config.NumberColumn(format="%.1f"),
        "P90": st.column_config.NumberColumn(format="%.1f"),
        "MP%": st.column_config.NumberColumn(format="%.1f"),
    },
    on_select="rerun",
    selection_mode="single-row",
    key="player_stats_table",
)

if event.selection.rows:
    selected_idx = event.selection.rows[0]
    _show_player_detail(df.iloc[selected_idx])
