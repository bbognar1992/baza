import streamlit as st
from default_data import get_default_phases

def render_phases_tab(project, project_index):
    """Render the phases tab for project details."""
    st.subheader("📅 Fázisok")
    phases_def = get_default_phases()
    
    # Ensure project has phases_checked field (for legacy items)
    if "phases_checked" not in project or not project["phases_checked"]:
        project["phases_checked"] = [[False for _ in p["tasks"]] for p in phases_def]
    
    total_tasks = 0
    total_done = 0
    
    for pi, phase in enumerate(phases_def):
        with st.expander(f"{pi+1}. {phase['name']}"):
            for ti, task in enumerate(phase["tasks"]):
                total_tasks += 1
                current = project["phases_checked"][pi][ti]
                
                # Handle both old string format and new object format
                if isinstance(task, str):
                    task_name = task
                    task_duration = "N/A"
                else:
                    task_name = task.get("name", "Unknown task")
                    task_profession = task.get("profession", "")
                    task_duration = task.get("duration_days", "N/A")
                    if isinstance(task_duration, int):
                        task_duration = f"{task_duration} nap"
                    if task_profession:
                        task_name = f"{task_name} (🔧 {task_profession})"
                
                # Display task with duration
                task_display = f"{task_name} ⏱️ {task_duration}"
                new_val = st.checkbox(task_display, value=current, key=f"proj_{project_index}_{pi}_{ti}")
                project["phases_checked"][pi][ti] = new_val
                if new_val:
                    total_done += 1
            
            # per-phase progress
            phase_total = len(phase["tasks"])
            phase_done = sum(1 for v in project["phases_checked"][pi] if v)
            _pct = int(phase_done * 100 / phase_total) if phase_total else 0
            st.progress(_pct)
            st.caption(f"{_pct}% ({phase_done}/{phase_total}) - Teljes idő: {phase.get('total_duration_days', 0)} nap")
    
    # Update overall project progress from checked tasks
    project["progress"] = int(total_done * 100 / total_tasks) if total_tasks else 0
