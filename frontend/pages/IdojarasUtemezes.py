import streamlit as st
import requests
from datetime import date, timedelta
from default_data import ensure_base_session_state

st.set_page_config(page_title="Időjárás alapú ütemezés – ÉpítAI", layout="wide")

st.title("🌤️ Időjárás alapú ütemezés")

st.write("Heti előrejelzés alapján megmutatjuk, mely projektek tudnak haladni.")


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
        rows.append({
            "Projekt": proj.get("name", f"Projekt {idx+1}"),
            "Helyszín": "-",
            "Összegzés": "Helyszín nincs megadva",
            "Haladhat": False,
        })
        continue

    coords = geocode_location(locs[0])
    if not coords:
        rows.append({
            "Projekt": proj.get("name", f"Projekt {idx+1}"),
            "Helyszín": locs[0],
            "Összegzés": "Helyszín nem geokódolható",
            "Haladhat": False,
        })
        continue

    weather = fetch_weekly_weather(coords[0], coords[1], start_day, end_day)
    if not weather or "daily" not in weather:
        rows.append({
            "Projekt": proj.get("name", f"Projekt {idx+1}"),
            "Helyszín": locs[0],
            "Összegzés": "Időjárási adatok nem elérhetők",
            "Haladhat": False,
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

    rows.append({
        "Projekt": proj.get("name", f"Projekt {idx+1}"),
        "Helyszín": locs[0],
        "Összegzés": summary,
        "Haladhat": can_progress,
    })


ok, risk = st.columns(2)
with ok:
    st.subheader("✅ Haladhat a héten")
    ok_rows = [r for r in rows if r["Haladhat"]]
    if ok_rows:
        st.table([{k: v for k, v in r.items() if k != "Haladhat"} for r in ok_rows])
    else:
        st.info("Nincs megfelelő projekt az időszakban.")

with risk:
    st.subheader("⚠️ Kockázatos / Nem javasolt")
    bad_rows = [r for r in rows if not r["Haladhat"]]
    if bad_rows:
        st.table([{k: v for k, v in r.items() if k != "Haladhat"} for r in bad_rows])
    else:
        st.info("Nincs kockázatos projekt az időszakban.")


