import streamlit as st
from default_data import ensure_base_session_state
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in
from database import get_db_session
from models import Project, ProjectType, Resource

st.set_page_config(page_title="Projects – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

def load_projects_from_db():
    """Load projects from database with relationships"""
    try:
        with get_db_session() as session:
            from sqlalchemy.orm import joinedload
            projects = session.query(Project).options(
                joinedload(Project.project_type),
                joinedload(Project.locations),
                joinedload(Project.members)
            ).all()
            return projects
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        return []

st.title("📁 Projektek")

st.write("Itt tudod kezelni az aktuális projekteket.")

# Load projects from database
projects = load_projects_from_db()

# Show creation form and list
with st.expander("➕ Új projekt", expanded=False):
    with st.form("create_project"):
        st.subheader("Új projekt létrehozása")
        name = st.text_input("Projekt neve")
        client_name = st.text_input("Ügyfél neve")
        start = st.date_input("Kezdés dátuma")
        end = st.date_input("Befejezés dátuma")
        budget = st.number_input("Költségvetés (HUF)", min_value=0, value=0)
        location = st.text_input("Helyszín")
        description = st.text_area("Leírás")
        
        # Get project types from database
        try:
            with get_db_session() as session:
                project_types = session.query(ProjectType).all()
                project_type_options = {pt.name: pt.project_type_id for pt in project_types}
                selected_type = st.selectbox("Projekt típus", options=list(project_type_options.keys()))
        except:
            project_type_options = {}
            selected_type = None
            
        # Get resources from database
        try:
            with get_db_session() as session:
                resources = session.query(Resource).all()
                resource_options = {f"{r.first_name} {r.last_name}": r.resource_id for r in resources}
                selected_members = st.multiselect("Projekt tagok", options=list(resource_options.keys()), default=[])
        except:
            resource_options = {}
            selected_members = []
            
        submitted = st.form_submit_button("Projekt hozzáadása")
        if submitted and name:
            try:
                with get_db_session() as session:
                    # Create new project
                    new_project = Project(
                        project_name=name,
                        client_name=client_name,
                        start_date=start,
                        end_date=end,
                        budget=budget if budget > 0 else None,
                        location=location,
                        description=description,
                        project_type_id=project_type_options.get(selected_type),
                        status="Tervezés alatt",
                        priority="Közepes",
                        progress_percent=0
                    )
                    session.add(new_project)
                    session.flush()  # Get the project_id
                    
                    # Add project members
                    for member_name in selected_members:
                        resource_id = resource_options.get(member_name)
                        if resource_id:
                            from models.project import ProjectMember
                            project_member = ProjectMember(
                                project_id=new_project.project_id,
                                resource_id=resource_id,
                                role_in_project="Tag"
                            )
                            session.add(project_member)
                    
                    session.commit()
                    st.success(f"Projekt létrehozva: {name}")
                    st.rerun()
            except Exception as e:
                st.error(f"Hiba a projekt létrehozásakor: {e}")

st.write("### Projektek")

if projects:
    future_projects = [p for p in projects if p.status in ("Tervezés alatt",)]
    active_projects = [p for p in projects if p.status in ("Folyamatban", "Késésben")]
    closed_projects = [p for p in projects if p.status in ("Lezárt",)]

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
            cols[0].markdown(f"**{proj.project_name}**")
            cols[1].write(proj.project_type.name if proj.project_type else "-")
            cols[2].write(proj.start_date.strftime("%Y-%m-%d") if proj.start_date else "-")
            cols[3].write(proj.end_date.strftime("%Y-%m-%d") if proj.end_date else "-")
            cols[4].write(proj.status)
            if cols[5].button("Megnyitás", key=f"open_{subset_key_prefix}{idx}"):
                st.session_state.selected_project_id = proj.project_id
                st.switch_page("pages/project_details.py")

    with tab_future:
        render_list(future_projects, "future_")
    with tab_active:
        render_list(active_projects, "active_")
    with tab_closed:
        render_list(closed_projects, "closed_")
else:
    st.info("Még nincs projekt. Hozz létre egyet fentebb.")
