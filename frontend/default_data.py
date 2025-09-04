import random
from datetime import datetime, timedelta


def get_default_resources():
    return [
        {"Típus": "Alkalmazott", "Név": "Kiss János", "Pozíció": "Kőműves"},
        {"Típus": "Alvállalkozó", "Név": "Acél Kft.", "Pozíció": "Vasszerkezetek"},
        {"Típus": "Beszállító", "Név": "ÉpAnyag Zrt.", "Pozíció": "Beton, tégla"},
        {"Típus": "Beszállító", "Név": "FaTrade Kft.", "Pozíció": "Faanyagok"},
        {"Típus": "Beszállító", "Név": "VillTech Bt.", "Pozíció": "Villanyszerelési anyagok"},
        {"Típus": "Beszállító", "Név": "GépGURU Kft.", "Pozíció": "Gépek, bérlés"},
    ]


def get_default_profession_types():
    return [
        {"Név": "Kőműves", "Leírás": "Falazat, betonozás, vakolás", "Szint": "Szakmunkás"},
        {"Név": "Villanyszerelő", "Leírás": "Elektromos hálózatok, kapcsolók, csatlakozók", "Szint": "Szakmunkás"},
        {"Név": "Víz-gáz-fűtésszerelő", "Leírás": "Vízvezetékek, fűtés, szellőztetés", "Szint": "Szakmunkás"},
        {"Név": "Ács", "Leírás": "Fa szerkezetek, tetőfedés", "Szint": "Szakmunkás"},
        {"Név": "Burkoló", "Leírás": "Padló, falburkolatok", "Szint": "Szakmunkás"},
        {"Név": "Festő", "Leírás": "Festés, tapétázás", "Szint": "Szakmunkás"},
        {"Név": "Műszaki vezető", "Leírás": "Projekt koordináció, minőségbiztosítás", "Szint": "Vezető"},
        {"Név": "Építésvezető", "Leírás": "Teljes építkezés irányítása", "Szint": "Vezető"},
    ]


def get_default_project_types():
    return [
        {"Név": "Földszintes ház", "Leírás": "Egyszintes családi ház"},
        {"Név": "Tetőteres ház", "Leírás": "Beépített tetőterű családi ház"},
    ]


def get_default_phases():
    return [
        {
            "name": "Szerződéskötés",
            "tasks": [
                {"name": "Ügyfél igényfelmérés", "profession": "Építésvezető", "duration_days": 3},
                {"name": "Ajánlatadás", "profession": "Építésvezető", "duration_days": 5},
                {"name": "Szerződés megírása, kiküldése", "profession": "Építésvezető", "duration_days": 7},
                {"name": "Engedélyek, biztosítások", "profession": "Építésvezető", "duration_days": 10},
                {"name": "[AI] Szerződés sablonok, automatikus kitöltés", "profession": "", "duration_days": 2},
            ],
            "total_duration_days": 27,
        },
        {
            "name": "Tervezés",
            "tasks": [
                {"name": "Építészeti tervek", "profession": "Műszaki vezető", "duration_days": 15},
                {"name": "Statikai, gépészeti, elektromos tervek", "profession": "Műszaki vezető", "duration_days": 20},
                {"name": "Engedélyek beadása", "profession": "Építésvezető", "duration_days": 30},
                {"name": "Költségvetés, ütemterv", "profession": "Műszaki vezető", "duration_days": 10},
            ],
            "total_duration_days": 75,
        },
        {
            "name": "Anyag- és erőforrás-tervezés",
            "tasks": [
                {"name": "Anyagok listázása", "profession": "Műszaki vezető", "duration_days": 5},
                {"name": "Ajánlatkérések kiküldése", "profession": "Műszaki vezető", "duration_days": 7},
                {"name": "Beszállítók kiválasztása", "profession": "Műszaki vezető", "duration_days": 10},
                {"name": "Munkaerő és alvállalkozók ütemezése", "profession": "Műszaki vezető", "duration_days": 8},
                {"name": "[AI] Ajánlatkérés e-mailben + válaszok feldolgozása", "profession": "", "duration_days": 3},
            ],
            "total_duration_days": 33,
        },
        {
            "name": "Kivitelezés",
            "tasks": [
                {"name": "Alapozás, földmunka", "profession": "Kőműves", "duration_days": 25},
                {"name": "Falazat, szerkezetépítés", "profession": "Kőműves", "duration_days": 40},
                {"name": "Tető, nyílászárók", "profession": "Ács", "duration_days": 20},
                {"name": "Gépészet, villanyszerelés", "profession": "Víz-gáz-fűtésszerelő", "duration_days": 30},
                {"name": "Villanyszerelés", "profession": "Villanyszerelő", "duration_days": 25},
                {"name": "Vakolás, burkolás, festés", "profession": "Burkoló", "duration_days": 35},
                {"name": "[AI] Erőforrás ütemezés (időjárás + ember + eszköz)", "profession": "", "duration_days": 5},
            ],
            "total_duration_days": 180,
        },
        {
            "name": "Műszaki átadás",
            "tasks": [
                {"name": "Ellenőrzés, műszaki vezető", "profession": "Műszaki vezető", "duration_days": 7},
                {"name": "Hibajegyzék készítése", "profession": "Műszaki vezető", "duration_days": 5},
                {"name": "Használatbavételi engedély", "profession": "Építésvezető", "duration_days": 10},
                {"name": "[AI] Checklist + hibajegyzék automatikus generálás", "profession": "", "duration_days": 2},
            ],
            "total_duration_days": 24,
        },
        {
            "name": "Projekt lezárás",
            "tasks": [
                {"name": "Pénzügyi elszámolás", "profession": "Építésvezető", "duration_days": 5},
                {"name": "Kulcsátadás", "profession": "Építésvezető", "duration_days": 1},
                {"name": "Garanciális időszak indul", "profession": "Műszaki vezető", "duration_days": 1},
            ],
            "total_duration_days": 7,
        },
    ]


