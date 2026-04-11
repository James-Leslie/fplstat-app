import pandas as pd
import streamlit as st

from data import fetch_fixtures, fetch_gameweek_info, fetch_team_id_map

# ── FDR colour scheme ───────────────────────────────────────────────────────

FDR_COLOURS: dict[int, tuple[str, str | None]] = {
    1: ("darkgreen", None),
    2: ("#09fc7b", None),
    3: ("#e7e7e8", None),
    4: ("#ff1651", "white"),
    5: ("#80072d", "white"),
}

# ── Sidebar ─────────────────────────────────────────────────────────────────

gw_info = fetch_gameweek_info()
gw_min, gw_max, gw_next = gw_info["min_gw"], gw_info["max_gw"], gw_info["next_gw"]

start_gw, end_gw = st.sidebar.slider(
    "Gameweek range",
    min_value=gw_min,
    max_value=gw_max,
    value=(gw_next, min(gw_next + 7, gw_max)),
)

# ── Data ────────────────────────────────────────────────────────────────────

fixtures = fetch_fixtures()
team_map = fetch_team_id_map()

# Filter to selected GW range.
fx = fixtures[
    (fixtures["gameweek_id"] >= start_gw) & (fixtures["gameweek_id"] <= end_gw)
].copy()

if fx.empty:
    st.info("No fixtures in the selected gameweek range.")
    st.stop()

# Split each fixture into home and away rows so every team appears once per
# fixture with its own opponent, venue, and FDR value.
home = fx[["gameweek_id", "team_h_id", "team_a_id", "team_h_difficulty"]].rename(
    columns={
        "team_h_id": "team_id",
        "team_a_id": "opponent_id",
        "team_h_difficulty": "fdr",
    }
)
home["venue"] = "H"

away = fx[["gameweek_id", "team_a_id", "team_h_id", "team_a_difficulty"]].rename(
    columns={
        "team_a_id": "team_id",
        "team_h_id": "opponent_id",
        "team_a_difficulty": "fdr",
    }
)
away["venue"] = "A"

long = pd.concat([home, away], ignore_index=True)
long["team"] = long["team_id"].map(team_map)
long["opponent"] = long["opponent_id"].map(team_map)

# Per-fixture display fragment: "ARS (H)"
long["fragment"] = long["opponent"] + " (" + long["venue"] + ")"

# ── Pivot ───────────────────────────────────────────────────────────────────

# For double GWs a team has two rows in the same GW.  Aggregate them:
#   display text → fragments joined directly + " {max_fdr}"
#   fdr value    → max (used for cell colouring)
grouped = long.groupby(["team", "gameweek_id"]).agg(
    display=("fragment", "".join),
    fdr=("fdr", "max"),
)
grouped["display"] = grouped["display"] + " " + grouped["fdr"].astype(str)
grouped = grouped.reset_index()

# Build display matrix (text) and FDR matrix (numeric).
display_matrix = grouped.pivot(
    index="team", columns="gameweek_id", values="display"
).fillna("")

fdr_matrix = grouped.pivot(index="team", columns="gameweek_id", values="fdr").fillna(0)

# Ensure all GWs in the selected range appear as columns.
all_gws = list(range(start_gw, end_gw + 1))
for gw in all_gws:
    if gw not in display_matrix.columns:
        display_matrix[gw] = ""
        fdr_matrix[gw] = 0
display_matrix = display_matrix[all_gws]
fdr_matrix = fdr_matrix[all_gws]

# Sort rows by ascending average FDR (easiest schedules at top).
avg_fdr = fdr_matrix.replace(0, pd.NA).mean(axis=1)
sort_order = avg_fdr.sort_values().index
display_matrix = display_matrix.loc[sort_order]
fdr_matrix = fdr_matrix.loc[sort_order]

# Clean column names to plain integers.
display_matrix.columns = [int(c) for c in display_matrix.columns]
fdr_matrix.columns = [int(c) for c in fdr_matrix.columns]
display_matrix.index.name = "Team"

# ── Styling ─────────────────────────────────────────────────────────────────


def _apply_fdr_colours(row: pd.Series) -> list[str]:
    """Return CSS strings for each cell based on the parallel FDR matrix."""
    team = row.name
    styles: list[str] = []
    for col in row.index:
        fdr_val = int(fdr_matrix.loc[team, col])  # type: ignore[arg-type]
        if fdr_val in FDR_COLOURS:
            bg, fg = FDR_COLOURS[fdr_val]
            css = f"background-color: {bg};"
            if fg:
                css += f" color: {fg};"
            styles.append(css)
        else:
            styles.append("")
    return styles


styled = display_matrix.style.apply(_apply_fdr_colours, axis=1)

# ── Render ──────────────────────────────────────────────────────────────────

st.markdown("## Fixtures")
st.caption("Sorted by average fixture difficulty — easiest schedules at the top")
st.dataframe(styled, use_container_width=True, height=750)
