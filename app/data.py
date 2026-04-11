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
