# Entrypoint for the fplstat multi-page app.
# Each page lives in app/pages/; add new st.Page entries here to register them.

import streamlit as st

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
pg.run()
