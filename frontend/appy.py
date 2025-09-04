import streamlit as st
from default_data import ensure_base_session_state

ensure_base_session_state(st)

pages = {
    "": [
        st.Page("Home.py", title="Kezdőoldal"),
    ],
    "Projektmenedzsment": [
        st.Page("pages/Projects.py", title="Projektek"),
        st.Page("pages/ProjektTipusok.py", title="Projekt Típusok"),
        st.Page("pages/ProfessionTypes.py", title="Szakmák"),
        st.Page("pages/IdojarasUtemezes.py", title="Időjárás Ütemezés"),
        st.Page("pages/Resources.py", title="Erőforrások"),
    ],
    "AI Asszisztensek": [
        st.Page("pages/AnyagarAjanlatkeresAI.py", title="Anyagár Ajánlatkérés"),
        st.Page("pages/SzerzodeskeszitesAI.py", title="Szerződéskészítés"),
    ],
}

pg = st.navigation(pages)
pg.run()
