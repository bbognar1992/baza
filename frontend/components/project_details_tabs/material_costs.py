import streamlit as st

def render_material_costs_tab(project):
    """Render the material costs tab for project details."""
    st.subheader("🧱 Anyagköltségek")
    
    # Initialize material costs if not exists
    if "material_costs" not in project:
        project["material_costs"] = []
    
    # Add new material cost button
    if st.button("➕ Új anyag hozzáadása", key="add_material"):
        st.session_state.show_add_material = True
        st.rerun()
    
    # Add material form
    if st.session_state.get("show_add_material", False):
        st.markdown("---")
        st.subheader("Új anyag hozzáadása")
        
        with st.form("add_material_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                material_name = st.text_input("Anyag neve", key="new_material_name")
            
            with col2:
                material_category = st.selectbox(
                    "Kategória",
                    ["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"],
                    key="new_material_category"
                )
            
            with col3:
                material_quantity = st.number_input("Mennyiség", min_value=0.0, value=1.0, key="new_material_quantity")
            
            with col4:
                material_unit = st.selectbox(
                    "Mértékegység",
                    ["db", "m²", "m³", "kg", "t", "m", "l", "csomag"],
                    key="new_material_unit"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                material_unit_price = st.number_input("Egységár (Ft)", min_value=0, value=0, key="new_material_unit_price")
            
            with col2:
                material_supplier = st.text_input("Beszállító", key="new_material_supplier")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Hozzáadás", type="primary"):
                    if material_name and material_unit_price > 0:
                        total_price = material_quantity * material_unit_price
                        new_material = {
                            "name": material_name,
                            "category": material_category,
                            "quantity": material_quantity,
                            "unit": material_unit,
                            "unit_price": material_unit_price,
                            "total_price": total_price,
                            "supplier": material_supplier
                        }
                        project["material_costs"].append(new_material)
                        st.success(f"Anyag hozzáadva: {material_name}")
                        st.session_state.show_add_material = False
                        st.rerun()
                    else:
                        st.error("Az anyag neve és egységára megadása kötelező!")
            
            with col2:
                if st.form_submit_button("❌ Mégse"):
                    st.session_state.show_add_material = False
                    st.rerun()
    
    # Display material costs
    if project["material_costs"]:
        # Group materials by category
        categories = {}
        for material in project["material_costs"]:
            category = material.get("category", "Egyéb")
            if category not in categories:
                categories[category] = []
            categories[category].append(material)
        
        # Display materials by category
        for category, materials in categories.items():
            with st.expander(f"📦 {category} ({len(materials)} anyag)", expanded=True):
                # Create a table for materials in this category
                for i, material in enumerate(materials):
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{material['name']}**")
                        if material.get('supplier'):
                            st.caption(f"Beszállító: {material['supplier']}")
                    
                    with col2:
                        st.metric("Mennyiség", f"{material['quantity']} {material['unit']}")
                    
                    with col3:
                        st.metric("Egységár", f"{material['unit_price']:,} Ft")
                    
                    with col4:
                        st.metric("Összesen", f"{material['total_price']:,} Ft")
                    
                    with col5:
                        if st.button("✏️", key=f"edit_material_{i}", help="Szerkesztés"):
                            st.session_state.edit_material_index = i
                            st.rerun()
                    
                    with col6:
                        if st.button("🗑️", key=f"delete_material_{i}", help="Törlés"):
                            st.session_state.delete_material_index = i
                            st.rerun()
                    
                    st.divider()
        
        # Summary section
        st.markdown("---")
        st.subheader("📊 Összesítés")
        
        # Calculate totals
        total_materials = len(project["material_costs"])
        total_cost = sum(material["total_price"] for material in project["material_costs"])
        
        # Calculate by category
        category_totals = {}
        for material in project["material_costs"]:
            category = material.get("category", "Egyéb")
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += material["total_price"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📦 Összes anyag", f"{total_materials} db")
        
        with col2:
            st.metric("💰 Összes költség", f"{total_cost:,} Ft")
        
        with col3:
            st.metric("📊 Kategóriák", f"{len(category_totals)} db")
        
        # Category breakdown
        st.subheader("📋 Kategóriánkénti bontás")
        for category, cost in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            st.write(f"**{category}:** {cost:,} Ft ({percentage:.1f}%)")
            st.progress(percentage / 100)
    
    else:
        st.info("Nincsenek még anyagköltségek rögzítve.")
        st.caption("💡 Tipp: Kattints az 'Új anyag hozzáadása' gombra az első anyag hozzáadásához.")
    
    # Edit material dialog
    if st.session_state.get("edit_material_index") is not None:
        edit_index = st.session_state.edit_material_index
        if edit_index < len(project["material_costs"]):
            material = project["material_costs"][edit_index]
            
            st.markdown("---")
            st.subheader("Anyag szerkesztése")
            
            with st.form("edit_material_form"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    edit_name = st.text_input("Anyag neve", value=material["name"], key="edit_material_name")
                
                with col2:
                    edit_category = st.selectbox(
                        "Kategória",
                        ["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"],
                        index=["Alapozás", "Falazat", "Tető", "Gépészet", "Villanyszerelés", "Burkolás", "Festés", "Egyéb"].index(material.get("category", "Egyéb")),
                        key="edit_material_category"
                    )
                
                with col3:
                    edit_quantity = st.number_input("Mennyiség", min_value=0.0, value=material["quantity"], key="edit_material_quantity")
                
                with col4:
                    edit_unit = st.selectbox(
                        "Mértékegység",
                        ["db", "m²", "m³", "kg", "t", "m", "l", "csomag"],
                        index=["db", "m²", "m³", "kg", "t", "m", "l", "csomag"].index(material.get("unit", "db")),
                        key="edit_material_unit"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    edit_unit_price = st.number_input("Egységár (Ft)", min_value=0, value=material["unit_price"], key="edit_material_unit_price")
                
                with col2:
                    edit_supplier = st.text_input("Beszállító", value=material.get("supplier", ""), key="edit_material_supplier")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Mentés", type="primary"):
                        if edit_name and edit_unit_price > 0:
                            project["material_costs"][edit_index] = {
                                "name": edit_name,
                                "category": edit_category,
                                "quantity": edit_quantity,
                                "unit": edit_unit,
                                "unit_price": edit_unit_price,
                                "total_price": edit_quantity * edit_unit_price,
                                "supplier": edit_supplier
                            }
                            st.success("Anyag sikeresen frissítve!")
                            st.session_state.edit_material_index = None
                            st.rerun()
                        else:
                            st.error("Az anyag neve és egységára megadása kötelező!")
                
                with col2:
                    if st.form_submit_button("❌ Mégse"):
                        st.session_state.edit_material_index = None
                        st.rerun()
    
    # Delete material confirmation
    if st.session_state.get("delete_material_index") is not None:
        delete_index = st.session_state.delete_material_index
        if delete_index < len(project["material_costs"]):
            material = project["material_costs"][delete_index]
            
            st.markdown("---")
            st.warning(f"⚠️ Biztosan törölni szeretnéd ezt az anyagot: **{material['name']}**?")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Igen, törlés", key="confirm_delete_material"):
                    del project["material_costs"][delete_index]
                    st.success("Anyag sikeresen törölve!")
                    st.session_state.delete_material_index = None
                    st.rerun()
            
            with col2:
                if st.button("❌ Mégse", key="cancel_delete_material"):
                    st.session_state.delete_material_index = None
                    st.rerun()
