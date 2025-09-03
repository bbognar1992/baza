import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Projects – ÉpítAI", layout="wide")

st.title("📁 Projektek")

st.write("Itt tudod kezelni az aktuális projekteket.")


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

def get_default_phases():
    return [
        {
            "name": "Szerződéskötés",
            "tasks": [
                "Ügyfél igényfelmérés",
                "Ajánlatadás",
                "Szerződés megírása, kiküldése",
                "Engedélyek, biztosítások",
                "[AI] Szerződés sablonok, automatikus kitöltés",
            ],
        },
        {
            "name": "Tervezés",
            "tasks": [
                "Építészeti tervek",
                "Statikai, gépészeti, elektromos tervek",
                "Engedélyek beadása",
                "Költségvetés, ütemterv",
            ],
        },
        {
            "name": "Anyag- és erőforrás-tervezés",
            "tasks": [
                "Anyagok listázása",
                "Ajánlatkérések kiküldése",
                "Beszállítók kiválasztása",
                "Munkaerő és alvállalkozók ütemezése",
                "[AI] Ajánlatkérés e-mailben + válaszok feldolgozása",
            ],
        },
        {
            "name": "Kivitelezés",
            "tasks": [
                "Alapozás, földmunka",
                "Falazat, szerkezetépítés",
                "Tető, nyílászárók",
                "Gépészet, villanyszerelés",
                "Vakolás, burkolás, festés",
                "[AI] Erőforrás ütemezés (időjárás + ember + eszköz)",
            ],
        },
        {
            "name": "Műszaki átadás",
            "tasks": [
                "Ellenőrzés, műszaki vezető",
                "Hibajegyzék készítése",
                "Használatbavételi engedély",
                "[AI] Checklist + hibajegyzék automatikus generálás",
            ],
        },
        {
            "name": "Projekt lezárás",
            "tasks": [
                "Pénzügyi elszámolás",
                "Kulcsátadás",
                "Garanciális időszak indul",
            ],
        },
    ]

# Simple in-memory store in session
if "projects" not in st.session_state:
    st.session_state.projects = []
if "selected_project_index" not in st.session_state:
    st.session_state.selected_project_index = None
if "resources" not in st.session_state:
    st.session_state.resources = [
        {"Típus": "Alkalmazott", "Név": "Kiss János", "Pozíció": "Kőműves"},
        {"Típus": "Alvállalkozó", "Név": "Acél Kft.", "Pozíció": "Vasszerkezetek"},
    ]

# Seed a default project if none exist
if not st.session_state.projects:
    member_names = [r.get("Név", "") for r in st.session_state.resources if r.get("Név")]
    _phases = get_default_phases()
    _phases_checked = [[False for _ in phase["tasks"]] for phase in _phases]
    st.session_state.projects.append({
        "name": "Alap projekt",
        "start": "2025-01-01",
        "end": "2025-12-31",
        "status": "Folyamatban",
        "members": member_names[:2],
        "locations": ["Győr"],
        "progress": 25,
        "phases_checked": _phases_checked,
    })
    # Add 25 more sample projects
    cities = ["Győr", "Budapest", "Debrecen", "Szeged", "Pécs", "Miskolc", "Veszprém"]
    statuses = ["Tervezés alatt", "Folyamatban", "Késésben", "Lezárt"]
    for i in range(1, 26):
        start_month = (i % 12) + 1
        end_month = ((i + 5) % 12) + 1
        city = cities[i % len(cities)]
        status = statuses[i % len(statuses)]
        st.session_state.projects.append({
            "name": f"Családi ház {i}",
            "start": f"2025-{start_month:02d}-01",
            "end": f"2025-{end_month:02d}-28",
            "status": status,
            "members": member_names[:2],
            "locations": [city],
            "progress": 100 if status == "Lezárt" else (i * 7) % 100,
            "phases_checked": [[False for _ in phase["tasks"]] for phase in _phases],
        })

selected_index = st.session_state.selected_project_index

