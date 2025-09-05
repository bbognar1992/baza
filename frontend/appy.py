import streamlit as st
from default_data import ensure_base_session_state

ensure_base_session_state(st)

pages = {
    "": [
        st.Page("Home.py", title="Kezdőoldal"),
    ],
    "Projektmenedzsment": [
        st.Page("pages/Projects.py", title="Projektek"),
        st.Page("pages/ClientView.py", title="Ügyfél Nézet"),
        st.Page("pages/utemezes.py", title="Ütemezés"),
        st.Page("pages/Resources.py", title="Erőforrások"),
        st.Page("pages/ResourceDetails.py", title="Erőforrás Részletek"),
    ],
    "AI Asszisztensek": [
        st.Page("pages/AnyagarAjanlatkeresAI.py", title="Anyagár Ajánlatkérés"),
        st.Page("pages/SzerzodeskeszitesAI.py", title="Szerződéskészítés"),
    ],
    "Beállítások": [
        st.Page("pages/ProfessionTypes.py", title="Szakmák"),
        st.Page("pages/ProjektTipusok.py", title="Projekt Típusok"),
    ],
}

pg = st.navigation(pages)
pg.run()
