import streamlit as st

st.set_page_config(page_title="Projekt típusok – ÉpítAI", layout="wide")

st.title("🏷️ Projekt típusok")
st.write("Hozz létre és kezeld a projekt típusokat.")

# Init default types
if "project_types" not in st.session_state:
    st.session_state.project_types = [
        {"Név": "Földszintes ház", "Leírás": "Egyszintes családi ház"},
        {"Név": "Tetőteres ház", "Leírás": "Beépített tetőterű családi ház"},
    ]

with st.expander("➕ Új típus hozzáadása", expanded=False):
    t_name = st.text_input("Típus neve", key="ptype_name")
    t_desc = st.text_input("Leírás", key="ptype_desc")
    if st.button("Hozzáadás", key="ptype_add"):
        if t_name:
            # prevent duplicate by name
            if any(pt.get("Név") == t_name for pt in st.session_state.project_types):
                st.warning("Ilyen nevű típus már létezik.")
            else:
                st.session_state.project_types.append({"Név": t_name, "Leírás": t_desc or "-"})
                st.success(f"Típus hozzáadva: {t_name}")
                st.rerun()

st.write("### Elérhető típusok")
if st.session_state.project_types:
    # Simple table with optional remove buttons
    for idx, ptype in enumerate(st.session_state.project_types):
        cols = st.columns([3, 6, 1])
        cols[0].markdown(f"**{ptype.get('Név','-')}**")
        cols[1].write(ptype.get("Leírás", "-"))
        if cols[2].button("❌", key=f"del_ptype_{idx}"):
            st.session_state.project_types.pop(idx)
            st.rerun()
else:
    st.info("Nincs projekt típus. Adj hozzá fentebb.")


