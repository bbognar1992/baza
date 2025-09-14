import streamlit as st
from datetime import datetime
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation, handle_user_not_logged_in
from components.project_details_tabs import basic_info, team, phases, locations, schedule, material_costs

st.set_page_config(page_title="Project Details – ÉpítAI", layout="wide")

ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("📁 Projekt Részletek")


# Check if a project is selected
if "selected_project_index" not in st.session_state or st.session_state.selected_project_index is None:
    st.warning("Nincs kiválasztott projekt. Kérjük, válassz ki egy projektet a fő Projektek oldalról.")
    st.info("💡 Tipp: Menj vissza a Projektek oldalra és kattints egy projekt nevére a részletek megtekintéséhez.")
    
    if st.button("🔙 Vissza a Projektek oldalra"):
        st.switch_page("pages/projects.py")
else:
    # Get the selected project
    project_index = st.session_state.selected_project_index
    if project_index < len(st.session_state.projects):
        project = st.session_state.projects[project_index]
        
        # Header with project info
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.subheader(f"📋 {project.get('name', 'Névtelen projekt')}")
            st.caption(f"Státusz: {project.get('status', 'Ismeretlen')}")
        
        with col2:
            if st.button("✏️ Szerkesztés", key="edit_project"):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col3:
            if st.button("👁️ Ügyfél nézet", key="client_view", help="Ügyfél nézet megnyitása - korlátozott hozzáférés"):
                # Set the client view to show this specific project
                st.session_state.client_selected_project_index = project_index
                st.switch_page("pages/client_view.py")
        
        with col4:
            if st.button("🔙 Vissza", key="back_to_projects"):
                st.session_state.selected_project_index = None
                st.switch_page("pages/projects.py")
        
        # Check if in edit mode
        if st.session_state.get("edit_mode", False):
            st.markdown("---")
            st.subheader("✏️ Projekt szerkesztése")
            
            with st.form("edit_project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input(
                        "Projekt neve",
                        value=project.get("name", ""),
                        key="edit_name"
                    )
                    
                    new_start = st.date_input(
                        "Kezdés dátuma",
                        value=datetime.strptime(project.get("start", "2025-01-01"), "%Y-%m-%d").date(),
                        key="edit_start"
                    )
                    
                    new_end = st.date_input(
                        "Befejezés dátuma",
                        value=datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date(),
                        key="edit_end"
                    )
                
                with col2:
                    new_status = st.selectbox(
                        "Státusz",
                        ["Tervezés alatt", "Folyamatban", "Késésben", "Lezárt"],
                        index=["Tervezés alatt", "Folyamatban", "Késésben", "Lezárt"].index(project.get("status", "Folyamatban")),
                        key="edit_status"
                    )
                    
                    new_type = st.text_input(
                        "Típus",
                        value=project.get("type", ""),
                        key="edit_type"
                    )
                    
                    locations_input = st.text_input(
                        "Helyszínek (vesszővel elválasztva)",
                        value=", ".join(project.get("locations", [])),
                        key="edit_locations"
                    )
                
                # Project members
                st.subheader("👥 Projekt tagok")
                resource_names = [r.get("Név", "") for r in st.session_state.resources if r.get("Név")]
                current_members = project.get("members", [])
                new_members = st.multiselect(
                    "Projekt tagok",
                    options=resource_names,
                    default=current_members,
                    key="edit_members"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Mentés", type="primary"):
                        if new_name:
                            # Update the project
                            locations_list = [
                                part.strip() for part in (locations_input or "").split(",") if part.strip()
                            ] or ["Budapest"]
                            
                            st.session_state.projects[project_index] = {
                                "name": new_name,
                                "start": str(new_start),
                                "end": str(new_end),
                                "status": new_status,
                                "type": new_type,
                                "members": new_members,
                                "locations": locations_list,
                                "progress": project.get("progress", 0),
                                "phases_checked": project.get("phases_checked", [])
                            }
                            st.success("Projekt sikeresen frissítve!")
                            st.session_state.edit_mode = False
                            st.rerun()
                        else:
                            st.error("A projekt nevének megadása kötelező!")
                
                with col2:
                    if st.form_submit_button("❌ Mégse"):
                        st.session_state.edit_mode = False
                        st.rerun()
        else:
            # Display mode
            st.markdown("---")
            
            # Main info cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Státusz",
                    value=project.get("status", "Ismeretlen")
                )
            
            with col2:
                st.metric(
                    label="Kezdés",
                    value=project.get("start", "-")
                )
            
            with col3:
                st.metric(
                    label="Befejezés",
                    value=project.get("end", "-")
                )
            
            with col4:
                st.metric(
                    label="Típus",
                    value=project.get("type", "-")
                )
            
            # Progress section
            st.write("### 📊 Haladás")
            progress = int(project.get("progress", 0))
            st.progress(progress / 100)
            st.caption(f"{progress}%")
            
            # Detailed information tabs
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📋 Alapadatok",
                "👥 Csapat",
                "📅 Fázisok",
                "🗺️ Helyszínek",
                "📊 Ütemterv",
                "🧱 Anyagköltségek"
            ])
            
            with tab1:
                basic_info.render_basic_info_tab(project)
            
            with tab2:
                team.render_team_tab(project, project_index)
            
            with tab3:
                phases.render_phases_tab(project, project_index)
            
            with tab4:
                locations.render_locations_tab(project)
            
            with tab5:
                schedule.render_schedule_tab(project)
            
            with tab6:
                material_costs.render_material_costs_tab(project)
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️ Szerkesztés", key="edit_button"):
                    st.session_state.edit_mode = True
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Törlés", key="delete_button"):
                    st.session_state.show_delete_confirmation = True
                    st.rerun()
            
            with col3:
                if st.button("👥 Tag hozzáadása", key="add_member"):
                    st.session_state.show_add_member = True
                    st.rerun()
            
            # Delete confirmation
            if st.session_state.get("show_delete_confirmation", False):
                st.warning("⚠️ Biztosan törölni szeretnéd ezt a projektet?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Igen, törlés", key="confirm_delete"):
                        del st.session_state.projects[project_index]
                        st.session_state.selected_project_index = None
                        st.session_state.show_delete_confirmation = False
                        st.success("Projekt sikeresen törölve!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Mégse", key="cancel_delete"):
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
            
            # Add member dialog
            if st.session_state.get("show_add_member", False):
                st.subheader("👥 Tag hozzáadása a projekthez")
                
                # Get available resources (not already in project)
                current_members = project.get("members", [])
                available_resources = [r for r in st.session_state.resources if r.get("Név") not in current_members]
                
                if available_resources:
                    resource_names = [r.get("Név", "Névtelen") for r in available_resources]
                    selected_resource_name = st.selectbox("Válassz erőforrást:", resource_names)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Hozzáadás", key="confirm_add_member"):
                            # Add the resource to project members
                            if "members" not in project:
                                project["members"] = []
                            project["members"].append(selected_resource_name)
                            
                            st.success(f"Tag hozzáadva a projekthez: {selected_resource_name}")
                            st.session_state.show_add_member = False
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Mégse", key="cancel_add_member"):
                            st.session_state.show_add_member = False
                            st.rerun()
                else:
                    st.info("Nincs elérhető erőforrás, akit hozzáadhatnál a projekthez.")
                    if st.button("❌ Bezárás", key="close_add_member"):
                        st.session_state.show_add_member = False
                        st.rerun()
    else:
        st.error("A kiválasztott projekt nem található.")
        st.session_state.selected_project_index = None
        st.rerun()
