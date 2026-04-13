import math

import altair as alt
import pandas as pd
import streamlit as st

from data import (
    fetch_fixtures,
    fetch_gameweek_info,
    fetch_player_history,
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

# Build shirt image URL from team code.
df["shirt"] = df["team_code"].apply(
    lambda c: (
        f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{c}-66.webp"
    )
)

# Build PP90 breakdown list for the BarChartColumn.
# Order: Goals / Assists / Defensive / Bonus / Appearance
_breakdown_cols = [
    "goals_pp90",
    "assists_pp90",
    "defensive_pp90",
    "bonus_pp90",
    "appearance_pp90",
]
df["pp90_breakdown"] = df[_breakdown_cols].values.tolist()

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

    grouped = (
        team_fx.groupby("gameweek_id")
        .agg(
            opponents=("fragment", " ".join),
            fdr=("fdr", "max"),
        )
        .reset_index()
    )

    gw_data = grouped.set_index("gameweek_id")
    result = []
    for gw in range(next_gw, end_gw + 1):
        if gw in gw_data.index:
            row = gw_data.loc[gw]
            result.append(
                {"gw": gw, "opponents": row["opponents"], "fdr": int(row["fdr"])}
            )
        else:
            result.append({"gw": gw, "opponents": "", "fdr": 0})
    return result


_OUTCOME_STYLE: dict[str, str] = {
    "W": "background-color:#00a651;color:white",
    "D": "background-color:#e7e7e8;color:#333",
    "L": "background-color:#e00030;color:white",
}


def _outcome(was_home: bool, home_score: int, away_score: int) -> str:
    ps = home_score if was_home else away_score
    os_ = away_score if was_home else home_score
    if ps > os_:
        return "W"
    if ps < os_:
        return "L"
    return "D"


# Points multipliers by position
_GOAL_MULT = {"GK": 6, "DEF": 6, "MID": 5, "FWD": 4}
_CS_MULT = {"GK": 4, "DEF": 4, "MID": 1, "FWD": 0}


def _build_pp90_breakdown(hist: pd.DataFrame, pos: str) -> pd.DataFrame:
    """Compute points-per-90 broken down by scoring category from per-GW history."""
    total_minutes = hist["minutes"].sum()
    if total_minutes == 0:
        return pd.DataFrame()

    per90_div = total_minutes / 90

    # Goals
    goals_pts = (hist["goals_scored"] * _GOAL_MULT[pos]).sum()

    # Assists
    assists_pts = (hist["assists"] * 3).sum()

    # Defensive: clean sheet points + goals conceded deduction + DC
    cs_pts = (hist["cs"] * _CS_MULT[pos]).sum()
    gc_ded = 0
    if pos in ("GK", "DEF"):
        # Floor applied per gameweek, then summed
        gc_ded = (hist["goals_conceded"] // 2 * -1).sum()
    # DC awards 2pts when raw count meets the position threshold (10 DEF/GK, 12 MID/FWD)
    dc_threshold = 10 if pos in ("GK", "DEF") else 12
    dc_pts = (hist["defensive_contribution"] >= dc_threshold).sum() * 2
    defensive_pts = cs_pts + gc_ded + dc_pts

    # Bonus
    bonus_pts = hist["bonus"].sum()

    # Appearance: 2 if ≥60 min, 1 if ≥1 min
    appearance_pts = (
        hist["minutes"].apply(lambda m: 2 if m >= 60 else (1 if m >= 1 else 0)).sum()
    )

    # Saves (GK only)
    saves_pts = (hist["saves"] // 3).sum() if pos == "GK" else None

    # Deductions
    deductions_pts = (
        hist["yellow_cards"] * -1
        + hist["red_cards"] * -3
        + hist["own_goals"] * -2
        + hist["penalties_missed"] * -2
    ).sum()

    categories = []
    for label, value in [
        ("Goals", goals_pts),
        ("Assists", assists_pts),
        ("Defensive", defensive_pts),
        ("Bonus", bonus_pts),
        ("Appearance", appearance_pts),
        ("Saves", saves_pts),
        ("Deductions", deductions_pts),
    ]:
        if value is not None:
            categories.append({"category": label, "pp90": round(value / per90_div, 2)})

    return pd.DataFrame(categories)


# Category colours for the PP90 breakdown chart
_PP90_COLOURS = {
    "Goals": "#2ecc71",
    "Assists": "#3498db",
    "Defensive": "#9b59b6",
    "Bonus": "#f39c12",
    "Appearance": "#95a5a6",
    "Saves": "#1abc9c",
    "Deductions": "#e74c3c",
}
_PP90_ORDER = [
    "Goals",
    "Assists",
    "Defensive",
    "Bonus",
    "Appearance",
    "Saves",
    "Deductions",
]


@st.dialog("Player Details", width="large")
def _show_player_detail(player_row: pd.Series) -> None:
    """Modal showing player header, key stats, per-GW history table + charts, and FDR strip."""
    # ── Header ──
    col_shirt, col_info = st.columns([1, 5])
    with col_shirt:
        st.image(
            f"https://fantasy.premierleague.com/dist/img/shirts/standard/"
            f"shirt_{int(player_row['team_code'])}-66.webp",
            width=80,
        )
    with col_info:
        st.subheader(player_row["player"])
        st.caption(
            f"{player_row['pos']}  ·  {player_row['team']}  ·  £{player_row['price']:.1f}"
        )

    # ── Key stats ──
    s1, s2, s3, s4, s5, s6, s7 = st.columns(7)
    s1.metric("Pts", int(player_row["pts"]))
    s2.metric("P90", f"{player_row['p90']:.1f}")
    s3.metric("xP90", f"{player_row['xp90']:.1f}")
    s4.metric("TSB%", f"{player_row['tsb']:.1f}%")
    s5.metric("ST", int(player_row["st"]))
    s6.metric("MP%", f"{player_row['mp_pct']:.0f}%")
    s7.metric("CS", int(player_row["cs"]))

    # ── Upcoming fixtures ──
    strip = _build_fdr_strip(player_row["team"])
    if strip:
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
                f"border-radius:6px;font-size:0.85em;font-weight:600;"
                f'min-width:70px;">{opponents}</div>'
                f"</div>"
            )
        st.html(
            '<div style="display:flex;flex-wrap:wrap;gap:4px;">'
            + "".join(html_parts)
            + "</div>"
        )

    st.divider()

    # ── History ──
    hist = fetch_player_history(int(player_row["player_id"]))

    if hist.empty:
        st.caption("No match history available.")
    else:
        hist = hist.reset_index(drop=True)

        # ── PP90 Breakdown chart ──
        breakdown_df = _build_pp90_breakdown(hist, player_row["pos"])
        if not breakdown_df.empty:
            st.markdown("##### Points per 90 Breakdown")
            present_order = [
                c for c in _PP90_ORDER if c in breakdown_df["category"].values
            ]
            chart = (
                alt.Chart(breakdown_df)
                .mark_bar(cornerRadiusEnd=4)
                .encode(
                    x=alt.X("pp90:Q", title="Points per 90"),
                    y=alt.Y("category:N", title=None, sort=present_order),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(
                            domain=list(_PP90_COLOURS.keys()),
                            range=list(_PP90_COLOURS.values()),
                        ),
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("category:N", title="Category"),
                        alt.Tooltip("pp90:Q", title="PP90", format=".2f"),
                    ],
                )
            )
            st.altair_chart(chart, use_container_width=True)

        # Derived columns
        hist["Opponent"] = (
            hist["opponent"]
            + " ("
            + hist["was_home"].map({True: "H", False: "A"})
            + ")"
        )
        hist["Score"] = hist.apply(
            lambda r: (
                f"{int(r['home_score'])}-{int(r['away_score'])}"
                if pd.notna(r["home_score"])
                else "-"
            ),
            axis=1,
        )
        outcomes = hist.apply(
            lambda r: (
                _outcome(r["was_home"], int(r["home_score"]), int(r["away_score"]))
                if pd.notna(r["home_score"])
                else "?"
            ),
            axis=1,
        )

        display_hist = hist.rename(
            columns={
                "gameweek_id": "GW",
                "goals_scored": "GS",
                "assists": "A",
                "cs": "CS",
                "goals_conceded": "GC",
                "own_goals": "OG",
                "penalties_saved": "PS",
                "penalties_missed": "PM",
                "yellow_cards": "YC",
                "red_cards": "RC",
                "saves": "S",
                "bonus": "B",
                "bps": "BPS",
                "pts": "Pts",
                "starts": "ST",
                "minutes": "MP",
                "xg": "xG",
                "xa": "xA",
                "xgi": "xGI",
                "xgc": "xGC",
                "influence": "I",
                "creativity": "C",
                "threat": "T",
                "ict_index": "ICT",
                "xpts": "xPts",
            }
        )[
            [
                "GW",
                "Opponent",
                "Score",
                "Pts",
                "xPts",
                "ST",
                "MP",
                "GS",
                "A",
                "xG",
                "xA",
                "xGI",
                "CS",
                "GC",
                "xGC",
                "OG",
                "PS",
                "PM",
                "YC",
                "RC",
                "S",
                "B",
                "BPS",
                "I",
                "C",
                "T",
                "ICT",
            ]
        ]

        score_col_idx = list(display_hist.columns).index("Score")

        def _style_row(row: pd.Series) -> list[str]:
            styles = [""] * len(row)
            styles[score_col_idx] = _OUTCOME_STYLE.get(outcomes[row.name], "")
            return styles

        styled = display_hist.style.apply(_style_row, axis=1)
        st.dataframe(
            styled,
            hide_index=True,
            width="stretch",
            height=350,
            column_config={
                "xPts": st.column_config.NumberColumn(format="%.2f"),
                "xG": st.column_config.NumberColumn(format="%.2f"),
                "xA": st.column_config.NumberColumn(format="%.2f"),
                "xGI": st.column_config.NumberColumn(format="%.2f"),
                "xGC": st.column_config.NumberColumn(format="%.2f"),
                "I": st.column_config.NumberColumn(format="%.1f"),
                "C": st.column_config.NumberColumn(format="%.1f"),
                "T": st.column_config.NumberColumn(format="%.1f"),
                "ICT": st.column_config.NumberColumn(format="%.1f"),
            },
        )

        # ── Charts ──
        chart_df = hist[["gameweek_id", "goals_scored", "assists", "xgi"]].copy()
        chart_df = chart_df.sort_values("gameweek_id").reset_index(drop=True)
        chart_df["gi"] = chart_df["goals_scored"] + chart_df["assists"]
        chart_df["gi_delta"] = (chart_df["gi"] - chart_df["xgi"]).round(2)
        chart_df["cum_gi"] = chart_df["gi"].cumsum()
        chart_df["cum_xgi"] = chart_df["xgi"].cumsum()

        # GI delta bar chart
        delta_max = max(float(chart_df["gi_delta"].abs().max()), 0.5)
        bar = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("gameweek_id:O", title="GW"),
                y=alt.Y("gi_delta:Q", title="GI delta"),
                color=alt.Color(
                    "gi_delta:Q",
                    scale=alt.Scale(
                        scheme="redyellowgreen",
                        domain=[-delta_max, delta_max],
                    ),
                    legend=alt.Legend(title="GI delta"),
                ),
                tooltip=[
                    alt.Tooltip("gameweek_id:O", title="GW"),
                    alt.Tooltip("gi_delta:Q", title="GI delta", format=".2f"),
                ],
            )
            .properties(title="GI − xGI delta  (positive = overperforming)")
        )
        st.altair_chart(bar, use_container_width=True)

        # Cumulative GI vs xGI line chart
        cum_melted = chart_df.melt(
            id_vars=["gameweek_id"],
            value_vars=["cum_gi", "cum_xgi"],
            var_name="variable",
            value_name="value",
        )
        cum_melted["variable"] = cum_melted["variable"].map(
            {"cum_gi": "GI", "cum_xgi": "xGI"}
        )
        line = (
            alt.Chart(cum_melted)
            .mark_line(point=True)
            .encode(
                x=alt.X("gameweek_id:Q", title="GW"),
                y=alt.Y("value:Q", title="Cumulative"),
                color=alt.Color("variable:N", legend=alt.Legend(title="")),
                tooltip=[
                    alt.Tooltip("gameweek_id:Q", title="GW"),
                    alt.Tooltip("variable:N", title="Metric"),
                    alt.Tooltip("value:Q", title="Value", format=".2f"),
                ],
            )
            .properties(title="Cumulative GI and xGI")
        )
        st.altair_chart(line, use_container_width=True)


# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("## Player stats")
st.caption("Click a row to view player details · Click column headers to sort")

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
        "pp90_breakdown",
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
        "pp90_breakdown": "PP90",
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

event = st.dataframe(
    display,
    width="stretch",
    hide_index=True,
    column_config={
        "Team": st.column_config.ImageColumn("Team", width="small"),
        "Player": st.column_config.TextColumn("Player"),
        "£": st.column_config.NumberColumn(format="%.1f"),
        "TSB%": st.column_config.NumberColumn(format="%.1f"),
        "P90": st.column_config.NumberColumn(format="%.1f"),
        "PP90": st.column_config.BarChartColumn(
            "PP90",
            help="Points per 90 breakdown: Goals | Assists | Defensive (CS + GC ded + DC) | Bonus | Appearance",
            y_min=0,
        ),
        "MP%": st.column_config.NumberColumn(format="%.1f"),
    },
    on_select="rerun",
    selection_mode="single-row",
    key="player_stats_table",
)

if event.selection.rows:
    selected_idx = event.selection.rows[0]
    _show_player_detail(df.iloc[selected_idx])
