import streamlit as st
import requests
import pandas as pd
import random
from datetime import date, timedelta
from default_data import ensure_base_session_state, get_default_phases
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="Időjárás alapú ütemezés – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("🌤️ Időjárás alapú ütemezés")

st.write("Heti előrejelzés alapján megmutatjuk, mely projektek tudnak haladni.")


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


@st.cache_data(show_spinner=False)
def geocode_location(name: str):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": name, "format": "json", "limit": 1},
            headers={"User-Agent": "epit-ai/1.0"},
            timeout=6,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False)
def fetch_weekly_weather(lat: float, lon: float, start: date, end: date):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_hours,precipitation_probability_mean,weathercode",
            "timezone": "auto",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


ensure_base_session_state(st)

col_a, col_b = st.columns([1, 2])
with col_a:
    start_day = st.date_input("Hét kezdete", value=date.today())
    end_day = start_day + timedelta(days=6)
with col_b:
    st.caption(f"Időszak: {start_day.isoformat()} – {end_day.isoformat()}")

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
        })
        continue

    coords = geocode_location(locs[0])
    if not coords:
        # Get actual tasks and required people for projects with geocoding issues
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
            "Helyszín": locs[0],
            "Összegzés": "Helyszín nem geokódolható",
            "Haladhat": False,
            "Aktuális feladatok": tasks_text,
            "Szükséges személyek száma": people_text,
        })
        continue

    weather = fetch_weekly_weather(coords[0], coords[1], start_day, end_day)
    if not weather or "daily" not in weather:
        # Get actual tasks and required people for projects with weather data issues
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
            "Helyszín": locs[0],
            "Összegzés": "Időjárási adatok nem elérhetők",
            "Haladhat": False,
            "Aktuális feladatok": tasks_text,
            "Szükséges személyek száma": people_text,
        })
        continue

    daily = weather["daily"]
    probs = daily.get("precipitation_probability_mean", [])
    hours = daily.get("precipitation_hours", [])
    # Heurisztika: haladhat, ha a héten a napok többségén alacsony csapadék esély és kevés csapadékos óra várható
    good_days = 0
    total_days = min(len(probs), len(hours))
    for p, h in zip(probs, hours):
        if (p or 0) < 40 and (h or 0) <= 2:
            good_days += 1
    can_progress = total_days > 0 and good_days >= max(3, total_days // 2)
    summary = f"Kedvező napok: {good_days}/{total_days} (eső < 40%, esős órák ≤ 2)"

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
    })


# Create a single table with all projects
st.subheader("📊 Projektek időjárás alapú ütemezése")

if rows:
    # Create table header with 6 columns
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 2.5, 2, 2, 1.5])
    with col1:
        st.markdown("**Projekt**")
    with col2:
        st.markdown("**Helyszín**")
    with col3:
        st.markdown("**Összegzés**")
    with col4:
        st.markdown("**Aktuális feladatok**")
    with col5:
        st.markdown("**Szükséges személyek száma**")
    with col6:
        st.markdown("**Státusz**")
    
    # Add separator
    st.markdown("---")
    
    # Display each row with conditional styling
    for r in rows:
        status = "✅ Haladhat" if r["Haladhat"] else "⚠️ Nem haladhat"
        
        # Choose background color based on status
        if r["Haladhat"]:
            # Green background for projects that can proceed
            st.markdown(f"""
            <div style="background-color: #e8f5e8; padding: 10px; margin: 2px 0; border-radius: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="flex: 2; font-weight: 500;">{r['Projekt']}</div>
                    <div style="flex: 1.5;">{r['Helyszín']}</div>
                    <div style="flex: 2.5;">{r['Összegzés']}</div>
                    <div style="flex: 2;">{r['Aktuális feladatok']}</div>
                    <div style="flex: 2;">{r['Szükséges személyek száma']}</div>
                    <div style="flex: 1.5; text-align: center;">{status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Red background for projects that cannot proceed
            st.markdown(f"""
            <div style="background-color: #ffebee; padding: 10px; margin: 2px 0; border-radius: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="flex: 2; font-weight: 500;">{r['Projekt']}</div>
                    <div style="flex: 1.5;">{r['Helyszín']}</div>
                    <div style="flex: 2.5;">{r['Összegzés']}</div>
                    <div style="flex: 2;">{r['Aktuális feladatok']}</div>
                    <div style="flex: 2;">{r['Szükséges személyek száma']}</div>
                    <div style="flex: 1.5; text-align: center;">{status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Nincs projekt az időszakban.")


