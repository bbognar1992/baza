import streamlit as st
from default_data import ensure_base_session_state
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Resource Details – ÉpítAI", layout="wide")

ensure_base_session_state(st)

st.title("👤 Erőforrás Részletek")

# Check if a resource is selected
if "selected_resource_index" not in st.session_state or st.session_state.selected_resource_index is None:
    st.warning("Nincs kiválasztott erőforrás. Kérjük, válassz ki egy erőforrást a fő Erőforrások oldalról.")
    st.info("💡 Tipp: Menj vissza az Erőforrások oldalra és kattints egy erőforrás nevére a részletek megtekintéséhez.")
    
    if st.button("🔙 Vissza az Erőforrások oldalra"):
        st.switch_page("pages/Resources.py")
else:
    # Get the selected resource
    resource_index = st.session_state.selected_resource_index
    if resource_index < len(st.session_state.resources):
        resource = st.session_state.resources[resource_index]
        
        # Header with resource info
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📋 {resource.get('Név', 'Névtelen')}")
            st.caption(f"Típus: {resource.get('Típus', 'Ismeretlen')}")
        
        with col2:
            if st.button("✏️ Szerkesztés", key="edit_resource"):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col3:
            if st.button("🔙 Vissza", key="back_to_resources"):
                st.session_state.selected_resource_index = None
                st.switch_page("pages/Resources.py")
        
        # Check if in edit mode
        if st.session_state.get("edit_mode", False):
            st.markdown("---")
            st.subheader("✏️ Erőforrás szerkesztése")
            
            with st.form("edit_resource_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_type = st.selectbox(
                        "Típus",
                        ["Alkalmazott", "Alvállalkozó", "Beszállító"],
                        index=["Alkalmazott", "Alvállalkozó", "Beszállító"].index(resource.get("Típus", "Alkalmazott")),
                        key="edit_type"
                    )
                    
                    name_label = "Név" if new_type == "Alkalmazott" else "Cég neve"
                    new_name = st.text_input(
                        name_label, 
                        value=resource.get("Név", ""),
                        key="edit_name"
                    )
                
                with col2:
                    if new_type == "Alkalmazott":
                        detail_label = "Pozíció"
                    elif new_type == "Alvállalkozó":
                        detail_label = "Elérhetőség"
                    else:  # Beszállító
                        detail_label = "Termék / szakterület"
                    
                    new_detail = st.text_input(
                        detail_label,
                        value=resource.get("Pozíció", ""),
                        key="edit_detail"
                    )
                
                # Additional fields for enhanced details
                st.subheader("📞 Kapcsolattartási adatok")
                col1, col2 = st.columns(2)
                
                with col1:
                    phone = st.text_input(
                        "Telefonszám",
                        value=resource.get("Telefonszám", ""),
                        key="edit_phone"
                    )
                    email = st.text_input(
                        "E-mail",
                        value=resource.get("E-mail", ""),
                        key="edit_email"
                    )
                
                with col2:
                    address = st.text_area(
                        "Cím",
                        value=resource.get("Cím", ""),
                        key="edit_address"
                    )
                
                # Skills and availability
                st.subheader("🛠️ Készségek és elérhetőség")
                col1, col2 = st.columns(2)
                
                with col1:
                    skills = st.text_area(
                        "Készségek / Szakterületek",
                        value=resource.get("Készségek", ""),
                        key="edit_skills"
                    )
                    hourly_rate = st.number_input(
                        "Órabér (Ft)",
                        value=float(resource.get("Órabér", 0)),
                        min_value=0.0,
                        key="edit_hourly_rate"
                    )
                
                with col2:
                    availability = st.selectbox(
                        "Elérhetőség",
                        ["Elérhető", "Foglalt", "Szabadságon", "Betegszabadság"],
                        index=["Elérhető", "Foglalt", "Szabadságon", "Betegszabadság"].index(resource.get("Elérhetőség", "Elérhető")),
                        key="edit_availability"
                    )
                    
                    experience_years = st.number_input(
                        "Tapasztalat (év)",
                        value=int(resource.get("Tapasztalat", 0)),
                        min_value=0,
                        max_value=50,
                        key="edit_experience"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Mentés", type="primary"):
                        if new_name:
                            # Update the resource
                            st.session_state.resources[resource_index] = {
                                "Típus": new_type,
                                "Név": new_name,
                                "Pozíció": new_detail,
                                "Telefonszám": phone,
                                "E-mail": email,
                                "Cím": address,
                                "Készségek": skills,
                                "Órabér": hourly_rate,
                                "Elérhetőség": availability,
                                "Tapasztalat": experience_years
                            }
                            st.success("Erőforrás sikeresen frissítve!")
                            st.session_state.edit_mode = False
                            st.rerun()
                        else:
                            st.error("A név megadása kötelező!")
                
                with col2:
                    if st.form_submit_button("❌ Mégse"):
                        st.session_state.edit_mode = False
                        st.rerun()
        else:
            # Display mode
            st.markdown("---")
            
            # Main info cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Típus",
                    value=resource.get("Típus", "Ismeretlen")
                )
            
            with col2:
                st.metric(
                    label="Elérhetőség",
                    value=resource.get("Elérhetőség", "Elérhető")
                )
            
            with col3:
                experience = resource.get("Tapasztalat", 0)
                st.metric(
                    label="Tapasztalat",
                    value=f"{experience} év"
                )
            
            with col4:
                hourly_rate = resource.get("Órabér", 0)
                st.metric(
                    label="Órabér",
                    value=f"{hourly_rate:,.0f} Ft" if hourly_rate > 0 else "Nincs megadva"
                )
            
            # Detailed information tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Alapadatok",
                "📞 Kapcsolat",
                "🛠️ Készségek",
                "📊 Projektek"
            ])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Személyes adatok")
                    st.write(f"**Név:** {resource.get('Név', 'Nincs megadva')}")
                    st.write(f"**Pozíció/Szakterület:** {resource.get('Pozíció', 'Nincs megadva')}")
                    st.write(f"**Típus:** {resource.get('Típus', 'Nincs megadva')}")
                    st.write(f"**Tapasztalat:** {resource.get('Tapasztalat', 0)} év")
                
                with col2:
                    st.subheader("Munkavégzés")
                    st.write(f"**Elérhetőség:** {resource.get('Elérhetőség', 'Elérhető')}")
                    st.write(f"**Órabér:** {resource.get('Órabér', 0):,.0f} Ft" if resource.get('Órabér', 0) > 0 else "**Órabér:** Nincs megadva")
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Kapcsolattartás")
                    phone = resource.get("Telefonszám", "")
                    email = resource.get("E-mail", "")
                    
                    if phone:
                        st.write(f"**Telefonszám:** {phone}")
                    else:
                        st.write("**Telefonszám:** Nincs megadva")
                    
                    if email:
                        st.write(f"**E-mail:** {email}")
                    else:
                        st.write("**E-mail:** Nincs megadva")
                
                with col2:
                    st.subheader("Cím")
                    address = resource.get("Cím", "")
                    if address:
                        st.write(f"**Cím:** {address}")
                    else:
                        st.write("**Cím:** Nincs megadva")
            
            with tab3:
                st.subheader("Készségek és szakterületek")
                skills = resource.get("Készségek", "")
                if skills:
                    st.write(skills)
                else:
                    st.info("Nincsenek megadva készségek.")
            
            with tab4:
                st.subheader("Projektelőzmények")
                
                # Find projects where this resource is involved
                involved_projects = []
                for project in st.session_state.projects:
                    if resource.get("Név") in project.get("members", []):
                        involved_projects.append(project)
                
                if involved_projects:
                    st.write(f"Ez az erőforrás **{len(involved_projects)}** projektben vesz részt:")
                    
                    for project in involved_projects:
                        with st.expander(f"📁 {project.get('name', 'Névtelen projekt')}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Státusz:** {project.get('status', 'Ismeretlen')}")
                                st.write(f"**Kezdés:** {project.get('start', 'Nincs megadva')}")
                                st.write(f"**Befejezés:** {project.get('end', 'Nincs megadva')}")
                            
                            with col2:
                                st.write(f"**Helyszín:** {', '.join(project.get('locations', []))}")
                                st.write(f"**Előrehaladás:** {project.get('progress', 0)}%")
                                st.write(f"**Típus:** {project.get('type', 'Nincs megadva')}")
                else:
                    st.info("Ez az erőforrás még nem vett részt egyetlen projektben sem.")
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️ Szerkesztés", key="edit_button"):
                    st.session_state.edit_mode = True
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Törlés", key="delete_button"):
                    st.session_state.show_delete_confirmation = True
                    st.rerun()
            
            with col3:
                if st.button("📋 Új projekthez hozzáadás", key="add_to_project"):
                    st.session_state.show_add_to_project = True
                    st.rerun()
            
            # Delete confirmation
            if st.session_state.get("show_delete_confirmation", False):
                st.warning("⚠️ Biztosan törölni szeretnéd ezt az erőforrást?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Igen, törlés", key="confirm_delete"):
                        del st.session_state.resources[resource_index]
                        st.session_state.selected_resource_index = None
                        st.session_state.show_delete_confirmation = False
                        st.success("Erőforrás sikeresen törölve!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Mégse", key="cancel_delete"):
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
            
            # Add to project dialog
            if st.session_state.get("show_add_to_project", False):
                st.subheader("📋 Erőforrás hozzáadása projekthez")
                
                # Get available projects
                available_projects = [p for p in st.session_state.projects if resource.get("Név") not in p.get("members", [])]
                
                if available_projects:
                    project_names = [p.get("name", "Névtelen projekt") for p in available_projects]
                    selected_project_name = st.selectbox("Válassz projektet:", project_names)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Hozzáadás", key="confirm_add_to_project"):
                            # Find the selected project and add the resource
                            for project in st.session_state.projects:
                                if project.get("name") == selected_project_name:
                                    if "members" not in project:
                                        project["members"] = []
                                    project["members"].append(resource.get("Név"))
                                    break
                            
                            st.success(f"Erőforrás hozzáadva a '{selected_project_name}' projekthez!")
                            st.session_state.show_add_to_project = False
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Mégse", key="cancel_add_to_project"):
                            st.session_state.show_add_to_project = False
                            st.rerun()
                else:
                    st.info("Nincs elérhető projekt, ahova hozzáadhatnád ezt az erőforrást.")
                    if st.button("❌ Bezárás", key="close_add_to_project"):
                        st.session_state.show_add_to_project = False
                        st.rerun()
    else:
        st.error("A kiválasztott erőforrás nem található.")
        st.session_state.selected_resource_index = None
        st.rerun()
