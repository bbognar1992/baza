import streamlit as st
from datetime import date
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="Anyagár ajánlatkérés AI-val – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("🧠 Anyagár ajánlatkérés AI-val")

st.write("Készíts gyorsan, egységes formátumú ajánlatkérő e-maileket a beszállítóknak.")

suppliers = [r for r in st.session_state.resources if r.get("Típus") == "Beszállító"]
supplier_names = [s.get("Név", "") for s in suppliers if s.get("Név")]
project_names = [p.get("name", "") for p in st.session_state.projects if p.get("name")]

with st.form("rfq_form"):
    col1, col2 = st.columns(2)
    with col1:
        project = st.selectbox("Projekt", options=["(nincs kiválasztva)"] + project_names)
        need_by = st.date_input("Kért szállítási határidő", value=date.today())
    with col2:
        selected_suppliers = st.multiselect("Címzettek (beszállítók)", options=supplier_names, default=supplier_names[:2])

    materials = st.text_area(
        "Anyaglista (egy sor = tétel)",
        value="""Beton C25/30, 20 m³\nTégla 30 cm, 1200 db\nVasalás Ø12, 600 m\nSzigetelőanyag EPS 10 cm, 200 m²""",
        height=140,
    )
    notes = st.text_area("Megjegyzés (opcionális)", value="Kérjük, az ár tartalmazza a szállítási költséget is.")

    submitted = st.form_submit_button("Ajánlatkérés generálása")

if submitted:
    if not selected_suppliers:
        st.warning("Válassz ki legalább egy beszállítót.")
    else:
        st.success("Ajánlatkérő tervezetek elkészítve. Másold a megfelelő e-mail kliensbe.")
        line_items = [ln.strip() for ln in (materials or "").split("\n") if ln.strip()]
        line_block = "\n".join(f"- {ln}" for ln in line_items) if line_items else "- (nincs tétel megadva)"
        proj_display = project if project and project != "(nincs kiválasztva)" else "(projekt megnevezése)"

        for i, name in enumerate(selected_suppliers):
            with st.expander(f"✉️ E-mail terv – {name}", expanded=False):
                subject = f"Ajánlatkérés – {proj_display} – anyagár"
                body = (
                    f"Tisztelt {name}!\n\n"
                    f"Az alábbi anyagokra kérnénk árajánlatot a {proj_display} projekthez:\n\n"
                    f"{line_block}\n\n"
                    f"Kért szállítási határidő: {need_by.isoformat()}\n"
                    f"Kérjük, az ajánlat tartalmazza a szállítási és esetleges rakodási költségeket is.\n"
                    f"{notes.strip()}\n\n"
                    f"Köszönjük együttműködésüket!\n"
                    f"Üdvözlettel,\n"
                    f"ÉpítAI rendszer"
                )
                st.text_input("Tárgy", value=subject, key=f"rfq_subject_{i}_{name}")
                st.text_area("Törzs", value=body, height=220, key=f"rfq_body_{i}_{name}")