def update_phase_durations(phases):
    """Update total duration for each phase based on task durations"""
    for phase in phases:
        if "tasks" in phase:
            total_duration = sum(task.get("duration_days", 1) for task in phase["tasks"])
            phase["total_duration_days"] = total_duration
    return phases


def calculate_total_project_duration(phases):
    """Calculate total duration for entire project"""
    total_duration = 0
    for phase in phases:
        if "tasks" in phase:
            phase_duration = sum(task.get("duration_days", 1) for task in phase["tasks"])
            total_duration += phase_duration
    return total_duration


def ensure_base_session_state(st):
    if "resources" not in st.session_state:
        st.session_state.resources = get_default_resources()
    if "profession_types" not in st.session_state:
        st.session_state.profession_types = get_default_profession_types()
    if "project_types" not in st.session_state or not st.session_state.project_types:
        st.session_state.project_types = get_default_project_types()
    if "projects" not in st.session_state:
        st.session_state.projects = []
        seed_projects_if_empty(st)
    if "selected_project_index" not in st.session_state:
        st.session_state.selected_project_index = None
    if "selected_project_type_index" not in st.session_state:
        st.session_state.selected_project_type_index = None


def seed_projects_if_empty(st):
    member_names = [r.get("Név", "") for r in st.session_state.resources if r.get("Név")]
    phases = get_default_phases()
    phases_checked_template = [[False for _ in phase["tasks"]] for phase in phases]
    type_names = [pt.get("Név", "") for pt in st.session_state.project_types if pt.get("Név")]
    seed_type = random.choice(type_names) if type_names else ""
    st.session_state.projects.append({
        "name": "Alap projekt",
        "start": "2025-01-01",
        "end": "2025-12-31",
        "status": "Folyamatban",
        "members": member_names[:2],
        "locations": ["Győr"],
        "progress": 25,
        "phases_checked": phases_checked_template,
        "type": seed_type,
    })
    cities = ["Győr", "Budapest", "Debrecen", "Szeged", "Pécs", "Miskolc", "Veszprém"]
    statuses = ["Tervezés alatt", "Folyamatban", "Késésben", "Lezárt"]
    for i in range(1, 26):
        start_month = (i % 12) + 1
        end_month = ((i + 5) % 12) + 1
        city = cities[i % len(cities)]
        status = statuses[i % len(statuses)]
        seed_type_i = random.choice(type_names) if type_names else ""
        st.session_state.projects.append({
            "name": f"Családi ház {i}",
            "start": f"2025-{start_month:02d}-01",
            "end": f"2025-{end_month:02d}-28",
            "status": status,
            "members": member_names[:2],
            "locations": [city],
            "progress": 100 if status == "Lezárt" else (i * 7) % 100,
            "phases_checked": [[False for _ in phase["tasks"]] for phase in phases],
            "type": seed_type_i,
        })


