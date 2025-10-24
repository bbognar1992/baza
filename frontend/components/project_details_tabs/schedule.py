import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from default_data import get_default_phases

def render_schedule_tab(project):
    """Render the schedule tab for project details."""
    st.subheader("📊 Ütemterv")
    try:
        phases_def = get_default_phases()
        proj_start = datetime.fromisoformat(str(project.get("start", "2025-01-01")))
        proj_end = datetime.fromisoformat(str(project.get("end", "2025-12-31")))
        duration_days = max((proj_end - proj_start).days, 1)
        num_phases = max(len(phases_def), 1)
        slice_days = max(duration_days // num_phases, 1)
        rows = []
        current_start = proj_start
        
        for pi, phase in enumerate(phases_def):
            # Use actual phase duration instead of equal slices
            phase_duration = phase.get('total_duration_days', slice_days)
            current_end = current_start + timedelta(days=phase_duration)
            # clamp to project end
            if pi == num_phases - 1 or current_end > proj_end:
                current_end = proj_end
            phase_total = len(phase["tasks"]) or 1
            phase_done = sum(1 for v in project["phases_checked"][pi] if v) if pi < len(project["phases_checked"]) else 0
            completion = int(phase_done * 100 / phase_total)
            rows.append({
                "Fázis": f"{pi+1}. {phase['name']} ({phase_duration} nap)",
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
                title="Fázisok ütemterve",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nincs megjeleníthető ütemterv.")
    except Exception as e:
        st.error(f"Hiba az ütemterv generálásakor: {str(e)}")
