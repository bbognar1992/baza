import random
import secrets
import string
from datetime import datetime, timedelta


def generate_project_id():
    """Generate a unique, long project ID for shareable URLs"""
    # Generate a 32-character random string with letters and numbers
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def get_default_resources():
    return [
        # Kőművesek
        {
            "Típus": "Alkalmazott", "Név": "Kiss János", "Pozíció": "Kőműves",
            "Telefonszám": "+36 20 123 4567", "E-mail": "kiss.janos@epitai.hu",
            "Cím": "Győr, Széchenyi u. 12.", "Készségek": "Falazat, betonozás, vakolás, csempe ragasztás",
            "Órabér": 3500, "Elérhetőség": "Elérhető", "Tapasztalat": 8
        },
        {
            "Típus": "Alkalmazott", "Név": "Nagy Péter", "Pozíció": "Kőműves",
            "Telefonszám": "+36 30 234 5678", "E-mail": "nagy.peter@epitai.hu",
            "Cím": "Győr, Kossuth L. u. 45.", "Készségek": "Falazat, betonozás, vakolás",
            "Órabér": 3200, "Elérhetőség": "Elérhető", "Tapasztalat": 5
        },
        {
            "Típus": "Alkalmazott", "Név": "Szabó László", "Pozíció": "Kőműves",
            "Telefonszám": "+36 70 345 6789", "E-mail": "szabo.laszlo@epitai.hu",
            "Cím": "Győr, Bartók B. u. 78.", "Készségek": "Falazat, betonozás, vakolás, kőműves munkák",
            "Órabér": 3800, "Elérhetőség": "Elérhető", "Tapasztalat": 12
        },
        
        # Villanyszerelők
        {
            "Típus": "Alkalmazott", "Név": "Kovács István", "Pozíció": "Villanyszerelő",
            "Telefonszám": "+36 20 456 7890", "E-mail": "kovacs.istvan@epitai.hu",
            "Cím": "Győr, Rákóczi u. 23.", "Készségek": "Villanyszerelés, kapcsolók, csatlakozók, LED világítás",
            "Órabér": 4200, "Elérhetőség": "Elérhető", "Tapasztalat": 10
        },
        {
            "Típus": "Alkalmazott", "Név": "Tóth Gábor", "Pozíció": "Villanyszerelő",
            "Telefonszám": "+36 30 567 8901", "E-mail": "toth.gabor@epitai.hu",
            "Cím": "Győr, Petőfi S. u. 56.", "Készségek": "Villanyszerelés, elektromos hálózatok, biztonsági rendszerek",
            "Órabér": 4000, "Elérhetőség": "Elérhető", "Tapasztalat": 7
        },
        
        # Víz-gáz-fűtésszerelők
        {
            "Típus": "Alkalmazott", "Név": "Molnár Zoltán", "Pozíció": "Víz-gáz-fűtésszerelő",
            "Telefonszám": "+36 70 678 9012", "E-mail": "molnar.zoltan@epitai.hu",
            "Cím": "Győr, Deák F. u. 89.", "Készségek": "Vízvezetékek, fűtés, szellőztetés, gázszerelés",
            "Órabér": 4500, "Elérhetőség": "Elérhető", "Tapasztalat": 15
        },
        {
            "Típus": "Alkalmazott", "Név": "Horváth Ferenc", "Pozíció": "Víz-gáz-fűtésszerelő",
            "Telefonszám": "+36 20 789 0123", "E-mail": "horvath.ferenc@epitai.hu",
            "Cím": "Győr, Bajcsy-Zs. u. 34.", "Készségek": "Vízvezetékek, fűtés, szellőztetés, klíma telepítés",
            "Órabér": 4300, "Elérhetőség": "Elérhető", "Tapasztalat": 9
        },
        
        # Ácsok
        {
            "Típus": "Alkalmazott", "Név": "Varga József", "Pozíció": "Ács",
            "Telefonszám": "+36 30 890 1234", "E-mail": "varga.jozsef@epitai.hu",
            "Cím": "Győr, Szent István u. 67.", "Készségek": "Fa szerkezetek, tetőfedés, bádogos munkák",
            "Órabér": 4000, "Elérhetőség": "Elérhető", "Tapasztalat": 11
        },
        {
            "Típus": "Alkalmazott", "Név": "Farkas Sándor", "Pozíció": "Ács",
            "Telefonszám": "+36 70 901 2345", "E-mail": "farkas.sandor@epitai.hu",
            "Cím": "Győr, Városház u. 12.", "Készségek": "Fa szerkezetek, tetőfedés, ablak-ajtó szerelés",
            "Órabér": 3800, "Elérhetőség": "Elérhető", "Tapasztalat": 6
        },
        
        # Burkolók
        {
            "Típus": "Alkalmazott", "Név": "Balogh Tamás", "Pozíció": "Burkoló",
            "Telefonszám": "+36 20 012 3456", "E-mail": "balogh.tamas@epitai.hu",
            "Cím": "Győr, Széchenyi u. 45.", "Készségek": "Padló, falburkolatok, csempe, parketta",
            "Órabér": 3600, "Elérhetőség": "Elérhető", "Tapasztalat": 8
        },
        {
            "Típus": "Alkalmazott", "Név": "Papp András", "Pozíció": "Burkoló",
            "Telefonszám": "+36 30 123 4567", "E-mail": "papp.andras@epitai.hu",
            "Cím": "Győr, Kossuth L. u. 78.", "Készségek": "Padló, falburkolatok, mozaik, természetes kő",
            "Órabér": 3700, "Elérhetőség": "Elérhető", "Tapasztalat": 10
        },
        
        # Festők
        {
            "Típus": "Alkalmazott", "Név": "Lakatos Miklós", "Pozíció": "Festő",
            "Telefonszám": "+36 70 234 5678", "E-mail": "lakatos.miklos@epitai.hu",
            "Cím": "Győr, Bartók B. u. 23.", "Készségek": "Festés, tapétázás, dekoratív festés, szigetelés",
            "Órabér": 3000, "Elérhetőség": "Elérhető", "Tapasztalat": 7
        },
        {
            "Típus": "Alkalmazott", "Név": "Takács Róbert", "Pozíció": "Festő",
            "Telefonszám": "+36 20 345 6789", "E-mail": "takacs.robert@epitai.hu",
            "Cím": "Győr, Rákóczi u. 56.", "Készségek": "Festés, tapétázás, textúrázás, szigetelés",
            "Órabér": 3100, "Elérhetőség": "Elérhető", "Tapasztalat": 5
        },
        
        # Műszaki vezetők
        {
            "Típus": "Alkalmazott", "Név": "Kovácsné Anna", "Pozíció": "Műszaki vezető",
            "Telefonszám": "+36 30 456 7890", "E-mail": "kovacsne.anna@epitai.hu",
            "Cím": "Győr, Petőfi S. u. 89.", "Készségek": "Projekt koordináció, minőségbiztosítás, CAD tervezés",
            "Órabér": 6000, "Elérhetőség": "Elérhető", "Tapasztalat": 12
        },
        {
            "Típus": "Alkalmazott", "Név": "Nagy Béla", "Pozíció": "Műszaki vezető",
            "Telefonszám": "+36 70 567 8901", "E-mail": "nagy.bela@epitai.hu",
            "Cím": "Győr, Deák F. u. 34.", "Készségek": "Projekt koordináció, minőségbiztosítás, statika",
            "Órabér": 6200, "Elérhetőség": "Elérhető", "Tapasztalat": 15
        },
        
        # Építésvezetők
        {
            "Típus": "Alkalmazott", "Név": "Szűcs Károly", "Pozíció": "Építésvezető",
            "Telefonszám": "+36 20 678 9012", "E-mail": "szucs.karoly@epitai.hu",
            "Cím": "Győr, Bajcsy-Zs. u. 67.", "Készségek": "Teljes építkezés irányítása, ügyfélkapcsolatok, engedélyek",
            "Órabér": 8000, "Elérhetőség": "Elérhető", "Tapasztalat": 20
        },
        
        # Alvállalkozók
        {
            "Típus": "Alvállalkozó", "Név": "Acél Kft.", "Pozíció": "Vasszerkezetek",
            "Telefonszám": "+36 96 123 4567", "E-mail": "info@acelkft.hu",
            "Cím": "Győr, Ipari út 12.", "Készségek": "Vasszerkezetek, acél építmények, hegesztés",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 25
        },
        {
            "Típus": "Alvállalkozó", "Név": "FaMester Bt.", "Pozíció": "Fa szerkezetek",
            "Telefonszám": "+36 96 234 5678", "E-mail": "info@famester.hu",
            "Cím": "Győr, Faipari út 45.", "Készségek": "Fa szerkezetek, tetőfedés, belső burkolatok",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 18
        },
        {
            "Típus": "Alvállalkozó", "Név": "BurkolóPro Kft.", "Pozíció": "Burkolás",
            "Telefonszám": "+36 96 345 6789", "E-mail": "info@burkolopro.hu",
            "Cím": "Győr, Burkoló út 78.", "Készségek": "Burkolás, csempe, parketta, természetes kő",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 22
        },
        
        # Beszállítók
        {
            "Típus": "Beszállító", "Név": "ÉpAnyag Zrt.", "Pozíció": "Beton, tégla",
            "Telefonszám": "+36 96 456 7890", "E-mail": "info@epanyag.hu",
            "Cím": "Győr, Építőanyag út 23.", "Készségek": "Beton, tégla, cement, homok, kavics",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 30
        },
        {
            "Típus": "Beszállító", "Név": "FaTrade Kft.", "Pozíció": "Faanyagok",
            "Telefonszám": "+36 96 567 8901", "E-mail": "info@fatrade.hu",
            "Cím": "Győr, Faanyag út 56.", "Készségek": "Faanyagok, deszka, gerenda, parketta",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 20
        },
        {
            "Típus": "Beszállító", "Név": "VillTech Bt.", "Pozíció": "Villanyszerelési anyagok",
            "Telefonszám": "+36 96 678 9012", "E-mail": "info@villtech.hu",
            "Cím": "Győr, Villany út 89.", "Készségek": "Villanyszerelési anyagok, kábelek, kapcsolók",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 15
        },
        {
            "Típus": "Beszállító", "Név": "GépGURU Kft.", "Pozíció": "Gépek, bérlés",
            "Telefonszám": "+36 96 789 0123", "E-mail": "info@gepguru.hu",
            "Cím": "Győr, Gép út 12.", "Készségek": "Gépek, bérlés, daruk, kotrógépek, betonkeverők",
            "Órabér": 0, "Elérhetőség": "Elérhető", "Tapasztalat": 12
        },
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
                {"name": "Ügyfél igényfelmérés", "profession": "Építésvezető", "duration_days": 3, "required_people": 1},
                {"name": "Ajánlatadás", "profession": "Építésvezető", "duration_days": 5, "required_people": 1},
                {"name": "Szerződés megírása, kiküldése", "profession": "Építésvezető", "duration_days": 7, "required_people": 1},
                {"name": "Engedélyek, biztosítások", "profession": "Építésvezető", "duration_days": 10, "required_people": 1},
                {"name": "[AI] Szerződés sablonok, automatikus kitöltés", "profession": "", "duration_days": 2, "required_people": 1},
            ],
            "total_duration_days": 27,
        },
        {
            "name": "Tervezés",
            "tasks": [
                {"name": "Építészeti tervek", "profession": "Műszaki vezető", "duration_days": 15, "required_people": 2},
                {"name": "Statikai, gépészeti, elektromos tervek", "profession": "Műszaki vezető", "duration_days": 20, "required_people": 3},
                {"name": "Engedélyek beadása", "profession": "Építésvezető", "duration_days": 30, "required_people": 1},
                {"name": "Költségvetés, ütemterv", "profession": "Műszaki vezető", "duration_days": 10, "required_people": 2},
            ],
            "total_duration_days": 75,
        },
        {
            "name": "Anyag- és erőforrás-tervezés",
            "tasks": [
                {"name": "Anyagok listázása", "profession": "Műszaki vezető", "duration_days": 5, "required_people": 1},
                {"name": "Ajánlatkérések kiküldése", "profession": "Műszaki vezető", "duration_days": 7, "required_people": 2},
                {"name": "Beszállítók kiválasztása", "profession": "Műszaki vezető", "duration_days": 10, "required_people": 2},
                {"name": "Munkaerő és alvállalkozók ütemezése", "profession": "Műszaki vezető", "duration_days": 8, "required_people": 1},
                {"name": "[AI] Ajánlatkérés e-mailben + válaszok feldolgozása", "profession": "", "duration_days": 3, "required_people": 1},
            ],
            "total_duration_days": 33,
        },
        {
            "name": "Kivitelezés",
            "tasks": [
                {"name": "Alapozás, földmunka", "profession": "Kőműves", "duration_days": 25, "required_people": 4},
                {"name": "Falazat, szerkezetépítés", "profession": "Kőműves", "duration_days": 40, "required_people": 6},
                {"name": "Tető, nyílászárók", "profession": "Ács", "duration_days": 20, "required_people": 3},
                {"name": "Gépészet, villanyszerelés", "profession": "Víz-gáz-fűtésszerelő", "duration_days": 30, "required_people": 4},
                {"name": "Villanyszerelés", "profession": "Villanyszerelő", "duration_days": 25, "required_people": 3},
                {"name": "Vakolás, burkolás, festés", "profession": "Burkoló", "duration_days": 35, "required_people": 5},
                {"name": "[AI] Erőforrás ütemezés (időjárás + ember + eszköz)", "profession": "", "duration_days": 5, "required_people": 1},
            ],
            "total_duration_days": 180,
        },
        {
            "name": "Műszaki átadás",
            "tasks": [
                {"name": "Ellenőrzés, műszaki vezető", "profession": "Műszaki vezető", "duration_days": 7, "required_people": 2},
                {"name": "Hibajegyzék készítése", "profession": "Műszaki vezető", "duration_days": 5, "required_people": 1},
                {"name": "Használatbavételi engedély", "profession": "Építésvezető", "duration_days": 10, "required_people": 1},
                {"name": "[AI] Checklist + hibajegyzék automatikus generálás", "profession": "", "duration_days": 2, "required_people": 1},
            ],
            "total_duration_days": 24,
        },
        {
            "name": "Projekt lezárás",
            "tasks": [
                {"name": "Pénzügyi elszámolás", "profession": "Építésvezető", "duration_days": 5, "required_people": 1},
                {"name": "Kulcsátadás", "profession": "Építésvezető", "duration_days": 1, "required_people": 1},
                {"name": "Garanciális időszak indul", "profession": "Műszaki vezető", "duration_days": 1, "required_people": 1},
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
        "project_id": generate_project_id(),
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


