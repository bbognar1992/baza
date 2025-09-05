import streamlit as st
from default_data import ensure_base_session_state

st.set_page_config(page_title="Resources – ÉpítAI", layout="wide")

st.title("🛠️ Erőforrások")

st.write("Itt tudod kezelni az alkalmazottakat és az alvállalkozókat.")

ensure_base_session_state(st)

with st.expander("➕ Új erőforrás"):
    resource_type = st.selectbox(
        "Típus",
        ["Alkalmazott", "Alvállalkozó", "Beszállító"],
        key="resource_type"
    )
    
    name_label = "Név" if resource_type == "Alkalmazott" else "Cég neve"
    name = st.text_input(name_label, key="resource_name")
    
    if resource_type == "Alkalmazott":
        detail_label = "Pozíció"
    elif resource_type == "Alvállalkozó":
        detail_label = "Elérhetőség"
    else:  # Beszállító
        detail_label = "Termék / szakterület"
    
    detail = st.text_input(detail_label, key="resource_detail")
    
    if st.button("Hozzáadás", key="add_resource"):
        if name:
            st.session_state.resources.append({
                "Típus": resource_type, 
                "Név": name, 
                "Pozíció": detail or "-"
            })
            st.success(f"{resource_type} hozzáadva: {name}")
            st.rerun()


st.write("### Aktuális erőforrások")

# Split resources by type
emps = [r for r in st.session_state.resources if r.get("Típus") == "Alkalmazott"]
subs = [r for r in st.session_state.resources if r.get("Típus") == "Alvállalkozó"]
sups = [r for r in st.session_state.resources if r.get("Típus") == "Beszállító"]

tab1, tab2, tab3 = st.tabs([
    f"Alkalmazott ({len(emps)})",
    f"Alvállalkozó ({len(subs)})",
    f"Beszállító ({len(sups)})",
])

with tab1:
    if emps:
        st.table(emps)
    else:
        st.info("Nincs alkalmazott.")

with tab2:
    if subs:
        st.table(subs)
    else:
        st.info("Nincs alvállalkozó.")

with tab3:
    if sups:
        st.table(sups)
    else:
        st.info("Nincs beszállító.")