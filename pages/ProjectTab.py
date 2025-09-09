import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation

st.set_page_config(page_title="Projekt Dashboard – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Render sidebar navigation
render_sidebar_navigation()

st.title("📁 Projekt Dashboard")

# Calculate key metrics
projects = st.session_state.projects

# Project status distribution
status_counts = {}
for project in projects:
    status = project.get("status", "Ismeretlen")
    status_counts[status] = status_counts.get(status, 0) + 1

# Progress metrics
total_projects = len(projects)
active_projects = len([p for p in projects if p.get("status") in ["Folyamatban", "Késésben"]])
completed_projects = len([p for p in projects if p.get("status") == "Lezárt"])
planning_projects = len([p for p in projects if p.get("status") == "Tervezés alatt"])

# Average progress
avg_progress = sum(p.get("progress", 0) for p in projects) / total_projects if total_projects > 0 else 0

# Overdue projects (past end date)
today = datetime.now().date()
overdue_projects = []
for project in projects:
    try:
        end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
        if end_date < today and project.get("status") not in ["Lezárt"]:
            overdue_projects.append(project)
    except:
        pass

# Projects by location
location_counts = {}
for project in projects:
    locations = project.get("locations", [])
    for location in locations:
        location_counts[location] = location_counts.get(location, 0) + 1

# Top row - Key metrics
st.subheader("📊 Projekt mutatók")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Összes projekt",
        value=total_projects,
        delta=None
    )

with col2:
    st.metric(
        label="Aktív projektek",
        value=active_projects,
        delta=f"{active_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
    )

with col3:
    st.metric(
        label="Lezárt projektek",
        value=completed_projects,
        delta=f"{completed_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
    )

with col4:
    st.metric(
        label="Átlagos haladás",
        value=f"{avg_progress:.1f}%",
        delta=None
    )

with col5:
    st.metric(
        label="Lejárt projektek",
        value=len(overdue_projects),
        delta=f"⚠️ {len(overdue_projects)}" if len(overdue_projects) > 0 else "✅ 0"
    )

st.markdown("---")

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Projekt státusz eloszlás")
    if status_counts:
        # Create pie chart
        fig_pie = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Projektek státusza szerint",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Nincs projekt adat megjelenítéshez.")

with col2:
    st.subheader("🗺️ Projektek helyszín szerint")
    if location_counts:
        # Create bar chart
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
    else:
        st.info("Nincs helyszín adat megjelenítéshez.")

st.markdown("---")

# Project details
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
        # Sort by days until deadline
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
    st.subheader("📋 Legutóbbi projektek")
    
    # Show recent projects (last 5)
    recent_projects = sorted(projects, key=lambda x: x.get('start', '2025-01-01'), reverse=True)[:5]
    
    if recent_projects:
        for project in recent_projects:
            status_emoji = {
                "Tervezés alatt": "📋",
                "Folyamatban": "🔄",
                "Késésben": "⚠️",
                "Lezárt": "✅"
            }.get(project.get("status", ""), "❓")
            
            progress = project.get("progress", 0)
            st.write(f"{status_emoji} **{project.get('name', 'Névtelen')}** - {progress}%")
    else:
        st.info("Nincs projekt megjelenítéshez.")

st.markdown("---")

# Project alerts
st.subheader("🚨 Projekt figyelmeztetések")

alerts = []

# Overdue projects
if overdue_projects:
    alerts.append(f"⚠️ **{len(overdue_projects)} lejárt projekt** - sürgős ellenőrzés szükséges")

# Projects with low progress
low_progress_projects = [p for p in projects if p.get("progress", 0) < 25 and p.get("status") == "Folyamatban"]
if low_progress_projects:
    alerts.append(f"📉 **{len(low_progress_projects)} projekt** alacsony haladással (25% alatt)")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ Nincs aktív projekt figyelmeztetés")

st.markdown("---")

# Quick actions
st.subheader("🚀 Gyors műveletek")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Új projekt", use_container_width=True, key="projecttab_new_project"):
        st.switch_page("pages/Projects.py")

with col2:
    if st.button("📁 Projektek", use_container_width=True, key="projecttab_projects"):
        st.switch_page("pages/Projects.py")

with col3:
    if st.button("👥 Erőforrások", use_container_width=True, key="projecttab_resources"):
        st.switch_page("pages/Resources.py")

with col4:
    if st.button("📊 Ütemezés", use_container_width=True, key="projecttab_schedule"):
        st.switch_page("pages/utemezes.py")

st.markdown("---")
st.caption("💡 **Tipp:** Használd a bal oldali menüt a részletes funkciók eléréséhez.")
