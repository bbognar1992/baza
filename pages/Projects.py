import streamlit as st
from default_data import ensure_base_session_state
from navbar import render_navbar, set_current_page

st.set_page_config(page_title="Projects – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Set current page for navbar highlighting
set_current_page("Projektek")

st.title("📁 Projektek")

st.write("Itt tudod kezelni az aktuális projekteket.")

# Show creation form and list
with st.expander("➕ Új projekt", expanded=False):
    with st.form("create_project"):
        st.subheader("Új projekt létrehozása")
        name = st.text_input("Projekt neve")
        start = st.date_input("Kezdés dátuma")
        end = st.date_input("Befejezés dátuma")
        locations_input = st.text_input("Helyszínek (vesszővel elválasztva)")
        resource_names = [r.get("Név", "") for r in st.session_state.resources if r.get("Név")]
        selected_members = st.multiselect("Projekt tagok", options=resource_names, default=[])
        submitted = st.form_submit_button("Projekt hozzáadása")
        if submitted and name:
            locations_list = [
                part.strip() for part in (locations_input or "").split(",") if part.strip()
            ] or ["Budapest"]
            st.session_state.projects.append({
                "name": name,
                "start": str(start),
                "end": str(end),
                "status": "Folyamatban",
                "members": selected_members,
                "locations": locations_list,
                "progress": 35
            })
            st.success(f"Projekt létrehozva: {name}")
            st.rerun()

st.write("### Projektek")

if st.session_state.projects:
    future_projects = [p for p in st.session_state.projects if p.get("status") in ("Tervezés alatt",)]
    active_projects = [p for p in st.session_state.projects if p.get("status") in ("Folyamatban", "Késésben")]
    closed_projects = [p for p in st.session_state.projects if p.get("status") in ("Lezárt",)]

    tab_future, tab_active, tab_closed = st.tabs([
        f"Jövőbeli ({len(future_projects)})",
        f"Folyamatban lévő ({len(active_projects)})",
        f"Lezárt ({len(closed_projects)})",
    ])

    def render_list(projects_subset, subset_key_prefix=""):
        if not projects_subset:
            st.info("Nincs megjeleníthető projekt.")
            return
        header = st.columns([3, 2, 2, 2, 2, 2])
        header[0].markdown("**Név**")
        header[1].markdown("**Típus**")
        header[2].markdown("**Kezdés**")
        header[3].markdown("**Befejezés**")
        header[4].markdown("**Státusz**")
        header[5].markdown("**Művelet**")
        for idx, proj in enumerate(projects_subset):
            cols = st.columns([3, 2, 2, 2, 2, 2])
            cols[0].markdown(f"**{proj['name']}**")
            cols[1].write(proj.get("type", "-"))
            cols[2].write(proj["start"])
            cols[3].write(proj["end"])
            cols[4].write(proj["status"])
            # Find original index to open details
            try:
                original_idx = st.session_state.projects.index(proj)
            except ValueError:
                original_idx = None
            if cols[5].button("Megnyitás", key=f"open_{subset_key_prefix}{idx}"):
                if original_idx is not None:
                    st.session_state.selected_project_index = original_idx
                    st.switch_page("pages/ProjectDetails.py")

    with tab_future:
        render_list(future_projects, "future_")
    with tab_active:
        render_list(active_projects, "active_")
    with tab_closed:
        render_list(closed_projects, "closed_")
else:
    st.info("Még nincs projekt. Hozz létre egyet fentebb.")
