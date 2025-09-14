import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
from default_data import get_default_phases, ensure_base_session_state
from navbar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="Project Details – ÉpítAI", layout="wide")

ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

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
                    # Group members by their profession/position
                    profession_groups = {}
                    member_details = {}
                    
                    for member_name in members:
                        # Find the resource details
                        member_resource = None
                        member_index = None
                        for idx, resource in enumerate(st.session_state.resources):
                            if resource.get("Név") == member_name:
                                member_resource = resource
                                member_index = idx
                                break
                        
                        if member_resource:
                            # Use position as profession, fallback to type if position is empty
                            profession = member_resource.get('Pozíció', 'Nincs megadva')
                            if profession == 'Nincs megadva' or not profession.strip():
                                profession = member_resource.get('Típus', 'Ismeretlen')
                            
                            # Group by profession
                            if profession not in profession_groups:
                                profession_groups[profession] = []
                            
                            profession_groups[profession].append({
                                'name': member_name,
                                'resource': member_resource,
                                'index': member_index
                            })
                            member_details[member_name] = {
                                'resource': member_resource,
                                'index': member_index
                            }
                    
                    st.write(f"A projekt **{len(members)}** tagot tartalmaz **{len(profession_groups)}** szakmában:")
                    st.write("")  # Add some spacing
                    
                    # Calculate work hours for each member based on completed tasks
                    phases_def = get_default_phases()
                    member_work_hours = {}
                    
                    # Initialize work hours for all members
                    for member_name in members:
                        member_work_hours[member_name] = {
                            'total_hours': 0,
                            'total_cost': 0,
                            'tasks_completed': 0,
                            'hourly_rate': 0
                        }
                        
                        # Get member's hourly rate
                        member_resource = member_details[member_name]['resource']
                        hourly_rate = member_resource.get('Órabér', 0)
                        member_work_hours[member_name]['hourly_rate'] = hourly_rate
                    
                    # Calculate work hours based on completed tasks
                    for pi, phase in enumerate(phases_def):
                        if pi < len(project.get("phases_checked", [])):
                            for ti, task in enumerate(phase["tasks"]):
                                if project["phases_checked"][pi][ti]:  # Task is completed
                                    # Get task details
                                    if isinstance(task, dict):
                                        task_duration_days = task.get("duration_days", 1)
                                        required_people = task.get("required_people", 1)
                                        task_profession = task.get("profession", "")
                                        
                                        # Calculate hours per person for this task (8 hours per day)
                                        hours_per_person = (task_duration_days * 8) / max(required_people, 1)
                                        
                                        # Find members who could work on this task
                                        for member_name in members:
                                            member_resource = member_details[member_name]['resource']
                                            member_profession = member_resource.get('Pozíció', '')
                                            if not member_profession.strip():
                                                member_profession = member_resource.get('Típus', '')
                                            
                                            # If member's profession matches task profession or if no specific profession required
                                            if not task_profession or task_profession == member_profession:
                                                member_work_hours[member_name]['total_hours'] += hours_per_person
                                                member_work_hours[member_name]['tasks_completed'] += 1
                                                member_work_hours[member_name]['total_cost'] += hours_per_person * member_work_hours[member_name]['hourly_rate']
                    
                    # Display each profession group in separate panels
                    for profession, group_members in profession_groups.items():
                        with st.expander(f"🛠️ {profession} ({len(group_members)} tag)", expanded=True):
                            # Create a table for better organization
                            for member_data in group_members:
                                member_name = member_data['name']
                                member_resource = member_data['resource']
                                member_index = member_data['index']
                                
                                # Get work hours data
                                work_data = member_work_hours[member_name]
                                
                                # Create columns for member info and work hours
                                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                                
                                with col1:
                                    member_type = member_resource.get('Típus', 'Ismeretlen')
                                    member_availability = member_resource.get('Elérhetőség', 'Elérhető')
                                    
                                    if st.button(f"👤 {member_name}", 
                                               key=f"member_link_{profession}_{member_name}", 
                                               help=f"Kattints a '{member_name}' erőforrás részleteinek megtekintéséhez",
                                               use_container_width=True):
                                        # Set the selected resource and navigate to resource details
                                        st.session_state.selected_resource_index = member_index
                                        st.switch_page("pages/resource_details.py")
                                    
                                    st.caption(f"{member_type} ({member_availability})")
                                
                                with col2:
                                    st.metric("⏱️ Munkaóra", f"{work_data['total_hours']:.1f} h")
                                
                                with col3:
                                    st.metric("💰 Költség", f"{work_data['total_cost']:,.0f} Ft")
                                
                                with col4:
                                    st.metric("📋 Feladatok", f"{work_data['tasks_completed']}")
                                
                                st.divider()
                    
                    # Summary section
                    st.subheader("📊 Összesítés")
                    total_hours = sum(data['total_hours'] for data in member_work_hours.values())
                    total_cost = sum(data['total_cost'] for data in member_work_hours.values())
                    total_tasks = sum(data['tasks_completed'] for data in member_work_hours.values())
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("⏱️ Összes munkaóra", f"{total_hours:.1f} h")
                    with col2:
                        st.metric("💰 Összes költség", f"{total_cost:,.0f} Ft")
                    with col3:
                        st.metric("📋 Összes feladat", f"{total_tasks}")
                        
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
            
            with tab6:
                st.subheader("🧱 Anyagköltségek")
                
                # Initialize material costs if not exists
                if "material_costs" not in project:
                    project["material_costs"] = []
                
                # Add new material cost button
                if st.button("➕ Új anyag hozzáadása", key="add_material"):
                    st.session_state.show_add_material = True
                    st.rerun()
                
                # Add material form
                if st.session_state.get("show_add_material", False):
                    st.markdown("---")
                    st.subheader("Új anyag hozzáadása")
                    
                    with st.form("add_material_form"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            material_name = st.text_input("Anyag neve", key="new_material_name")
                        
                        with col2:
                            material_category = st.selectbox(
                                "Kategória",
                                ["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"],
                                key="new_material_category"
                            )
                        
                        with col3:
                            material_quantity = st.number_input("Mennyiség", min_value=0.0, value=1.0, key="new_material_quantity")
                        
                        with col4:
                            material_unit = st.selectbox(
                                "Mértékegység",
                                ["db", "m²", "m³", "kg", "t", "m", "l", "csomag"],
                                key="new_material_unit"
                            )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            material_unit_price = st.number_input("Egységár (Ft)", min_value=0, value=0, key="new_material_unit_price")
                        
                        with col2:
                            material_supplier = st.text_input("Beszállító", key="new_material_supplier")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("✅ Hozzáadás", type="primary"):
                                if material_name and material_unit_price > 0:
                                    total_price = material_quantity * material_unit_price
                                    new_material = {
                                        "name": material_name,
                                        "category": material_category,
                                        "quantity": material_quantity,
                                        "unit": material_unit,
                                        "unit_price": material_unit_price,
                                        "total_price": total_price,
                                        "supplier": material_supplier
                                    }
                                    project["material_costs"].append(new_material)
                                    st.success(f"Anyag hozzáadva: {material_name}")
                                    st.session_state.show_add_material = False
                                    st.rerun()
                                else:
                                    st.error("Az anyag neve és egységára megadása kötelező!")
                        
                        with col2:
                            if st.form_submit_button("❌ Mégse"):
                                st.session_state.show_add_material = False
                                st.rerun()
                
                # Display material costs
                if project["material_costs"]:
                    # Group materials by category
                    categories = {}
                    for material in project["material_costs"]:
                        category = material.get("category", "Egyéb")
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(material)
                    
                    # Display materials by category
                    for category, materials in categories.items():
                        with st.expander(f"📦 {category} ({len(materials)} anyag)", expanded=True):
                            # Create a table for materials in this category
                            for i, material in enumerate(materials):
                                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                                
                                with col1:
                                    st.write(f"**{material['name']}**")
                                    if material.get('supplier'):
                                        st.caption(f"Beszállító: {material['supplier']}")
                                
                                with col2:
                                    st.metric("Mennyiség", f"{material['quantity']} {material['unit']}")
                                
                                with col3:
                                    st.metric("Egységár", f"{material['unit_price']:,} Ft")
                                
                                with col4:
                                    st.metric("Összesen", f"{material['total_price']:,} Ft")
                                
                                with col5:
                                    if st.button("✏️", key=f"edit_material_{i}", help="Szerkesztés"):
                                        st.session_state.edit_material_index = i
                                        st.rerun()
                                
                                with col6:
                                    if st.button("🗑️", key=f"delete_material_{i}", help="Törlés"):
                                        st.session_state.delete_material_index = i
                                        st.rerun()
                                
                                st.divider()
                    
                    # Summary section
                    st.markdown("---")
                    st.subheader("📊 Összesítés")
                    
                    # Calculate totals
                    total_materials = len(project["material_costs"])
                    total_cost = sum(material["total_price"] for material in project["material_costs"])
                    
                    # Calculate by category
                    category_totals = {}
                    for material in project["material_costs"]:
                        category = material.get("category", "Egyéb")
                        if category not in category_totals:
                            category_totals[category] = 0
                        category_totals[category] += material["total_price"]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📦 Összes anyag", f"{total_materials} db")
                    
                    with col2:
                        st.metric("💰 Összes költség", f"{total_cost:,} Ft")
                    
                    with col3:
                        st.metric("📊 Kategóriák", f"{len(category_totals)} db")
                    
                    # Category breakdown
                    st.subheader("📋 Kategóriánkénti bontás")
                    for category, cost in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                        percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                        st.write(f"**{category}:** {cost:,} Ft ({percentage:.1f}%)")
                        st.progress(percentage / 100)
                
                else:
                    st.info("Nincsenek még anyagköltségek rögzítve.")
                    st.caption("💡 Tipp: Kattints az 'Új anyag hozzáadása' gombra az első anyag hozzáadásához.")
                
                # Edit material dialog
                if st.session_state.get("edit_material_index") is not None:
                    edit_index = st.session_state.edit_material_index
                    if edit_index < len(project["material_costs"]):
                        material = project["material_costs"][edit_index]
                        
                        st.markdown("---")
                        st.subheader("Anyag szerkesztése")
                        
                        with st.form("edit_material_form"):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                edit_name = st.text_input("Anyag neve", value=material["name"], key="edit_material_name")
                            
                            with col2:
                                edit_category = st.selectbox(
                                    "Kategória",
                                    ["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"],
                                    index=["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"].index(material.get("category", "Egyéb")),
                                    key="edit_material_category"
                                )
                            
                            with col3:
                                edit_quantity = st.number_input("Mennyiség", min_value=0.0, value=material["quantity"], key="edit_material_quantity")
                            
                            with col4:
                                edit_unit = st.selectbox(
                                    "Mértékegység",
                                    ["db", "m²", "m³", "kg", "t", "m", "l", "csomag"],
                                    index=["db", "m²", "m³", "kg", "t", "m", "l", "csomag"].index(material.get("unit", "db")),
                                    key="edit_material_unit"
                                )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_unit_price = st.number_input("Egységár (Ft)", min_value=0, value=material["unit_price"], key="edit_material_unit_price")
                            
                            with col2:
                                edit_supplier = st.text_input("Beszállító", value=material.get("supplier", ""), key="edit_material_supplier")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Mentés", type="primary"):
                                    if edit_name and edit_unit_price > 0:
                                        project["material_costs"][edit_index] = {
                                            "name": edit_name,
                                            "category": edit_category,
                                            "quantity": edit_quantity,
                                            "unit": edit_unit,
                                            "unit_price": edit_unit_price,
                                            "total_price": edit_quantity * edit_unit_price,
                                            "supplier": edit_supplier
                                        }
                                        st.success("Anyag sikeresen frissítve!")
                                        st.session_state.edit_material_index = None
                                        st.rerun()
                                    else:
                                        st.error("Az anyag neve és egységára megadása kötelező!")
                            
                            with col2:
                                if st.form_submit_button("❌ Mégse"):
                                    st.session_state.edit_material_index = None
                                    st.rerun()
                
                # Delete material confirmation
                if st.session_state.get("delete_material_index") is not None:
                    delete_index = st.session_state.delete_material_index
                    if delete_index < len(project["material_costs"]):
                        material = project["material_costs"][delete_index]
                        
                        st.markdown("---")
                        st.warning(f"⚠️ Biztosan törölni szeretnéd ezt az anyagot: **{material['name']}**?")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✅ Igen, törlés", key="confirm_delete_material"):
                                del project["material_costs"][delete_index]
                                st.success("Anyag sikeresen törölve!")
                                st.session_state.delete_material_index = None
                                st.rerun()
                        
                        with col2:
                            if st.button("❌ Mégse", key="cancel_delete_material"):
                                st.session_state.delete_material_index = None
                                st.rerun()
            
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
