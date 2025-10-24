import streamlit as st
from datetime import datetime

def render_basic_info_tab(project):
    """Render the basic information tab for project details."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Projekt információk")
        st.write(f"**Név:** {project.get('name', 'Nincs megadva')}")
        st.write(f"**Státusz:** {project.get('status', 'Nincs megadva')}")
        st.write(f"**Típus:** {project.get('type', 'Nincs megadva')}")
        st.write(f"**Alapterület:** {project.get('size', 'Nincs megadva')} m²")
        st.write(f"**Előrehaladás:** {project.get('progress', 0)}%")
    
    with col2:
        st.subheader("Időzítés")
        st.write(f"**Kezdés:** {project.get('start', 'Nincs megadva')}")
        st.write(f"**Befejezés:** {project.get('end', 'Nincs megadva')}")
        
        # Calculate duration
        try:
            start_date = datetime.strptime(project.get("start", "2025-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d")
            duration = (end_date - start_date).days
            st.write(f"**Időtartam:** {duration} nap")
        except:
            st.write("**Időtartam:** Nincs megadva")