# If a project is selected, show its details view
if selected_index is not None and 0 <= selected_index < len(st.session_state.projects):
    project = st.session_state.projects[selected_index]

    st.subheader(project["name"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Állapot", project.get("status", "Ismeretlen"))
    with col2:
        st.metric("Kezdés", project.get("start", "-"))
    with col3:
        st.metric("Befejezés", project.get("end", "-"))

    st.write("### Haladás")
    st.progress(int(project.get("progress", 0)))
    st.caption(f"{int(project.get('progress', 0))}%")

    st.write("### Dolgozók a projekten")
    st.write(", ".join(project.get("members", [])) or "N/A")

    st.write("### Fázisok")
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
                new_val = st.checkbox(task, value=current, key=f"proj_{selected_index}_{pi}_{ti}")
                project["phases_checked"][pi][ti] = new_val
                if new_val:
                    total_done += 1
            # per-phase progress
            phase_total = len(phase["tasks"])
            phase_done = sum(1 for v in project["phases_checked"][pi] if v)
            _pct = int(phase_done * 100 / phase_total) if phase_total else 0
            st.progress(_pct)
            st.caption(f"{_pct}% ({phase_done}/{phase_total})")

    # Update overall project progress from checked tasks
    project["progress"] = int(total_done * 100 / total_tasks) if total_tasks else 0

    # Gantt chart for phases based on project start/end
    st.write("### Ütemterv")
    try:
        proj_start = datetime.fromisoformat(str(project.get("start", "2025-01-01")))
        proj_end = datetime.fromisoformat(str(project.get("end", "2025-12-31")))
        duration_days = max((proj_end - proj_start).days, 1)
        num_phases = max(len(phases_def), 1)
        slice_days = max(duration_days // num_phases, 1)
        rows = []
        current_start = proj_start
        for pi, phase in enumerate(phases_def):
            current_end = current_start + timedelta(days=slice_days)
            # clamp to project end
            if pi == num_phases - 1 or current_end > proj_end:
                current_end = proj_end
            phase_total = len(phase["tasks"]) or 1
            phase_done = sum(1 for v in project["phases_checked"][pi] if v) if pi < len(project["phases_checked"]) else 0
            completion = int(phase_done * 100 / phase_total)
            rows.append({
                "Fázis": f"{pi+1}. {phase['name']}",
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
    except Exception:
        pass

    st.write("### Helyszínek")
    locations = project.get("locations", [])
    st.write(", ".join(locations) or "N/A")

    # Map for locations
    points = []
    for loc in locations:
        coords = geocode_location(loc)
        if coords:
            points.append({"lat": coords[0], "lon": coords[1]})
    if points:
        st.map(points, zoom=12)

    if st.button("⬅️ Vissza a listához"):
        st.session_state.selected_project_index = None
        st.rerun()

# Otherwise show creation form and list
else:
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
        tab_future, tab_active, tab_closed = st.tabs(["Jövőbeli", "Folyamatban lévő", "Lezárt"]) 

        def render_list(projects_subset, subset_key_prefix=""):
            if not projects_subset:
                st.info("Nincs megjeleníthető projekt.")
                return
            header = st.columns([3, 2, 2, 2, 2])
            header[0].markdown("**Név**")
            header[1].markdown("**Kezdés**")
            header[2].markdown("**Befejezés**")
            header[3].markdown("**Státusz**")
            header[4].markdown("**Művelet**")
            for idx, proj in enumerate(projects_subset):
                cols = st.columns([3, 2, 2, 2, 2])
                cols[0].markdown(f"**{proj['name']}**")
                cols[1].write(proj["start"])
                cols[2].write(proj["end"])
                cols[3].write(proj["status"])
                # Find original index to open details
                try:
                    original_idx = st.session_state.projects.index(proj)
                except ValueError:
                    original_idx = None
                if cols[4].button("Megnyitás", key=f"open_{subset_key_prefix}{idx}"):
                    if original_idx is not None:
                        st.session_state.selected_project_index = original_idx
                        st.rerun()

        future_projects = [p for p in st.session_state.projects if p.get("status") in ("Tervezés alatt",)]
        active_projects = [p for p in st.session_state.projects if p.get("status") in ("Folyamatban", "Késésben")]
        closed_projects = [p for p in st.session_state.projects if p.get("status") in ("Lezárt",)]

        with tab_future:
            render_list(future_projects, "future_")
        with tab_active:
            render_list(active_projects, "active_")
        with tab_closed:
            render_list(closed_projects, "closed_")
    else:
        st.info("Még nincs projekt. Hozz létre egyet fentebb.")
