import streamlit as st

st.set_page_config(page_title="Resources – ÉpítAI", layout="wide")

st.title("🛠️ Erőforrások")

st.write("Itt tudod kezelni az alkalmazottakat és az alvállalkozókat.")

# Initialize session resource list
if "resources" not in st.session_state:
    st.session_state.resources = [
        {"Típus": "Alkalmazott", "Név": "Kiss János", "Pozíció": "Kőműves"},
        {"Típus": "Alvállalkozó", "Név": "Acél Kft.", "Pozíció": "Vasszerkezetek"},
        {"Típus": "Beszállító", "Név": "ÉpAnyag Zrt.", "Pozíció": "Beton, tégla"},
        {"Típus": "Beszállító", "Név": "FaTrade Kft.", "Pozíció": "Faanyagok"},
        {"Típus": "Beszállító", "Név": "VillTech Bt.", "Pozíció": "Villanyszerelési anyagok"},
        {"Típus": "Beszállító", "Név": "GépGURU Kft.", "Pozíció": "Gépek, bérlés"},
    ]

with st.expander("➕ Új alkalmazott"):
    emp_name = st.text_input("Név", key="emp_name")
    emp_role = st.text_input("Pozíció", key="emp_role")
    if st.button("Hozzáadás", key="add_employee"):
        if emp_name:
            st.session_state.resources.append({"Típus": "Alkalmazott", "Név": emp_name, "Pozíció": emp_role or "-"})
            st.success(f"Alkalmazott hozzáadva: {emp_name}")
            st.rerun()

with st.expander("➕ Új alvállalkozó"):
    comp_name = st.text_input("Cég neve", key="comp_name")
    comp_role = st.text_input("Elérhetőség", key="comp_role")
    if st.button("Hozzáadás", key="add_contractor"):
        if comp_name:
            st.session_state.resources.append({"Típus": "Alvállalkozó", "Név": comp_name, "Pozíció": comp_role or "-"})
            st.success(f"Alvállalkozó hozzáadva: {comp_name}")
            st.rerun()

with st.expander("➕ Új beszállító"):
    sup_name = st.text_input("Cég neve", key="sup_name")
    sup_scope = st.text_input("Termék / szakterület", key="sup_scope")
    if st.button("Hozzáadás", key="add_supplier"):
        if sup_name:
            st.session_state.resources.append({"Típus": "Beszállító", "Név": sup_name, "Pozíció": sup_scope or "-"})
            st.success(f"Beszállító hozzáadva: {sup_name}")
            st.rerun()


st.write("### Aktuális erőforrások")
st.table(st.session_state.resources)