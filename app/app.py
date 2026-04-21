# Entrypoint for the fplstat multi-page app.
# Each page lives in app/pages/; add new st.Page entries here to register them.

from datetime import datetime, timezone

import streamlit as st

from data import fetch_last_updated

st.set_page_config(page_title="fplstat", layout="wide")

pg = st.navigation(
    [
        st.Page("pages/stats.py", title="Player Stats", icon=":material/bar_chart:"),
        st.Page(
            "pages/fdr_matrix.py", title="FDR Matrix", icon=":material/calendar_month:"
        ),
    ],
    position="top",
)


def _time_ago(dt: datetime) -> str:
    """Format a datetime as a human-readable relative string."""
    delta = datetime.now(timezone.utc) - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


last_updated = fetch_last_updated()
if last_updated:
    st.caption(f"Data last updated {_time_ago(last_updated)}")

pg.run()
