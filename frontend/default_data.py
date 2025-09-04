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
                {"name": "Ügyfél igényfelmérés", "profession": "Építésvezető"},
                {"name": "Ajánlatadás", "profession": "Építésvezető"},
                {"name": "Szerződés megírása, kiküldése", "profession": "Építésvezető"},
                {"name": "Engedélyek, biztosítások", "profession": "Építésvezető"},
                {"name": "[AI] Szerződés sablonok, automatikus kitöltés", "profession": ""},
            ],
        },
        {
            "name": "Tervezés",
            "tasks": [
                {"name": "Építészeti tervek", "profession": "Műszaki vezető"},
                {"name": "Statikai, gépészeti, elektromos tervek", "profession": "Műszaki vezető"},
                {"name": "Engedélyek beadása", "profession": "Építésvezető"},
                {"name": "Költségvetés, ütemterv", "profession": "Műszaki vezető"},
            ],
        },
        {
            "name": "Anyag- és erőforrás-tervezés",
            "tasks": [
                {"name": "Anyagok listázása", "profession": "Műszaki vezető"},
                {"name": "Ajánlatkérések kiküldése", "profession": "Műszaki vezető"},
                {"name": "Beszállítók kiválasztása", "profession": "Műszaki vezető"},
                {"name": "Munkaerő és alvállalkozók ütemezése", "profession": "Műszaki vezető"},
                {"name": "[AI] Ajánlatkérés e-mailben + válaszok feldolgozása", "profession": ""},
            ],
        },
        {
            "name": "Kivitelezés",
            "tasks": [
                {"name": "Alapozás, földmunka", "profession": "Kőműves"},
                {"name": "Falazat, szerkezetépítés", "profession": "Kőműves"},
                {"name": "Tető, nyílászárók", "profession": "Ács"},
                {"name": "Gépészet, villanyszerelés", "profession": "Víz-gáz-fűtésszerelő"},
                {"name": "Villanyszerelés", "profession": "Villanyszerelő"},
                {"name": "Vakolás, burkolás, festés", "profession": "Burkoló"},
                {"name": "[AI] Erőforrás ütemezés (időjárás + ember + eszköz)", "profession": ""},
            ],
        },
        {
            "name": "Műszaki átadás",
            "tasks": [
                {"name": "Ellenőrzés, műszaki vezető", "profession": "Műszaki vezető"},
                {"name": "Hibajegyzék készítése", "profession": "Műszaki vezető"},
                {"name": "Használatbavételi engedély", "profession": "Építésvezető"},
                {"name": "[AI] Checklist + hibajegyzék automatikus generálás", "profession": ""},
            ],
        },
        {
            "name": "Projekt lezárás",
            "tasks": [
                {"name": "Pénzügyi elszámolás", "profession": "Építésvezető"},
                {"name": "Kulcsátadás", "profession": "Építésvezető"},
                {"name": "Garanciális időszak indul", "profession": "Műszaki vezető"},
            ],
        },
    ]


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


