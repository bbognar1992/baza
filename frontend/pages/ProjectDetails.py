import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
from default_data import get_default_phases, ensure_base_session_state

st.set_page_config(page_title="Project Details – ÉpítAI", layout="wide")

ensure_base_session_state(st)

st.title("📁 Projekt Részletek")

@st.cache_data(show_spinner=False)
def geocode_location(name: str):
    """Return (lat, lon) for a location name using OpenStreetMap Nominatim."""
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": name, "format": "json", "limit": 1},
            headers={"User-Agent": "epit-ai/1.0"},
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None

# Check if a project is selected
if "selected_project_index" not in st.session_state or st.session_state.selected_project_index is None:
    st.warning("Nincs kiválasztott projekt. Kérjük, válassz ki egy projektet a fő Projektek oldalról.")
    st.info("💡 Tipp: Menj vissza a Projektek oldalra és kattints egy projekt nevére a részletek megtekintéséhez.")
    
    if st.button("🔙 Vissza a Projektek oldalra"):
        st.switch_page("pages/Projects.py")
else:
    # Get the selected project
    project_index = st.session_state.selected_project_index
    if project_index < len(st.session_state.projects):
        project = st.session_state.projects[project_index]
        
        # Header with project info
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📋 {project.get('name', 'Névtelen projekt')}")
            st.caption(f"Státusz: {project.get('status', 'Ismeretlen')}")
        
        with col2:
            if st.button("✏️ Szerkesztés", key="edit_project"):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col3:
            if st.button("🔙 Vissza", key="back_to_projects"):
                st.session_state.selected_project_index = None
                st.switch_page("pages/Projects.py")
        
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
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Alapadatok",
                "👥 Csapat",
                "📅 Fázisok",
                "🗺️ Helyszínek",
                "📊 Ütemterv"
            ])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Projekt információk")
                    st.write(f"**Név:** {project.get('name', 'Nincs megadva')}")
                    st.write(f"**Státusz:** {project.get('status', 'Nincs megadva')}")
                    st.write(f"**Típus:** {project.get('type', 'Nincs megadva')}")
                    st.write(f"**Előrehaladás:** {project.get('progress', 0)}%")
                
                with col2:
                    st.subheader("Időzítés")
                    st.write(f"**Kezdés:** {project.get('start', 'Nincs megadva')}")
                    st.write(f"**Befejezés:** {project.get('end', 'Nincs megadva')}")
                    
                    # Calculate duration
                    try:
                        start_date = datetime.strptime(project.get("start", "2025-01-01"), "%Y-%m-%d")
                        end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d")
                        duration = (end_date - start_date).days
                        st.write(f"**Időtartam:** {duration} nap")
                    except:
                        st.write("**Időtartam:** Nincs megadva")
            
            with tab2:
                st.subheader("👥 Dolgozók a projekten")
                members = project.get("members", [])
                if members:
                    st.write(", ".join(members))
                    
                    # Show member details
                    st.write("### Tagok részletei")
                    for member_name in members:
                        # Find the resource details
                        member_resource = None
                        for resource in st.session_state.resources:
                            if resource.get("Név") == member_name:
                                member_resource = resource
                                break
                        
                        if member_resource:
                            with st.expander(f"👤 {member_name}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Pozíció:** {member_resource.get('Pozíció', 'Nincs megadva')}")
                                    st.write(f"**Típus:** {member_resource.get('Típus', 'Nincs megadva')}")
                                    st.write(f"**Elérhetőség:** {member_resource.get('Elérhetőség', 'Elérhető')}")
                                
                                with col2:
                                    st.write(f"**Telefonszám:** {member_resource.get('Telefonszám', 'Nincs megadva')}")
                                    st.write(f"**E-mail:** {member_resource.get('E-mail', 'Nincs megadva')}")
                                    st.write(f"**Tapasztalat:** {member_resource.get('Tapasztalat', 0)} év")
                else:
                    st.info("Nincs hozzárendelt tag a projekthez.")
            
            with tab3:
                st.subheader("📅 Fázisok")
                phases_def = get_default_phases()
                
                # Ensure project has phases_checked field (for legacy items)
                if "phases_checked" not in project or not project["phases_checked"]:
                    project["phases_checked"] = [[False for _ in p["tasks"]] for p in phases_def]
                
                total_tasks = 0
                total_done = 0
                
                for pi, phase in enumerate(phases_def):
                    with st.expander(f"{pi+1}. {phase['name']}"):
                        for ti, task in enumerate(phase["tasks"]):
                            total_tasks += 1
                            current = project["phases_checked"][pi][ti]
                            
                            # Handle both old string format and new object format
                            if isinstance(task, str):
                                task_name = task
                                task_duration = "N/A"
                            else:
                                task_name = task.get("name", "Unknown task")
                                task_profession = task.get("profession", "")
                                task_duration = task.get("duration_days", "N/A")
                                if isinstance(task_duration, int):
                                    task_duration = f"{task_duration} nap"
                                if task_profession:
                                    task_name = f"{task_name} (🔧 {task_profession})"
                            
                            # Display task with duration
                            task_display = f"{task_name} ⏱️ {task_duration}"
                            new_val = st.checkbox(task_display, value=current, key=f"proj_{project_index}_{pi}_{ti}")
                            project["phases_checked"][pi][ti] = new_val
                            if new_val:
                                total_done += 1
                        
                        # per-phase progress
                        phase_total = len(phase["tasks"])
                        phase_done = sum(1 for v in project["phases_checked"][pi] if v)
                        _pct = int(phase_done * 100 / phase_total) if phase_total else 0
                        st.progress(_pct)
                        st.caption(f"{_pct}% ({phase_done}/{phase_total}) - Teljes idő: {phase.get('total_duration_days', 0)} nap")
                
                # Update overall project progress from checked tasks
                project["progress"] = int(total_done * 100 / total_tasks) if total_tasks else 0
            
            with tab4:
                st.subheader("🗺️ Helyszínek")
                locations = project.get("locations", [])
                if locations:
                    st.write(", ".join(locations))
                    
                    # Map for locations
                    points = []
                    for loc in locations:
                        coords = geocode_location(loc)
                        if coords:
                            points.append({"lat": coords[0], "lon": coords[1]})
                    
                    if points:
                        st.map(points, zoom=12)
                    else:
                        st.info("Nem sikerült megjeleníteni a térképet a megadott helyszínekhez.")
                else:
                    st.info("Nincsenek megadva helyszínek.")
            
            with tab5:
                st.subheader("📊 Ütemterv")
                try:
                    proj_start = datetime.fromisoformat(str(project.get("start", "2025-01-01")))
                    proj_end = datetime.fromisoformat(str(project.get("end", "2025-12-31")))
                    duration_days = max((proj_end - proj_start).days, 1)
                    num_phases = max(len(phases_def), 1)
                    slice_days = max(duration_days // num_phases, 1)
                    rows = []
                    current_start = proj_start
                    
                    for pi, phase in enumerate(phases_def):
                        # Use actual phase duration instead of equal slices
                        phase_duration = phase.get('total_duration_days', slice_days)
                        current_end = current_start + timedelta(days=phase_duration)
                        # clamp to project end
                        if pi == num_phases - 1 or current_end > proj_end:
                            current_end = proj_end
                        phase_total = len(phase["tasks"]) or 1
                        phase_done = sum(1 for v in project["phases_checked"][pi] if v) if pi < len(project["phases_checked"]) else 0
                        completion = int(phase_done * 100 / phase_total)
                        rows.append({
                            "Fázis": f"{pi+1}. {phase['name']} ({phase_duration} nap)",
                            "Kezdés": current_start,
                            "Befejezés": current_end,
                            "Készültség": completion,
                        })
                        current_start = current_end
                    
                    if rows:
                        fig = px.timeline(
                            rows,
                            x_start="Kezdés",
                            x_end="Befejezés",
                            y="Fázis",
                            color="Készültség",
                            color_continuous_scale="Blues",
                            title="Fázisok ütemterve",
                        )
                        fig.update_yaxes(autorange="reversed")
                        fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Nincs megjeleníthető ütemterv.")
                except Exception as e:
                    st.error(f"Hiba az ütemterv generálásakor: {str(e)}")
            
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
