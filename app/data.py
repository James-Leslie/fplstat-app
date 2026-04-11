import os

import pandas as pd
import streamlit as st
from supabase import create_client


@st.cache_resource
def get_client():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


# player_stats() aggregates per-player stats for the season or a recent GW window.
# Cached for 5 minutes to avoid hammering the DB on every Streamlit interaction.
@st.cache_data(ttl=300)
def fetch_stats(last_n: int | None) -> pd.DataFrame:
    client = get_client()
    params = {"last_n": last_n} if last_n is not None else {}
    rows = client.rpc("player_stats", params).execute().data  # type: ignore[union-attr]
    return pd.DataFrame(rows)  # type: ignore[arg-type]


# Team short codes (e.g. ARS, LIV) sourced from public.teams so the list
# stays accurate across promotions and relegations without touching this file.
@st.cache_data(ttl=300)
def fetch_teams() -> list[str]:
    client = get_client()
    rows = client.from_("teams").select("short_name").execute().data  # type: ignore[union-attr]
    return sorted(r["short_name"] for r in rows)  # type: ignore[index, return-value]


@st.cache_data(ttl=300)
def fetch_team_id_map() -> dict[int, str]:
    """Map team id → short_name (e.g. {1: 'ARS', 2: 'AVL', …})."""
    client = get_client()
    rows = client.from_("teams").select("id, short_name").execute().data  # type: ignore[union-attr]
    return {r["id"]: r["short_name"] for r in rows}  # type: ignore[index]


@st.cache_data(ttl=300)
def fetch_fixtures() -> pd.DataFrame:
    """All fixtures with the columns needed for the FDR matrix."""
    client = get_client()
    rows = (
        client.from_("fixtures")
        .select(
            "gameweek_id, team_h_id, team_a_id, team_h_difficulty, team_a_difficulty"
        )
        .execute()
        .data
    )
    return pd.DataFrame(rows)  # type: ignore[arg-type]


@st.cache_data(ttl=300)
def fetch_gameweek_info() -> dict:
    """Return min/max GW ids and the next GW id (for slider defaults)."""
    client = get_client()
    rows = client.from_("gameweeks").select("id, is_next").execute().data  # type: ignore[union-attr]
    ids = [r["id"] for r in rows]  # type: ignore[index]
    next_gw = next((r["id"] for r in rows if r["is_next"]), max(ids))  # type: ignore[index]
    return {"min_gw": min(ids), "max_gw": max(ids), "next_gw": next_gw}
