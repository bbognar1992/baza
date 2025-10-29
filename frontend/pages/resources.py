import streamlit as st
from default_data import ensure_base_session_state
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="Resources – Pontum", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("🛠️ Erőforrások")

st.write("Itt tudod kezelni az alkalmazottakat és az alvállalkozókat.")

with st.expander("➕ Új erőforrás"):
    resource_type = st.selectbox(
        "Típus",
        ["Alkalmazott", "Alvállalkozó", "Beszállító"],
        key="resource_type"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        name_label = "Név" if resource_type == "Alkalmazott" else "Cég neve"
        name = st.text_input(name_label, key="resource_name")
        
        if resource_type == "Alkalmazott":
            detail_label = "Pozíció"
        elif resource_type == "Alvállalkozó":
            detail_label = "Elérhetőség"
        else:  # Beszállító
            detail_label = "Termék / szakterület"
        
        detail = st.text_input(detail_label, key="resource_detail")
        
        phone = st.text_input("Telefonszám", key="resource_phone")
        email = st.text_input("E-mail", key="resource_email")
    
    with col2:
        address = st.text_area("Cím", key="resource_address")
        skills = st.text_area("Készségek / Szakterületek", key="resource_skills")
        
        if resource_type == "Alkalmazott":
            hourly_rate = st.number_input("Órabér (Ft)", min_value=0.0, key="resource_hourly_rate")
            experience = st.number_input("Tapasztalat (év)", min_value=0, max_value=50, key="resource_experience")
        else:
            hourly_rate = 0
            experience = 0
        
        availability = st.selectbox(
            "Elérhetőség",
            ["Elérhető", "Foglalt", "Szabadságon", "Betegszabadság"],
            key="resource_availability"
        )
    
    if st.button("Hozzáadás", key="add_resource"):
        if name:
            new_resource = {
                "Típus": resource_type, 
                "Név": name, 
                "Pozíció": detail or "-",
                "Telefonszám": phone or "",
                "E-mail": email or "",
                "Cím": address or "",
                "Készségek": skills or "",
                "Órabér": hourly_rate,
                "Elérhetőség": availability,
                "Tapasztalat": experience
            }
            st.session_state.resources.append(new_resource)
            st.success(f"{resource_type} hozzáadva: {name}")
            st.rerun()
        else:
            st.error("A név megadása kötelező!")


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

def render_resource_list(resources_subset, subset_key_prefix=""):
    if not resources_subset:
        st.info("Nincs megjeleníthető erőforrás.")
        return
    
    header = st.columns([3, 2, 2, 2, 2, 2])
    header[0].markdown("**Név**")
    header[1].markdown("**Pozíció**")
    header[2].markdown("**Elérhetőség**")
    header[3].markdown("**Tapasztalat**")
    header[4].markdown("**Órabér**")
    header[5].markdown("**Művelet**")
    
    for idx, resource in enumerate(resources_subset):
        cols = st.columns([3, 2, 2, 2, 2, 2])
        
        # Add icon based on resource type
        icon = "👤" if resource.get("Típus") == "Alkalmazott" else "🏢" if resource.get("Típus") == "Alvállalkozó" else "📦"
        cols[0].markdown(f"**{icon} {resource.get('Név', 'Névtelen')}**")
        cols[1].write(resource.get('Pozíció', '-'))
        cols[2].write(resource.get('Elérhetőség', 'Elérhető'))
        
        experience = resource.get('Tapasztalat', 0)
        cols[3].write(f"{experience} év" if experience > 0 else "-")
        
        hourly_rate = resource.get('Órabér', 0)
        cols[4].write(f"{hourly_rate:,.0f} Ft" if hourly_rate > 0 else "-")
        
        # Find original index to open details
        try:
            original_idx = st.session_state.resources.index(resource)
        except ValueError:
            original_idx = None
        
        if cols[5].button("Megnyitás", key=f"open_{subset_key_prefix}{idx}"):
            if original_idx is not None:
                st.session_state.selected_resource_index = original_idx
                st.switch_page("pages/resource_details.py")

with tab1:
    render_resource_list(emps, "emp_")

with tab2:
    render_resource_list(subs, "sub_")

with tab3:
    render_resource_list(sups, "sup_")