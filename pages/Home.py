import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation, handle_user_not_logged_in

st.set_page_config(page_title="ÉpítAI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
ensure_base_session_state(st)

# Check if user is logged in
handle_user_not_logged_in()

# Render sidebar navigation
render_sidebar_navigation()

st.title("Dashboard")

# Calculate key metrics
projects = st.session_state.projects
resources = st.session_state.resources

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📁 Projekt kapcsolatos", "👥 Erőforrás kapcsolatos", "📅 Heti tervezés"])

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

# Resource utilization
total_resources = len(resources)
available_resources = len([r for r in resources if r.get("Elérhetőség") == "Elérhető"])

# Projects by location
location_counts = {}
for project in projects:
    locations = project.get("locations", [])
    for location in locations:
        location_counts[location] = location_counts.get(location, 0) + 1

with tab1:
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

with tab2:
    # Resource metrics
    st.subheader("👥 Erőforrás mutatók")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Összes erőforrás",
            value=total_resources
        )
    
    with col2:
        st.metric(
            label="Elérhető erőforrás",
            value=available_resources,
            delta=f"{available_resources/total_resources*100:.1f}%" if total_resources > 0 else "0%"
        )
    
    with col3:
        unavailable_resources = total_resources - available_resources
        st.metric(
            label="Nem elérhető",
            value=unavailable_resources,
            delta=f"⚠️ {unavailable_resources}" if unavailable_resources > 0 else "✅ 0"
        )
    
    st.markdown("---")
    
    # Profession distribution
    st.subheader("🛠️ Szakmák eloszlása")
    profession_counts = {}
    for resource in resources:
        profession = resource.get("Pozíció", "Nincs megadva")
        profession_counts[profession] = profession_counts.get(profession, 0) + 1
    
    if profession_counts:
        # Create profession distribution chart
        profession_df = pd.DataFrame(list(profession_counts.items()), columns=['Szakma', 'Létszám'])
        fig_profession = px.pie(
            profession_df,
            values='Létszám',
            names='Szakma',
            title="Erőforrások szakmák szerint",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_profession.update_layout(height=400)
        st.plotly_chart(fig_profession, use_container_width=True)
        
        # Detailed profession list
        st.write("**Részletes szakma lista:**")
        for profession, count in sorted(profession_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"• {profession}: {count} fő")
    else:
        st.info("Nincs szakma adat megjelenítéshez.")
    
    st.markdown("---")
    
    # Resource alerts
    st.subheader("🚨 Erőforrás figyelmeztetések")
    
    resource_alerts = []
    
    # Resource availability
    unavailable_resources = total_resources - available_resources
    if unavailable_resources > 0:
        resource_alerts.append(f"👥 **{unavailable_resources} erőforrás** nem elérhető")
    
    # Check for critical profession shortages
    critical_professions = ["Építésvezető", "Műszaki vezető", "Kőműves", "Villanyszerelő"]
    for profession in critical_professions:
        count = profession_counts.get(profession, 0)
        if count == 0:
            resource_alerts.append(f"⚠️ **{profession}** hiányzik a csapatból")
        elif count == 1:
            resource_alerts.append(f"🟡 **{profession}** csak 1 fő - kockázat")
    
    if resource_alerts:
        for alert in resource_alerts:
            st.warning(alert)
    else:
        st.success("✅ Nincs aktív erőforrás figyelmeztetés")

with tab3:
    # Weekly Planning Section
    st.subheader("📅 Heti tervezés - Kivitelezői áttekintés")

    # Week selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_week = st.date_input(
            "Válassz hetet:",
            value=today,
            help="Válassz ki egy dátumot a hét tervezéséhez"
        )

    # Calculate week start and end
    week_start = selected_week - timedelta(days=selected_week.weekday())
    week_end = week_start + timedelta(days=6)

    st.markdown(f"**Tervezett hét:** {week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}")

    # Weekly planning metrics
    col1, col2, col3, col4 = st.columns(4)

    # Calculate weekly resource workload
    weekly_resource_workload = {}
    for resource in resources:
        if resource.get("Elérhetőség") == "Elérhető":
            # Count how many projects this resource is assigned to
            assigned_projects = 0
            for project in projects:
                if project.get("status") in ["Folyamatban", "Késésben"]:
                    if resource.get("Név") in project.get("members", []):
                        assigned_projects += 1
            weekly_resource_workload[resource.get("Név", "Névtelen")] = assigned_projects

    # Calculate weekly project tasks
    weekly_tasks = []
    for project in projects:
        if project.get("status") in ["Folyamatban", "Késésben"]:
            try:
                project_start = datetime.strptime(project.get("start", "2025-01-01"), "%Y-%m-%d").date()
                project_end = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
                
                # Check if project overlaps with selected week
                if not (project_end < week_start or project_start > week_end):
                    weekly_tasks.append({
                        'project': project.get('name', 'Névtelen'),
                        'status': project.get('status', 'Ismeretlen'),
                        'progress': project.get('progress', 0),
                        'members': len(project.get('members', [])),
                        'locations': project.get('locations', [])
                    })
            except:
                pass

    with col1:
        st.metric(
            label="Heti aktív projektek",
            value=len(weekly_tasks),
            delta=f"{len(weekly_tasks)} projekt"
        )

    with col2:
        available_this_week = len([r for r in resources if r.get("Elérhetőség") == "Elérhető"])
        st.metric(
            label="Elérhető erőforrások",
            value=available_this_week,
            delta=f"{available_this_week}/{total_resources}"
        )

    with col3:
        # Calculate total required people for the week
        total_required_people = sum(task['members'] for task in weekly_tasks)
        st.metric(
            label="Szükséges emberek",
            value=total_required_people,
            delta=f"{total_required_people} fő"
        )

    with col4:
        # Calculate workload distribution
        overloaded_resources = len([name for name, count in weekly_resource_workload.items() if count > 2])
        st.metric(
            label="Túlterhelt erőforrások",
            value=overloaded_resources,
            delta=f"⚠️ {overloaded_resources}" if overloaded_resources > 0 else "✅ 0"
        )

    st.markdown("---")

    # Weekly Resource Planning
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Erőforrás terhelés - Heti áttekintés")
    
        if weekly_resource_workload:
            # Create resource workload chart
            workload_data = []
            for name, project_count in weekly_resource_workload.items():
                resource = next((r for r in resources if r.get("Név") == name), None)
                if resource:
                    profession = resource.get("Pozíció", "Ismeretlen")
                    workload_data.append({
                        'Név': name,
                        'Pozíció': profession,
                        'Projektek': project_count,
                        'Terhelés': 'Magas' if project_count > 2 else 'Normál' if project_count > 0 else 'Alacsony'
                    })
            
            if workload_data:
                workload_df = pd.DataFrame(workload_data)
                
                # Color mapping for workload
                color_map = {'Alacsony': '#28a745', 'Normál': '#ffc107', 'Magas': '#dc3545'}
                workload_df['Szín'] = workload_df['Terhelés'].map(color_map)
                
                fig_workload = px.bar(
                    workload_df,
                    x='Név',
                    y='Projektek',
                    color='Terhelés',
                    title="Erőforrás terhelés (projektek száma)",
                    color_discrete_map=color_map,
                    hover_data=['Pozíció']
                )
                fig_workload.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_workload, use_container_width=True)
                
                # Resource recommendations
                st.write("**Erőforrás ajánlások:**")
                for _, row in workload_df.iterrows():
                    if row['Terhelés'] == 'Magas':
                        st.warning(f"⚠️ **{row['Név']}** ({row['Pozíció']}) - {row['Projektek']} projektben dolgozik")
                    elif row['Terhelés'] == 'Alacsony':
                        st.info(f"💡 **{row['Név']}** ({row['Pozíció']}) - további feladatokhoz rendelhető")
            else:
                st.info("Nincs elérhető erőforrás adat.")
        else:
            st.info("Nincs erőforrás terhelés adat.")

    with col2:
        st.subheader("📋 Heti projekt feladatok")
        
        if weekly_tasks:
            # Group tasks by location for better planning
            location_groups = {}
            for task in weekly_tasks:
                for location in task['locations']:
                    if location not in location_groups:
                        location_groups[location] = []
                    location_groups[location].append(task)
            
            for location, tasks in location_groups.items():
                with st.expander(f"📍 {location} ({len(tasks)} projekt)", expanded=True):
                    for task in tasks:
                        status_emoji = {
                            "Folyamatban": "🔄",
                            "Késésben": "⚠️",
                            "Tervezés alatt": "📋"
                        }.get(task['status'], "❓")
                        
                        progress_color = "🟢" if task['progress'] > 75 else "🟡" if task['progress'] > 50 else "🔴"
                        
                        st.write(f"""
                        {status_emoji} **{task['project']}**  
                        📊 Haladás: {progress_color} {task['progress']}%  
                        👥 Csapat: {task['members']} fő
                        """)
        else:
            st.info("Nincs aktív projekt a kiválasztott héten.")

    st.markdown("---")

    # Weekly Schedule Planning
    st.subheader("📅 Heti ütemterv tervezés")

    # Create weekly schedule grid
    days = ['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap']
    day_dates = [(week_start + timedelta(days=i)).strftime('%m-%d') for i in range(7)]

    # Create schedule data
    schedule_data = []
    for i, (day, date) in enumerate(zip(days, day_dates)):
        # Count projects active on this day
        active_projects = 0
        for task in weekly_tasks:
            # Simple logic: if project is active this week, it's active every day
            active_projects += 1
        
        schedule_data.append({
            'Nap': day,
            'Dátum': date,
            'Aktív projektek': active_projects,
            'Szükséges emberek': total_required_people if active_projects > 0 else 0
        })

    if schedule_data:
        schedule_df = pd.DataFrame(schedule_data)
        
        # Create weekly schedule chart
        fig_schedule = px.bar(
            schedule_df,
            x='Nap',
            y='Aktív projektek',
            title="Heti projekt terhelés",
            color='Aktív projektek',
            color_continuous_scale='Blues',
            hover_data=['Dátum', 'Szükséges emberek']
        )
        fig_schedule.update_layout(height=300)
        st.plotly_chart(fig_schedule, use_container_width=True)
        
        # Weekly planning recommendations
        st.subheader("🤖 AI Tervezési ajánlások")
        
        recommendations = []
        
        # Resource recommendations
        if overloaded_resources > 0:
            recommendations.append("⚠️ **Erőforrás optimalizálás:** Néhány dolgozó túlterhelt. Fontolj meg új emberek felvételét vagy feladatok átszervezését.")
        
        if available_this_week < total_required_people:
            recommendations.append("👥 **Személyzet hiány:** Nincs elég elérhető ember a tervezett feladatokhoz. Keress alvállalkozókat vagy halaszd el a feladatokat.")
        
        # Project recommendations
        low_progress_weekly = [task for task in weekly_tasks if task['progress'] < 30]
        if low_progress_weekly:
            recommendations.append("📉 **Lassú haladás:** Néhány projekt lassabban halad, mint tervezve. Növeld a csapat méretét vagy optimalizáld a folyamatokat.")
        
        # Weather and external factors (simulated)
        recommendations.append("🌤️ **Időjárás figyelés:** Ellenőrizd a heti időjárás előrejelzést a kültéri munkákhoz.")
        recommendations.append("📋 **Anyagellátás:** Győződj meg róla, hogy minden szükséges anyag rendelkezésre áll a tervezett munkákhoz.")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.success("✅ Minden rendben! A heti tervezés optimális.")

st.markdown("---")
st.caption("💡 **Tipp:** Használd a fenti tabokat a különböző területek megtekintéséhez.")
