import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta
from default_data import ensure_base_session_state, get_default_phases
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in
import random

st.set_page_config(page_title="Következő nap ütemezése – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("📅 Ütemezése")

st.write("Az erőforrások hozzárendelése a kiválasztott dátumtól kezdve történik. Amint egy erőforrás egy feladathoz lett rendelve, a befejezésig vagy módosításig azon a feladaton marad.")


def get_random_tasks():
    """Get random tasks from default phases"""
    phases = get_default_phases()
    all_tasks = []
    for phase in phases:
        for task in phase.get("tasks", []):
            all_tasks.append(task.get("name", ""))
    
    # Return 1-4 random tasks
    num_tasks = random.randint(1, 4)
    return random.sample(all_tasks, min(num_tasks, len(all_tasks)))


def get_random_people():
    """Get random people from resources"""
    if not st.session_state.resources:
        return []
    
    # Return 1-3 random people
    num_people = random.randint(1, 3)
    available_people = [r.get("Név", "") for r in st.session_state.resources if r.get("Név")]
    return random.sample(available_people, min(num_people, len(available_people)))


def get_next_working_day(current_date):
    """Get the next working day, skipping weekends"""
    next_day = current_date + timedelta(days=1)
    # Skip weekends (Saturday=5, Sunday=6)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day

def get_fake_weather_data(location_name: str):
    """Generate fake weather data for demonstration purposes"""
    import random
    
    # Generate random weather data for 1 day
    daily_data = {
        "precipitation_probability_mean": [random.randint(10, 80)],
        "precipitation_hours": [random.randint(0, 6)]
    }
    
    return {
        "daily": daily_data
    }

def get_task_profession(task_name, phases):
    """Get the required profession for a task from phases"""
    for phase in phases:
        for task in phase.get("tasks", []):
            if task.get("name") == task_name:
                return task.get("profession", "")
    return ""

def get_used_resources_from_session():
    """Get all currently assigned resources from session state"""
    used_resources = set()
    
    if "task_assignments" in st.session_state:
        for task_id, assignments in st.session_state.task_assignments.items():
            if isinstance(assignments, list):
                for assignment in assignments:
                    # Extract resource name from "Name (Position)" format
                    resource_name = assignment.split(" (")[0]
                    used_resources.add(resource_name)
    
    return used_resources

def get_available_resources_for_task(task_profession, used_resources):
    """Get resources that match the task profession and are not already used"""
    available_resources = []
    
    for resource in st.session_state.resources:
        # Skip suppliers
        if resource.get("Típus") == "Beszállító":
            continue
            
        # Skip if already used
        resource_name = resource.get("Név", "")
        if resource_name in used_resources:
            continue
            
        # Check if resource has the required profession or skills
        resource_position = resource.get("Pozíció", "")
        resource_skills = resource.get("Készségek", "").lower()
        
        # Match by exact profession or by skills
        if (task_profession and 
            (resource_position == task_profession or 
             (task_profession.lower() in resource_skills) or
             (resource_position.lower() in task_profession.lower()))):
            available_resources.append(resource)
        elif not task_profession:  # If no specific profession required
            available_resources.append(resource)
    
    return available_resources

def get_tasks_grouped_by_location():
    """Get all tasks grouped by location"""
    location_groups = {}
    phases = get_default_phases()
    
    projects_in_progress = [
        p for p in st.session_state.projects if p.get("status") == "Folyamatban" or p.get("status") == "Késésben"
    ]
    
    for project in projects_in_progress:
        project_name = project.get("name", "")
        locations = project.get("locations", [])
        
        # Get weather data for projects with locations
        if locations:
            weather = get_fake_weather_data(locations[0])
            daily = weather["daily"]
            probs = daily.get("precipitation_probability_mean", [])
            hours = daily.get("precipitation_hours", [])
            
            if probs and hours:
                prob = probs[0] or 0
                hour = hours[0] or 0
                can_progress = prob < 40 and hour <= 2
                weather_summary = f"Csapadék esély: {prob}%, esős órák: {hour}"
            else:
                can_progress = False
                weather_summary = "Időjárási adatok nem elérhetők"
        else:
            can_progress = True  # Projects without location can always progress
            weather_summary = "Helyszín nincs megadva"
        
        # Get tasks for this project
        actual_tasks = project.get("current_tasks", []) or get_random_tasks()
        
        for i, task in enumerate(actual_tasks):
            task_profession = get_task_profession(task, phases)
            location = locations[0] if locations else "Helyszín nincs megadva"
            
            # Group by location
            if location not in location_groups:
                location_groups[location] = {
                    "weather_summary": weather_summary,
                    "can_progress": can_progress,
                    "tasks": []
                }
            
            location_groups[location]["tasks"].append({
                "Projekt": project_name,
                "Feladat": task,
                "Szükséges szakma": task_profession or "Nincs megadva",
                "Helyszín": location,
                "Időjárás": weather_summary,
                "Haladhat": can_progress,
                "Projekt méret": project.get("size", "Nincs megadva"),
                "task_id": f"{project_name}_{i}_{task}"
            })
    
    return location_groups


ensure_base_session_state(st)

col_a, col_b = st.columns([1, 2])
with col_a:
    current_date = st.date_input("Dátum kiválasztása", value=date.today())

if not st.session_state.projects:
    st.info("Nincs projekt a rendszerben. Adj hozzá projekteket a Projektek oldalon.")
    st.stop()

projects_in_progress = [
    p for p in st.session_state.projects if p.get("status") == "Folyamatban" or p.get("status") == "Késésben"
]
if not projects_in_progress:
    st.info("Nincs folyamatban lévő projekt a rendszerben.")
    st.stop()


# Get tasks grouped by location
location_groups = get_tasks_grouped_by_location()

# Initialize task assignments in session state if not exists
if "task_assignments" not in st.session_state:
    st.session_state.task_assignments = {}

if location_groups:
    tab1, tab2 = st.tabs(["Feladat-hozzárendelés", "Erőforrás-helyszín táblázat"])
    with tab1:
        # Get currently used resources from session state
        used_resources = get_used_resources_from_session()
        
        # Create a form for all
        with st.form("task_assignments_form"):
            # Display each location as a separate table
            for location, location_data in location_groups.items():
                tasks = location_data["tasks"]
                weather_summary = location_data["weather_summary"]
                can_progress = location_data["can_progress"]
                
                # Determine container color based on weather
                if can_progress:
                    container_color = "green"
                    status_icon = "✅"
                else:
                    container_color = "orange"
                    status_icon = "⚠️"
                
                # Create colored container for this location
                with st.container():
                    # Add custom CSS for colored background
                    st.markdown(f"""
                    <div style="
                        background-color: {'#d4edda' if container_color == 'green' else '#fff3cd'};
                        border: 2px solid {'#c3e6cb' if container_color == 'green' else '#ffeaa7'};
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                    ">
                    """, unsafe_allow_html=True)
                    
                    # Location header with weather info
                    st.markdown(f"### 📍 {location} {status_icon}")
                    
                    if weather_summary != "Helyszín nincs megadva":
                        st.caption(f"Időjárás: {weather_summary}")
                    
                    # Create table for this location
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        st.markdown("**Projekt**")
                    with col2:
                        st.markdown("**Feladat**")
                    with col3:
                        st.markdown("**Hozzárendelt szakemberek**")
                    
                    st.markdown("---")
                    
                    # Display each task as a row
                    for row in tasks:
                        col1, col2, col3 = st.columns([2, 2, 2])
                        
                        with col1:
                            st.write(row["Projekt"])
                        with col2:
                            st.write(row["Feladat"])
                        with col3:
                            # Get available resources for this task
                            task_profession = row["Szükséges szakma"]
                            available_resources = get_available_resources_for_task(task_profession, used_resources)
                            
                            if available_resources:
                                # Create resource options
                                resource_options = [f"{r.get('Név', '')} ({r.get('Pozíció', 'Ismeretlen')})" for r in available_resources]
                                
                                # Get current assignments for this task
                                task_id = row["task_id"]
                                current_assignments = st.session_state.task_assignments.get(task_id, [])
                                
                                # Ensure current_assignments is a list
                                if not isinstance(current_assignments, list):
                                    current_assignments = []
                                
                                # Resource assignment multi-select
                                selected_resources = st.multiselect(
                                    "",
                                    options=resource_options,
                                    default=current_assignments,
                                    key=f"assign_{task_id}",
                                    label_visibility="collapsed"
                                )
                    
                    # Close the colored container
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Single save button for all assignments
            submitted = st.form_submit_button("💾 Összes hozzárendelés mentése", type="primary")
            
            if submitted:
                # Update session state with all selections from all locations
                for location, location_data in location_groups.items():
                    for row in location_data["tasks"]:
                        task_id = row["task_id"]
                        multiselect_key = f"assign_{task_id}"
                        if multiselect_key in st.session_state:
                            st.session_state.task_assignments[task_id] = st.session_state[multiselect_key]
                st.success("✅ Összes hozzárendelés mentve!")
                st.rerun()
            else:
                st.info("Nincs feladat az időszakban.")

    with tab2:
        st.subheader("👥 Erőforrás-helyszín táblázat")
        
        # Get all available resources (excluding suppliers)
        available_resources = [
            r for r in st.session_state.resources 
            if r.get("Típus") != "Beszállító" and r.get("Név")
        ]
        
        if available_resources:
            # Create a table showing resources and their assigned locations
            table_data = []
            
            for resource in available_resources:
                resource_name = resource.get("Név", "")
                resource_position = resource.get("Pozíció", "Ismeretlen")
                
                # Find assigned locations for this resource
                assigned_locations = set()
                
                for task_id, assignments in st.session_state.task_assignments.items():
                    if isinstance(assignments, list):
                        for assignment in assignments:
                            if assignment.startswith(resource_name):
                                # Find the task details
                                for location, location_data in location_groups.items():
                                    for task_row in location_data["tasks"]:
                                        if task_row["task_id"] == task_id:
                                            assigned_locations.add(location)
                                            break
                
                # Create table row
                if assigned_locations:
                    locations_text = ", ".join(sorted(assigned_locations))
                else:
                    locations_text = "Nincs hozzárendelve"
                
                table_data.append({
                    "Erőforrás": f"{resource_name} ({resource_position})",
                    "Helyszín": locations_text,
                })
            
            # Display the table using st.table
            if table_data:
                st.table(table_data)
            else:
                st.info("Nincsenek hozzárendelt erőforrások.")
        else:
            st.info("Nincsenek elérhető erőforrások.")

# Show current assignments summary
if "task_assignments" in st.session_state and st.session_state.task_assignments:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📋 Aktuális hozzárendelések összefoglalója")
    
    with col2:
        if st.button("🗑️ Összes hozzárendelés törlése", type="secondary"):
            st.session_state.task_assignments = {}
            st.success("✅ Összes hozzárendelés törölve!")
            st.rerun()
    
    assignment_summary = {}
    for task_id, assignments in st.session_state.task_assignments.items():
        if isinstance(assignments, list) and assignments:
            # Extract project and task from task_id
            parts = task_id.split("_", 2)
            if len(parts) >= 3:
                project_name = parts[0]
                task_name = parts[2]
                
                if project_name not in assignment_summary:
                    assignment_summary[project_name] = []
                
                assignment_summary[project_name].append({
                    "task": task_name,
                    "resources": assignments
                })
    
    if assignment_summary:
        for project_name, tasks in assignment_summary.items():
            with st.expander(f"📁 {project_name}", expanded=False):
                for task_info in tasks:
                    st.write(f"**{task_info['task']}:** {', '.join(task_info['resources'])}")
                else:
                    st.info("Nincsenek aktív hozzárendelések.")


