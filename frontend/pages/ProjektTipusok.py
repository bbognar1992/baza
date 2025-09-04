import streamlit as st
from default_data import get_default_phases, ensure_base_session_state, get_default_project_types, update_phase_durations, calculate_total_project_duration

# Profession types are now handled by ensure_base_session_state

st.set_page_config(page_title="Projekt típusok – ÉpítAI", layout="wide")

st.title("🏷️ Projekt típusok")
st.write("Hozz létre és kezeld a projekt típusokat.")

ensure_base_session_state(st)

if "selected_project_type_index" not in st.session_state:
    st.session_state.selected_project_type_index = None

def _noop():
    return None

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

selected_index = st.session_state.selected_project_type_index

if selected_index is not None and 0 <= selected_index < len(st.session_state.project_types):
    ptype = st.session_state.project_types[selected_index]
    st.subheader(ptype.get("Név", "-"))
    st.write(ptype.get("Leírás", "-"))

    # phases per type stored in the type dict (editable)
    if "phases" not in ptype or not ptype["phases"]:
        ptype["phases"] = get_default_phases()

    # Ensure phases_checked matches phases shape
    if "phases_checked" not in ptype or not ptype["phases_checked"]:
        ptype["phases_checked"] = [[False for _ in p["tasks"]] for p in ptype["phases"]]
    else:
        # resize rows to match number of phases
        while len(ptype["phases_checked"]) < len(ptype["phases"]):
            ptype["phases_checked"].append([False for _ in ptype["phases"][len(ptype["phases_checked"])]["tasks"]])
        if len(ptype["phases_checked"]) > len(ptype["phases"]):
            ptype["phases_checked"] = ptype["phases_checked"][:len(ptype["phases"])]

    st.write("### Fázisok (szerkeszthető)")
    total_tasks = 0
    total_done = 0

    # Button to add a new phase
    if st.button("➕ Új fázis hozzáadása"):
        ptype["phases"].append({"name": "Új fázis", "tasks": [{"name": "Új feladat", "profession": ""}]})
        ptype["phases_checked"].append([False])
        st.rerun()

    for pi, phase in enumerate(ptype["phases"]):
        with st.expander(f"{pi+1}. {phase['name']}", expanded=False):
            # Editable phase name
            new_name = st.text_input("Fázis neve", value=phase["name"], key=f"ptype_name_{selected_index}_{pi}")
            phase["name"] = new_name.strip() or phase["name"]

            # Ensure tasks have the new structure with profession
            if "tasks" not in phase or not phase["tasks"]:
                phase["tasks"] = [{"name": "Új feladat", "profession": "", "duration_days": 1, "required_people": 1}]
            elif isinstance(phase["tasks"][0], str):  # Convert old string format to new object format
                phase["tasks"] = [{"name": task, "profession": "", "duration_days": 1, "required_people": 1} for task in phase["tasks"]]
            # Ensure all tasks have required fields
            for task in phase["tasks"]:
                if "duration_days" not in task:
                    task["duration_days"] = 1
                if "required_people" not in task:
                    task["required_people"] = 1

            # Task management section
            st.write("#### Feladatok")
            
            # Add new task button
            if st.button("➕ Új feladat", key=f"add_task_{selected_index}_{pi}"):
                phase["tasks"].append({"name": "Új feladat", "profession": "", "duration_days": 1, "required_people": 1})
                ptype["phases_checked"][pi].append(False)
                st.rerun()

            # Display and edit tasks
            for ti, task_obj in enumerate(phase["tasks"]):
                task_name = task_obj.get("name", "Új feladat")
                task_profession = task_obj.get("profession", "")
                
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 1, 1])
                    
                    with col1:
                        # Task name input
                        new_task_name = st.text_input(
                            "Feladat neve", 
                            value=task_name, 
                            key=f"task_name_{selected_index}_{pi}_{ti}"
                        )
                        task_obj["name"] = new_task_name.strip() or "Új feladat"
                    
                    with col2:
                        # Profession selection
                        profession_names = [""] + [p.get("Név", "") for p in st.session_state.profession_types]
                        current_profession_index = profession_names.index(task_profession) if task_profession in profession_names else 0
                        selected_profession = st.selectbox(
                            "Szakma", 
                            options=profession_names,
                            index=current_profession_index,
                            key=f"task_profession_{selected_index}_{pi}_{ti}"
                        )
                        task_obj["profession"] = selected_profession
                    
                    with col3:
                        # Duration input
                        task_duration = task_obj.get("duration_days", 1)
                        new_duration = st.number_input(
                            "Idő (nap)", 
                            min_value=1, 
                            value=int(task_duration), 
                            key=f"task_duration_{selected_index}_{pi}_{ti}"
                        )
                        if new_duration != task_duration:
                            task_obj["duration_days"] = new_duration
                            # Update phase total duration
                            phase["total_duration_days"] = sum(task.get("duration_days", 1) for task in phase["tasks"])
                    
                    with col4:
                        # Required people input
                        task_required_people = task_obj.get("required_people", 1)
                        new_required_people = st.number_input(
                            "Emberek", 
                            min_value=1, 
                            value=int(task_required_people), 
                            key=f"task_required_people_{selected_index}_{pi}_{ti}"
                        )
                        if new_required_people != task_required_people:
                            task_obj["required_people"] = new_required_people
                    
                    with col5:
                        # Checkbox for completion
                        if ti < len(ptype["phases_checked"][pi]):
                            current = ptype["phases_checked"][pi][ti]
                            stored = st.checkbox("✓", value=current, key=f"ptype_chk_{selected_index}_{pi}_{ti}")
                            ptype["phases_checked"][pi][ti] = stored
                            if stored:
                                total_done += 1
                            total_tasks += 1
                    
                    with col6:
                        # Delete task button
                        if st.button("❌", key=f"del_task_{selected_index}_{pi}_{ti}"):
                            phase["tasks"].pop(ti)
                            if ti < len(ptype["phases_checked"][pi]):
                                ptype["phases_checked"][pi].pop(ti)
                            st.rerun()
                    
                    # Show profession info if selected
                    if selected_profession:
                        profession_info = next((p for p in st.session_state.profession_types if p.get("Név") == selected_profession), None)
                        if profession_info:
                            level = profession_info.get("Szint", "")
                            level_color = "orange" if level == "Vezető" else "red" if level == "Szakértő" else "blue"
                            st.markdown(f"<small style='color: {level_color};'>🔧 {selected_profession} ({level})</small>", unsafe_allow_html=True)

            # Ensure phases_checked matches tasks count
            while len(ptype["phases_checked"][pi]) < len(phase["tasks"]):
                ptype["phases_checked"][pi].append(False)
            if len(ptype["phases_checked"][pi]) > len(phase["tasks"]):
                ptype["phases_checked"][pi] = ptype["phases_checked"][pi][:len(phase["tasks"])]

            # Progress for this phase
            phase_total = len(phase["tasks"]) or 1
            phase_done = sum(1 for v in ptype["phases_checked"][pi] if v)
            pct = int(phase_done * 100 / phase_total)
            st.progress(pct)
            st.caption(f"{pct}% ({phase_done}/{phase_total})")
            
            # Phase duration and people summary
            total_phase_duration = sum(task.get("duration_days", 1) for task in phase["tasks"])
            total_phase_people = sum(task.get("required_people", 1) for task in phase["tasks"])
            phase["total_duration_days"] = total_phase_duration  # Update the phase total
            st.info(f"⏱️ Fázis teljes időtartama: {total_phase_duration} nap | 👥 Szükséges emberek: {total_phase_people} fő")

            # Delete phase button
            if st.button("🗑️ Fázis törlése", key=f"del_phase_{selected_index}_{pi}"):
                ptype["phases"].pop(pi)
                ptype["phases_checked"].pop(pi)
                st.rerun()

    overall = int(total_done * 100 / total_tasks) if total_tasks else 0
    st.write("### Összhaladás")
    st.progress(overall)
    st.caption(f"{overall}%")
    
    # Total project duration and people
    total_project_duration = calculate_total_project_duration(ptype["phases"])
    total_project_people = sum(
        sum(task.get("required_people", 1) for task in phase["tasks"]) 
        for phase in ptype["phases"]
    )
    
    st.write("### ⏱️ Projekt áttekintés")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Teljes időtartam", f"{total_project_duration} nap")
    with col2:
        st.metric("Szükséges emberek", f"{total_project_people} fő")

    if st.button("⬅️ Vissza a listához"):
        st.session_state.selected_project_type_index = None
        st.rerun()
else:
    st.write("### Elérhető típusok")
    if st.session_state.project_types:
        # list with open/remove actions
        header = st.columns([3, 6, 2, 1])
        header[0].markdown("**Név**")
        header[1].markdown("**Leírás**")
        header[2].markdown("**Művelet**")
        header[3].markdown("")
        for idx, ptype in enumerate(st.session_state.project_types):
            cols = st.columns([3, 6, 2, 1])
            cols[0].markdown(f"**{ptype.get('Név','-')}**")
            cols[1].write(ptype.get("Leírás", "-"))
            if cols[2].button("Megnyitás", key=f"open_ptype_{idx}"):
                st.session_state.selected_project_type_index = idx
                st.rerun()
            if cols[3].button("❌", key=f"del_ptype_{idx}"):
                st.session_state.project_types.pop(idx)
                st.rerun()
    else:
        st.info("Nincs projekt típus. Adj hozzá fentebb.")


