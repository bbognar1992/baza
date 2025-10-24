import streamlit as st
from default_data import ensure_base_session_state, get_default_profession_types
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="Szakma típusok – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("🔧 Szakma típusok")
st.write("Hozz létre és kezeld a szakma típusokat.")

# Profession types are now handled by ensure_base_session_state

if "selected_profession_type_index" not in st.session_state:
    st.session_state.selected_profession_type_index = None

with st.expander("➕ Új szakma típus hozzáadása", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        t_name = st.text_input("Szakma neve", key="szakma_name")
    with col2:
        t_desc = st.text_input("Leírás", key="szakma_desc")
    with col3:
        t_level = st.selectbox("Szint", ["Szakmunkás", "Vezető", "Szakértő"], key="szakma_level")
    
    if st.button("Hozzáadás", key="szakma_add"):
        if t_name:
            # prevent duplicate by name
            if any(st.get("Név") == t_name for st in st.session_state.profession_types):
                st.warning("Ilyen nevű szakma már létezik.")
            else:
                st.session_state.profession_types.append({
                    "Név": t_name, 
                    "Leírás": t_desc or "-",
                    "Szint": t_level
                })
                st.success(f"Szakma típus hozzáadva: {t_name}")
                st.rerun()

selected_index = st.session_state.selected_profession_type_index

if selected_index is not None and 0 <= selected_index < len(st.session_state.profession_types):
    profession = st.session_state.profession_types[selected_index]
    st.subheader(profession.get("Név", "-"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Leírás:** {profession.get('Leírás', '-')}")
    with col2:
        st.write(f"**Szint:** {profession.get('Szint', '-')}")
    
    # Editable fields
    st.write("### Szerkesztés")
    new_name = st.text_input("Szakma neve", value=profession.get("Név", ""), key=f"edit_szakma_name_{selected_index}")
    new_desc = st.text_input("Leírás", value=profession.get("Leírás", ""), key=f"edit_szakma_desc_{selected_index}")
    new_level = st.selectbox("Szint", ["Szakmunkás", "Vezető", "Szakértő"], 
                           index=["Szakmunkás", "Vezető", "Szakértő"].index(profession.get("Szint", "Szakmunkás")),
                           key=f"edit_szakma_level_{selected_index}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Mentés", key=f"save_szakma_{selected_index}"):
            profession["Név"] = new_name
            profession["Leírás"] = new_desc
            profession["Szint"] = new_level
            st.success("Szakma típus frissítve!")
            st.rerun()
    
    with col2:
        if st.button("⬅️ Vissza a listához"):
            st.session_state.selected_profession_type_index = None
            st.rerun()
else:
    st.write("### Elérhető szakma típusok")
    if st.session_state.profession_types:
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Keresés név alapján", key="szakma_search")
        with col2:
            level_filter = st.selectbox("Szint szűrő", ["Összes", "Szakmunkás", "Vezető", "Szakértő"], key="szakma_filter")
        
        # Filter the list
        filtered_profession = st.session_state.profession_types
        if search_term:
            filtered_profession = [s for s in filtered_profession if search_term.lower() in s.get("Név", "").lower()]
        if level_filter != "Összes":
            filtered_profession = [s for s in filtered_profession if s.get("Szint") == level_filter]
        
        # Display filtered results
        if filtered_profession:
            header = st.columns([3, 4, 2, 2, 1])
            header[0].markdown("**Név**")
            header[1].markdown("**Leírás**")
            header[2].markdown("**Szint**")
            header[3].markdown("**Művelet**")
            header[4].markdown("")
            
            for idx, profession in enumerate(filtered_profession):
                # Find original index for operations
                original_idx = st.session_state.profession_types.index(profession)
                
                cols = st.columns([3, 4, 2, 2, 1])
                cols[0].markdown(f"**{profession.get('Név','-')}**")
                cols[1].write(profession.get("Leírás", "-"))
                
                # Color code the level
                level = profession.get("Szint", "-")
                if level == "Vezető":
                    cols[2].markdown(f"<span style='color: orange; font-weight: bold;'>{level}</span>", unsafe_allow_html=True)
                elif level == "Szakértő":
                    cols[2].markdown(f"<span style='color: red; font-weight: bold;'>{level}</span>", unsafe_allow_html=True)
                else:
                    cols[2].write(level)
                
                if cols[3].button("Megnyitás", key=f"open_szakma_{original_idx}"):
                    st.session_state.selected_profession_type_index = original_idx
                    st.rerun()
                if cols[4].button("❌", key=f"del_szakma_{original_idx}"):
                    st.session_state.profession_types.pop(original_idx)
                    st.rerun()
        else:
            st.info("Nincs találat a megadott szűrőkkel.")
    else:
        st.info("Nincs szakma típus. Adj hozzá fentebb.")

# Statistics
if st.session_state.profession_types:
    st.write("### Statisztikák")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_count = len(st.session_state.profession_types)
        st.metric("Összes szakma típus", total_count)
    
    with col2:
        worker_count = len([s for s in st.session_state.profession_types if s.get("Szint") == "Szakmunkás"])
        st.metric("Szakmunkások", worker_count)
    
    with col3:
        leader_count = len([s for s in st.session_state.profession_types if s.get("Szint") in ["Vezető", "Szakértő"]])
        st.metric("Vezetők/Szakértők", leader_count)
