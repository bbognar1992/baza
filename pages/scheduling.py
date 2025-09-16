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

st.title("📅 Következő nap ütemezése")

st.write("A következő munkanap előrejelzése alapján megmutatjuk, mely projektek tudnak haladni.")


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

def render_task_assignments(project_name, actual_tasks):
    """Render task assignment interface for a project"""
    # Initialize task assignments in session state if not exists
    project_key = f"task_assignments_{project_name}"
    if project_key not in st.session_state:
        st.session_state[project_key] = {}
    
    if actual_tasks:
        # Use form to prevent immediate page reload
        with st.form(key=f"form_{project_name}"):
            for i, task in enumerate(actual_tasks):
                # Get available resources (excluding suppliers)
                available_resources = [
                    r for r in st.session_state.resources 
                    if r.get("Típus") != "Beszállító" and r.get("Név")
                ]
                
                if available_resources:
                    # Create resource options for multi-select
                    resource_options = [f"{r.get('Név', '')} ({r.get('Pozíció', 'Ismeretlen')})" for r in available_resources]
                    
                    # Get current assignments for this task
                    task_key = f"task_{i}_{task}"
                    current_assignments = st.session_state[project_key].get(task_key, [])
                    
                    # Ensure current_assignments is a list
                    if not isinstance(current_assignments, list):
                        current_assignments = []
                    
                    # Resource assignment multi-select
                    selected_resources = st.multiselect(
                        f"**{i+1}. {task}**",
                        options=resource_options,
                        default=current_assignments,
                        key=f"assign_{project_name}_{i}_{task}"
                    )
            
            # Submit button to save all assignments at once
            submitted = st.form_submit_button("💾 Mentés", type="primary")
            
            if submitted:
                # Update session state with all selections
                for i, task in enumerate(actual_tasks):
                    task_key = f"task_{i}_{task}"
                    multiselect_key = f"assign_{project_name}_{i}_{task}"
                    if multiselect_key in st.session_state:
                        st.session_state[project_key][task_key] = st.session_state[multiselect_key]
                st.success("✅ Hozzárendelések mentve!")
    else:
        st.markdown("Nincsenek megadva feladatok.")


ensure_base_session_state(st)

col_a, col_b = st.columns([1, 2])
with col_a:
    current_date = st.date_input("Mai dátum", value=date.today())
    next_working_day = get_next_working_day(current_date)
with col_b:
    st.caption(f"Következő munkanap: {next_working_day.strftime('%Y-%m-%d (%A)')}")

# Resources expander
with st.expander("👥 Elérhető erőforrások", expanded=False):
    if st.session_state.resources:
        # Group resources by profession and count them
        profession_counts = {}
        for resource in st.session_state.resources:
            # Skip suppliers (Beszállító)
            if resource.get("Típus") == "Beszállító":
                continue
                
            profession = resource.get("Pozíció", "Szakma nincs megadva")
            if profession not in profession_counts:
                profession_counts[profession] = 0
            profession_counts[profession] += 1
        
        if profession_counts:
            st.write("**Szakmák és elérhető személyek száma:**")
            for profession, count in profession_counts.items():
                st.write(f"• **{profession}**: {count} személy")
        else:
            st.info("Nincsenek elérhető szakemberek a rendszerben.")
    else:
        st.info("Nincsenek erőforrások a rendszerben.")

if not st.session_state.projects:
    st.info("Nincs projekt a rendszerben. Adj hozzá projekteket a Projektek oldalon.")
    st.stop()

projects_in_progress = [
    p for p in st.session_state.projects if p.get("status") == "Folyamatban" or p.get("status") == "Késésben"
]
if not projects_in_progress:
    st.info("Nincs folyamatban lévő projekt a rendszerben.")
    st.stop()


