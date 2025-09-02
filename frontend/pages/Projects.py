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
    st.markdown(get_default_phases_markdown())

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
        st.map(points)

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
