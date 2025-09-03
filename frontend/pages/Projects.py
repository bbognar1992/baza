import streamlit as st
import requests

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


def get_default_phases_markdown() -> str:
    return (
        "1. Szerződéskötés\n"
        "   - Ügyfél igényfelmérés\n"
        "   - Ajánlatadás\n"
        "   - Szerződés megírása, kiküldése\n"
        "   - Engedélyek, biztosítások\n"
        "     - [AI] Szerződés sablonok, automatikus kitöltés\n"
        "\n"
        "2. Tervezés\n"
        "   - Építészeti tervek\n"
        "   - Statikai, gépészeti, elektromos tervek\n"
        "   - Engedélyek beadása\n"
        "   - Költségvetés, ütemterv\n"
        "\n"
        "3. Anyag- és erőforrás-tervezés\n"
        "   - Anyagok listázása\n"
        "   - Ajánlatkérések kiküldése\n"
        "   - Beszállítók kiválasztása\n"
        "   - Munkaerő és alvállalkozók ütemezése\n"
        "     - [AI] Ajánlatkérés e-mailben + válaszok feldolgozása\n"
        "\n"
        "4. Kivitelezés\n"
        "   - Alapozás, földmunka\n"
        "   - Falazat, szerkezetépítés\n"
        "   - Tető, nyílászárók\n"
        "   - Gépészet, villanyszerelés\n"
        "   - Vakolás, burkolás, festés\n"
        "   - [AI] Erőforrás ütemezés (időjárás + ember + eszköz)\n"
        "\n"
        "5. Műszaki átadás\n"
        "   - Ellenőrzés, műszaki vezető\n"
        "   - Hibajegyzék készítése\n"
        "   - Használatbavételi engedély\n"
        "   - [AI] Checklist + hibajegyzék automatikus generálás\n"
        "\n"
        "6. Projekt lezárás\n"
        "   - Pénzügyi elszámolás\n"
        "   - Kulcsátadás\n"
        "   - Garanciális időszak indul\n"
    )


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
    st.session_state.projects.append({
        "name": "Alap projekt",
        "start": "2025-01-01",
        "end": "2025-12-31",
        "status": "Folyamatban",
        "members": member_names[:2],
        "locations": ["Győr"],
        "progress": 25,
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

    st.write("### Dolgozók a projekten")
    st.write(", ".join(project.get("members", [])) or "N/A")

    st.write("### Fázisok")
    phases = get_default_phases()
    proj_key_prefix = f"proj_{selected_index}_phase_"
    for pi, phase in enumerate(phases):
        with st.expander(f"{pi+1}. {phase['name']}"):
            for ti, task in enumerate(phase["tasks"]):
                key = f"{proj_key_prefix}{pi}_task_{ti}"
                default_val = st.session_state.get(key, False)
                checked = st.checkbox(task, value=default_val, key=key)
            # Optional: show simple completion ratio per phase
            total = len(phase["tasks"])
            done = sum(1 for ti in range(total) if st.session_state.get(f"{proj_key_prefix}{pi}_task_{ti}", False))
            st.progress(int(done * 100 / total) if total else 0)

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

    st.write("### Folyamatban lévő projektek")

    if st.session_state.projects:
        header = st.columns([3, 2, 2, 2, 2])
        header[0].markdown("**Név**")
        header[1].markdown("**Kezdés**")
        header[2].markdown("**Befejezés**")
        header[3].markdown("**Státusz**")
        header[4].markdown("**Művelet**")

        for idx, proj in enumerate(st.session_state.projects):
            cols = st.columns([3, 2, 2, 2, 2])
            cols[0].markdown(f"**{proj['name']}**")
            cols[1].write(proj["start"])
            cols[2].write(proj["end"])
            cols[3].write(proj["status"])
            if cols[4].button("Megnyitás", key=f"open_{idx}"):
                st.session_state.selected_project_index = idx
                st.rerun()
    else:
        st.info("Még nincs projekt. Hozz létre egyet fentebb.")
