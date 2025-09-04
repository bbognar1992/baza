import streamlit as st
from default_data import get_default_phases, ensure_base_session_state, get_default_project_types

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
        ptype["phases"].append({"name": "Új fázis", "tasks": ["Új feladat"]})
        ptype["phases_checked"].append([False])
        st.rerun()

    for pi, phase in enumerate(ptype["phases"]):
        with st.expander(f"{pi+1}. {phase['name']}", expanded=False):
            # Editable phase name
            new_name = st.text_input("Fázis neve", value=phase["name"], key=f"ptype_name_{selected_index}_{pi}")
            phase["name"] = new_name.strip() or phase["name"]

            # Editable tasks as newline-separated
            tasks_str = "\n".join(phase.get("tasks", []))
            new_tasks_str = st.text_area("Feladatok (soronként)", value=tasks_str, height=120, key=f"ptype_tasks_{selected_index}_{pi}")
            new_tasks = [ln.strip() for ln in new_tasks_str.split("\n") if ln.strip()]
            if not new_tasks:
                new_tasks = ["(üres feladat)"]
            phase["tasks"] = new_tasks

            # Resize checked list for this phase to match tasks count
            current_checks = ptype["phases_checked"][pi]
            new_len = len(new_tasks)
            resized = []
            for ti in range(new_len):
                resized.append(current_checks[ti] if ti < len(current_checks) else False)
            ptype["phases_checked"][pi] = resized

            # Render checkboxes bound to stored state
            for ti, task in enumerate(new_tasks):
                total_tasks += 1
                current = ptype["phases_checked"][pi][ti]
                stored = st.checkbox(task, value=current, key=f"ptype_chk_{selected_index}_{pi}_{ti}")
                ptype["phases_checked"][pi][ti] = stored
                if stored:
                    total_done += 1

            phase_total = len(new_tasks) or 1
            phase_done = sum(1 for v in ptype["phases_checked"][pi] if v)
            pct = int(phase_done * 100 / phase_total)
            st.progress(pct)
            st.caption(f"{pct}% ({phase_done}/{phase_total})")

            # Delete phase button
            if st.button("Fázis törlése", key=f"del_phase_{selected_index}_{pi}"):
                ptype["phases"].pop(pi)
                ptype["phases_checked"].pop(pi)
                st.rerun()

    overall = int(total_done * 100 / total_tasks) if total_tasks else 0
    st.write("### Összhaladás")
    st.progress(overall)
    st.caption(f"{overall}%")

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


