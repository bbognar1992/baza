import streamlit as st
import requests

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

def render_locations_tab(project):
    """Render the locations tab for project details."""
    st.subheader("🗺️ Helyszínek")
    locations = project.get("locations", [])
    if locations:
        st.write(", ".join(locations))
        
        # Map for locations
        points = []
        for loc in locations:
            coords = geocode_location(loc)
            if coords:
                points.append({"lat": coords[0], "lon": coords[1]})
        
        if points:
            st.map(points, zoom=12)
        else:
            st.info("Nem sikerült megjeleníteni a térképet a megadott helyszínekhez.")
    else:
        st.info("Nincsenek megadva helyszínek.")