rows = []
for idx, proj in enumerate(projects_in_progress):
    locs = proj.get("locations") or []
    if not locs:
        # Get actual tasks and required people for projects without location
        actual_tasks = proj.get("current_tasks", []) or get_random_tasks()
        required_people = proj.get("required_people", []) or get_random_people()
        
        # Format actual tasks
        if actual_tasks:
            tasks_text = ", ".join(actual_tasks[:3])
            if len(actual_tasks) > 3:
                tasks_text += f" (+{len(actual_tasks) - 3} további)"
        else:
            tasks_text = "Nincs megadva"
        
        # Format required people count
        if required_people:
            people_text = str(len(required_people))
        else:
            people_text = "0"
            
        rows.append({
            "Projekt": proj.get("name", f"Projekt {idx+1}"),
            "Helyszín": "-",
            "Összegzés": "Helyszín nincs megadva",
            "Haladhat": False,
            "Aktuális feladatok": tasks_text,
            "Szükséges személyek száma": people_text,
            "Méret": random.randint(80, 200),
        })
        continue

    # Use fake weather data instead of API calls
    weather = get_fake_weather_data(locs[0])

    daily = weather["daily"]
    probs = daily.get("precipitation_probability_mean", [])
    hours = daily.get("precipitation_hours", [])
    # Heurisztika: haladhat, ha a következő munkanapon alacsony csapadék esély és kevés csapadékos óra várható
    if probs and hours:
        prob = probs[0] or 0
        hour = hours[0] or 0
        can_progress = prob < 40 and hour <= 2
        summary = f"Csapadék esély: {prob}%, esős órák: {hour} (haladhat: {prob < 40 and hour <= 2})"
    else:
        can_progress = False
        summary = "Időjárási adatok nem elérhetők"

    # Get actual tasks and required people
    actual_tasks = proj.get("current_tasks", []) or get_random_tasks()
    required_people = proj.get("required_people", []) or get_random_people()
    
    # Format actual tasks
    if actual_tasks:
        tasks_text = ", ".join(actual_tasks[:3])  # Show first 3 tasks
        if len(actual_tasks) > 3:
            tasks_text += f" (+{len(actual_tasks) - 3} további)"
    else:
        tasks_text = "Nincs megadva"
    
    # Format required people count
    if required_people:
        people_text = str(len(required_people))
    else:
        people_text = "0"

    rows.append({
        "Projekt": proj.get("name", f"Projekt {idx+1}"),
        "Helyszín": locs[0],
        "Összegzés": summary,
        "Haladhat": can_progress,
        "Aktuális feladatok": tasks_text,
        "Szükséges személyek száma": people_text,
        "Méret": proj.get("size", "Nincs megadva"),
    })


# Display projects in expanders
st.subheader("📊 Projektek következő nap ütemezése")

if rows:
    for r in rows:
        status = "✅ Haladhat" if r["Haladhat"] else "⚠️ Nem haladhat"
        
        # Determine if project is weather-sensitive (cannot proceed)
        is_weather_sensitive = not r["Haladhat"]
        
        # Create expander with conditional styling
        if is_weather_sensitive:
            # Red expander for weather-sensitive projects
            with st.expander(f"🔴 {r['Projekt']} - {status}", expanded=True):
                st.markdown(f"**Helyszín:** {r['Helyszín']}")
                st.markdown(f"**Méret:** {r['Méret']}")
                st.markdown(f"**Időjárás összegzés:** {r['Összegzés']}")
                
                # Show tasks and resource assignments
                st.markdown("**Aktuális feladatok és szakember hozzárendelések:**")
                
                # Get the actual project data to show detailed task information
                project_data = next((p for p in projects_in_progress if p.get("name") == r['Projekt']), None)
                if project_data:
                    # Get actual tasks
                    actual_tasks = project_data.get("current_tasks", []) or get_random_tasks()
                    
                    # Render task assignments
                    render_task_assignments(r['Projekt'], actual_tasks)
                else:
                    st.markdown("Projekt adatok nem elérhetők.")
        else:
            # Normal expander for projects that can proceed
            with st.expander(f"🟢 {r['Projekt']} - {status}", expanded=True):
                st.markdown(f"**Helyszín:** {r['Helyszín']}")
                st.markdown(f"**Méret:** {r['Méret']}")
                st.markdown(f"**Időjárás összegzés:** {r['Összegzés']}")
                
                # Show tasks and resource assignments
                st.markdown("**Aktuális feladatok és szakember hozzárendelések:**")
                
                # Get the actual project data to show detailed task information
                project_data = next((p for p in projects_in_progress if p.get("name") == r['Projekt']), None)
                if project_data:
                    # Get actual tasks
                    actual_tasks = project_data.get("current_tasks", []) or get_random_tasks()
                    
                    # Render task assignments
                    render_task_assignments(r['Projekt'], actual_tasks)
                else:
                    st.markdown("Projekt adatok nem elérhetők.")
else:
    st.info("Nincs projekt az időszakban.")


