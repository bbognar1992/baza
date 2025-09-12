import streamlit as st
from default_data import ensure_base_session_state
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configure page
st.set_page_config(
    page_title="ÉpítAI - Üdvözöljük",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
ensure_base_session_state(st)

def show_project_insights():
    """Show interesting project insights for logged-in users"""
    st.markdown("## 🎯 Projekt Áttekintés")
    st.markdown("Üdvözöljük vissza! Íme néhány érdekes információ a projekteiről:")
    
    # Debug info (can be removed in production)
    with st.expander("🔧 Debug Info", expanded=False):
        st.write("Session state keys:", list(st.session_state.keys()))
        st.write("User logged in:", st.session_state.get("user_logged_in", False))
        st.write("Projects count:", len(st.session_state.get("projects", [])))
    
    projects = st.session_state.projects
    resources = st.session_state.resources
    
    if not projects:
        st.info("Még nincsenek projektek a rendszerben.")
        return
    
    # Calculate key metrics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.get("status") in ["Folyamatban", "Késésben"]])
    completed_projects = len([p for p in projects if p.get("status") == "Lezárt"])
    planning_projects = len([p for p in projects if p.get("status") == "Tervezés alatt"])
    
    # Average progress
    avg_progress = sum(p.get("progress", 0) for p in projects) / total_projects if total_projects > 0 else 0
    
    # Overdue projects
    today = datetime.now().date()
    overdue_projects = []
    for project in projects:
        try:
            end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
            if end_date < today and project.get("status") not in ["Lezárt"]:
                overdue_projects.append(project)
        except:
            pass
    
    # Key metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Összes projekt",
            value=total_projects,
            delta=f"{active_projects} aktív"
        )
    
    with col2:
        st.metric(
            label="🔄 Aktív projektek",
            value=active_projects,
            delta=f"{active_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
        )
    
    with col3:
        st.metric(
            label="✅ Lezárt projektek",
            value=completed_projects,
            delta=f"{completed_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
        )
    
    with col4:
        st.metric(
            label="📈 Átlagos haladás",
            value=f"{avg_progress:.1f}%",
            delta=f"⚠️ {len(overdue_projects)} lejárt" if len(overdue_projects) > 0 else "✅ Minden rendben"
        )
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # Project status distribution
        status_counts = {}
        for project in projects:
            status = project.get("status", "Ismeretlen")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            st.subheader("📊 Projekt státusz eloszlás")
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Projektek státusza szerint",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Projects by location
        location_counts = {}
        for project in projects:
            locations = project.get("locations", [])
            for location in locations:
                location_counts[location] = location_counts.get(location, 0) + 1
        
        if location_counts:
            st.subheader("🗺️ Projektek helyszín szerint")
            locations_df = pd.DataFrame(list(location_counts.items()), columns=['Helyszín', 'Projektek száma'])
            fig_bar = px.bar(
                locations_df,
                x='Helyszín',
                y='Projektek száma',
                title="Projektek száma helyszín szerint",
                color='Projektek száma',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Recent activity and alerts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏰ Közelgő határidők")
        
        # Upcoming deadlines (next 30 days)
        upcoming_deadlines = []
        for project in projects:
            try:
                end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
                days_until = (end_date - today).days
                if 0 <= days_until <= 30 and project.get("status") not in ["Lezárt"]:
                    upcoming_deadlines.append({
                        'name': project.get('name', 'Névtelen'),
                        'end_date': end_date,
                        'days_until': days_until,
                        'status': project.get('status', 'Ismeretlen')
                    })
            except:
                pass
        
        if upcoming_deadlines:
            upcoming_deadlines.sort(key=lambda x: x['days_until'])
            
            for deadline in upcoming_deadlines[:5]:  # Show top 5
                days = deadline['days_until']
                if days == 0:
                    color = "🔴"
                    text = "Ma jár le!"
                elif days <= 7:
                    color = "🟡"
                    text = f"{days} nap múlva"
                else:
                    color = "🟢"
                    text = f"{days} nap múlva"
                
                st.write(f"{color} **{deadline['name']}** - {text}")
        else:
            st.info("Nincs közelgő határidő a következő 30 napban.")
    
    with col2:
        st.subheader("🚨 Figyelmeztetések")
        
        alerts = []
        
        # Overdue projects
        if overdue_projects:
            alerts.append(f"⚠️ **{len(overdue_projects)} lejárt projekt** - sürgős ellenőrzés szükséges")
        
        # Projects with low progress
        low_progress_projects = [p for p in projects if p.get("progress", 0) < 25 and p.get("status") == "Folyamatban"]
        if low_progress_projects:
            alerts.append(f"📉 **{len(low_progress_projects)} projekt** alacsony haladással (25% alatt)")
        
        # Resource availability
        total_resources = len(resources)
        available_resources = len([r for r in resources if r.get("Elérhetőség") == "Elérhető"])
        if available_resources < total_resources * 0.8:  # Less than 80% available
            alerts.append(f"👥 **{total_resources - available_resources} erőforrás** nem elérhető")
        
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ Nincs aktív figyelmeztetés")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Gyors műveletek")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Teljes Dashboard", use_container_width=True, key="insights_dashboard"):
            st.switch_page("pages/Home.py")
    
    with col2:
        if st.button("📁 Projektek kezelése", use_container_width=True, key="insights_projects"):
            st.switch_page("pages/Projects.py")
    
    with col3:
        if st.button("👥 Erőforrások", use_container_width=True, key="insights_resources"):
            st.switch_page("pages/Resources.py")
    
    with col4:
        if st.button("🚪 Kijelentkezés", use_container_width=True, key="insights_logout"):
            # Clear all session state to fully logout
            for key in list(st.session_state.keys()):
                if key not in ["resources", "profession_types", "project_types"]:  # Keep default data
                    del st.session_state[key]
            st.rerun()

def landing_page():
    """Landing page for logged out users"""
    
    with st.container():
        # Center the content using columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Welcome message
            st.markdown("""
            ### Üdvözöljük az ÉpítAI rendszerben!
            
            Az ÉpítAI egy modern építőipari projektmenedzsment rendszer, amely segít Önnek 
            hatékonyan kezelni projekteit, erőforrásait és ütemezéseit.
            
            **Főbb funkciók:**
            - 📊 Projekt követés és monitoring
            - 👥 Erőforrás menedzsment
            - 📅 Ütemezés és határidő kezelés
            - 🤖 AI asszisztensek ajánlatkéréshez és szerződéskészítéshez
            """)
            
            # Login button
            st.divider()
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🔐 Bejelentkezés", use_container_width=True, type="primary"):
                    st.switch_page("pages/Login.py")

            
            # Footer
            st.divider()
            st.markdown("<div style='text-align: center;'>© 2025 ÉpítAI - Construction Management System</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    # Check if user is logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    has_projects = len(st.session_state.get("projects", [])) > 0

    # User is not logged in, show landing page
    landing_page()
