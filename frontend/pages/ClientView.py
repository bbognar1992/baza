import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
from default_data import get_default_phases, ensure_base_session_state

st.set_page_config(page_title="Ügyfél Nézet – ÉpítAI", layout="wide")

# Custom CSS for client view styling
st.markdown("""
<style>
.client-header {
    background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}
.client-metric {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}
.phase-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.task-item {
    padding: 0.5rem;
    margin: 0.25rem 0;
    border-radius: 4px;
    background: #f8f9fa;
}
.task-completed {
    background: #d4edda;
    border-left: 4px solid #28a745;
}
.task-pending {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
}
</style>
""", unsafe_allow_html=True)

ensure_base_session_state(st)

# Client view header
st.markdown("""
<div class="client-header">
    <h1>🏗️ ÉpítAI - Projekt Áttekintés</h1>
    <p>Ügyfél nézet - Projekt állapot és haladás</p>
</div>
""", unsafe_allow_html=True)

# Project selection for client view
if "client_selected_project_index" not in st.session_state:
    st.session_state.client_selected_project_index = None

# Project selector
if st.session_state.projects:
    project_names = [f"{p['name']} ({p.get('status', 'Ismeretlen')})" for p in st.session_state.projects]
    selected_project_name = st.selectbox(
        "Válassz projektet:",
        options=project_names,
        index=st.session_state.client_selected_project_index if st.session_state.client_selected_project_index is not None else 0
    )
    
    # Find the selected project
    selected_project = None
    for i, project in enumerate(st.session_state.projects):
        if f"{project['name']} ({project.get('status', 'Ismeretlen')})" == selected_project_name:
            selected_project = project
            st.session_state.client_selected_project_index = i
            break
else:
    st.warning("Nincs elérhető projekt.")
    st.stop()

if selected_project:
    # Project header with key information
    st.markdown(f"""
    <div class="client-header">
        <h2>📋 {selected_project['name']}</h2>
        <p><strong>Projekt típus:</strong> {selected_project.get('type', 'Nincs megadva')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics in a clean layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="client-metric">
            <h4>📊 Állapot</h4>
            <p><strong>{selected_project.get('status', 'Ismeretlen')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="client-metric">
            <h4>📅 Kezdés</h4>
            <p><strong>{selected_project.get('start', '-')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="client-metric">
            <h4>🎯 Befejezés</h4>
            <p><strong>{selected_project.get('end', '-')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="client-metric">
            <h4>📍 Helyszín</h4>
            <p><strong>{', '.join(selected_project.get('locations', ['Nincs megadva']))}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Overall progress
    st.markdown("### 📈 Teljes haladás")
    progress_value = int(selected_project.get("progress", 0))
    st.progress(progress_value / 100)
    st.markdown(f"<p style='text-align: center; font-size: 1.2em;'><strong>{progress_value}% kész</strong></p>", unsafe_allow_html=True)

    # Project phases with simplified view - only current and next phase
    st.markdown("### 🏗️ Aktuális fázisok")
    phases_def = get_default_phases()
    
    # Ensure project has phases_checked field
    if "phases_checked" not in selected_project or not selected_project["phases_checked"]:
        selected_project["phases_checked"] = [[False for _ in p["tasks"]] for p in phases_def]

    # Find current phase (first incomplete phase)
    current_phase_index = -1
    for pi, phase in enumerate(phases_def):
        if pi < len(selected_project["phases_checked"]):
            phase_total = len(phase["tasks"])
            phase_done = sum(1 for v in selected_project["phases_checked"][pi] if v)
            if phase_done < phase_total:
                current_phase_index = pi
                break
    
    # If all phases are complete, show the last phase
    if current_phase_index == -1:
        current_phase_index = len(phases_def) - 1
    
    # Show current phase
    if 0 <= current_phase_index < len(phases_def):
        phase = phases_def[current_phase_index]
        phase_total = len(phase["tasks"])
        phase_done = sum(1 for v in selected_project["phases_checked"][current_phase_index] if v) if current_phase_index < len(selected_project["phases_checked"]) else 0
        phase_progress = int(phase_done * 100 / phase_total) if phase_total else 0
        
        st.markdown(f"""
        <div class="phase-card">
            <h4>🎯 Aktuális fázis: {current_phase_index+1}. {phase['name']}</h4>
            <p><strong>Haladás:</strong> {phase_done}/{phase_total} feladat kész</p>
        """, unsafe_allow_html=True)
        
        st.progress(phase_progress / 100)
        st.markdown(f"<p style='text-align: center;'><strong>{phase_progress}%</strong></p>", unsafe_allow_html=True)
        
        # Show tasks in a simplified way
        for ti, task in enumerate(phase["tasks"]):
            is_completed = selected_project["phases_checked"][current_phase_index][ti] if current_phase_index < len(selected_project["phases_checked"]) and ti < len(selected_project["phases_checked"][current_phase_index]) else False
            
            # Handle both old string format and new object format
            if isinstance(task, str):
                task_name = task
            else:
                task_name = task.get("name", "Unknown task")
            
            status_icon = "✅" if is_completed else "⏳"
            css_class = "task-completed" if is_completed else "task-pending"
            
            st.markdown(f"""
            <div class="task-item {css_class}">
                {status_icon} {task_name}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Show next phase if available
    next_phase_index = current_phase_index + 1
    if next_phase_index < len(phases_def):
        next_phase = phases_def[next_phase_index]
        
        st.markdown(f"""
        <div class="phase-card">
            <h4>⏭️ Következő fázis: {next_phase_index+1}. {next_phase['name']}</h4>
        </div>
        """, unsafe_allow_html=True)

    # Simplified timeline chart
    st.markdown("### 📅 Ütemterv")
    try:
        proj_start = datetime.fromisoformat(str(selected_project.get("start", "2025-01-01")))
        proj_end = datetime.fromisoformat(str(selected_project.get("end", "2025-12-31")))
        duration_days = max((proj_end - proj_start).days, 1)
        num_phases = max(len(phases_def), 1)
        slice_days = max(duration_days // num_phases, 1)
        
        rows = []
        current_start = proj_start
        for pi, phase in enumerate(phases_def):
            current_end = current_start + timedelta(days=slice_days)
            if pi == num_phases - 1 or current_end > proj_end:
                current_end = proj_end
            
            phase_total = len(phase["tasks"]) or 1
            phase_done = sum(1 for v in selected_project["phases_checked"][pi] if v) if pi < len(selected_project["phases_checked"]) else 0
            completion = int(phase_done * 100 / phase_total)
            
            rows.append({
                "Fázis": f"{pi+1}. {phase['name']}",
                "Kezdés": current_start,
                "Befejezés": current_end,
                "Készültség": completion,
            })
            current_start = current_end
        
        if rows:
            fig = px.timeline(
                rows,
                x_start="Kezdés",
                x_end="Befejezés",
                y="Fázis",
                color="Készültség",
                color_continuous_scale="Blues",
                title="Projekt ütemterv",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                height=320, 
                margin=dict(l=10, r=10, t=40, b=10),
                title_font_size=16,
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Ütemterv nem elérhető.")

    # Footer with contact information
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px;'>
        <h4>📞 Kapcsolat</h4>
        <p>Kérdéseivel forduljon hozzánk bizalommal!</p>
        <p><strong>Email:</strong> info@epitai.hu | <strong>Telefon:</strong> +36 1 234 5678</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Válassz ki egy projektet a fenti listából.")
