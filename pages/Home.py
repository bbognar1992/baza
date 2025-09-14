import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from default_data import ensure_base_session_state
from components.sidebar import render_sidebar_navigation, handle_user_not_logged_in

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
today = datetime.now().date()

# Project status distribution
status_counts = {}
for project in projects:
    status = project.get("status", "Ismeretlen")
    status_counts[status] = status_counts.get(status, 0) + 1

# Progress metrics
total_projects = len(projects)
active_projects = len([p for p in projects if p.get("status") == "Folyamatban"])
completed_projects = len([p for p in projects if p.get("status") == "Lezárt"])
overdue_projects = len([p for p in projects if p.get("status") == "Késésben"])

# Overdue projects (past end date)
overdue_projects_list = []
for project in projects:
    try:
        end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
        if end_date < today and project.get("status") not in ["Lezárt"]:
            overdue_projects_list.append(project)
    except:
        pass

# Resource utilization
total_resources = len(resources)
available_resources = len([r for r in resources if r.get("Elérhetőség") == "Elérhető"])

# Check for resource overload (working on multiple projects)
resource_overload = {}
for resource in resources:
    if resource.get("Elérhetőség") == "Elérhető":
        assigned_projects = 0
        for project in projects:
            if project.get("status") in ["Folyamatban", "Késésben"]:
                if resource.get("Név") in project.get("members", []):
                    assigned_projects += 1
        if assigned_projects > 1:
            resource_overload[resource.get("Név", "Névtelen")] = assigned_projects

# Projects by location
location_counts = {}
for project in projects:
    locations = project.get("locations", [])
    for location in locations:
        location_counts[location] = location_counts.get(location, 0) + 1

# Create tabs for better organization
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Projekt státusz", 
    "👥 Erőforrások", 
    "💰 Anyag & Költség", 
    "🌤️ Időjárás", 
    "🚨 Riasztások"
])

# Simulate material price changes (in real app, this would come from external API)
material_price_changes = {
    "Vasanyag": "+10%",
    "Beton": "+5%",
    "Faanyag": "-2%",
    "Csempe": "+8%"
}

# Simulate budget deviations
budget_deviations = {
    "Projekt A": "+15% (túllépés)",
    "Projekt B": "-5% (takarékosság)",
    "Projekt C": "+25% (sürgős figyelem)"
}

# Simulate weather forecast by project location
weather_forecast = {
    "Budapest": ["☀️ 22°C", "⛅ 20°C", "🌧️ 18°C", "☀️ 24°C", "⛅ 21°C", "🌧️ 19°C", "☀️ 23°C"],
    "Debrecen": ["☀️ 25°C", "☀️ 27°C", "⛅ 23°C", "🌧️ 20°C", "☀️ 26°C", "☀️ 28°C", "⛅ 24°C"],
    "Szeged": ["⛅ 24°C", "🌧️ 21°C", "🌧️ 19°C", "☀️ 25°C", "⛅ 22°C", "☀️ 26°C", "☀️ 27°C"]
}

days = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

with tab1:
    # 1. Projekt státusz összefoglaló
    st.subheader("📊 Projekt státusz összefoglaló")
    col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
            label="Aktív projektek száma",
            value=active_projects,
            delta=f"{active_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
    )

with col2:
    st.metric(
            label="Befejezett projektek száma",
            value=completed_projects,
            delta=f"{completed_projects/total_projects*100:.1f}%" if total_projects > 0 else "0%"
    )

with col3:
    st.metric(
            label="Késésben lévő projektek",
            value=overdue_projects,
            delta=f"⚠️ {overdue_projects}" if overdue_projects > 0 else "✅ 0"
    )

with col4:
    st.metric(
            label="Összes projekt",
            value=total_projects,
        delta=None
    )

st.markdown("---")

# Additional project details
st.subheader("📈 Projekt részletek")

# Project status distribution chart
if status_counts:
    col1, col2 = st.columns(2)

    with col1:
        # Create pie chart
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
        if location_counts:
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
else:
    st.info("Nincs projekt adat megjelenítéshez.")

with tab2:
    # 2. Erőforrások állapota
    st.subheader("👥 Erőforrások állapota")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Összes erőforrás",
            value=total_resources,
            delta="(alkalmazott, alvállalkozó, eszköz)"
        )
    
    with col2:
        available_ratio = available_resources / total_resources if total_resources > 0 else 0
        st.metric(
            label="Szabad / lefoglalt arány",
            value=f"{available_resources}/{total_resources - available_resources}",
            delta=f"{available_ratio*100:.1f}% szabad"
        )
    
    with col3:
        overloaded_count = len(resource_overload)
        st.metric(
            label="Túlterhelt erőforrások",
            value=overloaded_count,
            delta=f"⚠️ {overloaded_count}" if overloaded_count > 0 else "✅ 0"
        )

    # Show resource overload details
    if resource_overload:
        st.warning("⚠️ **Túlterhelés figyelmeztetés:**")
        for name, project_count in resource_overload.items():
            st.write(f"• **{name}** - {project_count} projekten dolgozik egyszerre")

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

with tab3:
    # 3. Anyag- és költségriasztások
    st.subheader("💰 Anyag- és költségriasztások")
    
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Anyagár változások (az előző hónaphoz képest):**")
        for material, change in material_price_changes.items():
            if "+" in change:
                st.error(f"📈 {material}: {change}")
            else:
                st.success(f"📉 {material}: {change}")

    with col2:
        st.write("**Költségkerethez képest eltérés:**")
        for project, deviation in budget_deviations.items():
            if "túllépés" in deviation or "+" in deviation and int(deviation.split("+")[1].split("%")[0]) > 10:
                st.error(f"⚠️ {project}: {deviation}")
            else:
                st.success(f"✅ {project}: {deviation}")

    st.markdown("---")

    # Cost analysis chart
    st.subheader("📊 Költség elemzés")
    
    # Create cost deviation chart
    cost_data = []
    for project, deviation in budget_deviations.items():
        percentage = int(deviation.split("+")[1].split("%")[0]) if "+" in deviation else int(deviation.split("-")[1].split("%")[0])
        if "-" in deviation:
            percentage = -percentage
        cost_data.append({
            'Projekt': project,
            'Eltérés (%)': percentage,
            'Típus': 'Túllépés' if percentage > 10 else 'Takarékosság' if percentage < 0 else 'Normál'
        })
    
    if cost_data:
        cost_df = pd.DataFrame(cost_data)
        fig_cost = px.bar(
            cost_df,
            x='Projekt',
            y='Eltérés (%)',
            color='Típus',
            title="Projekt költség eltérések",
            color_discrete_map={'Túllépés': '#dc3545', 'Takarékosság': '#28a745', 'Normál': '#ffc107'}
        )
        fig_cost.update_layout(height=400)
        st.plotly_chart(fig_cost, use_container_width=True)

with tab4:
    # 4. Időjárás előrejelzés (AI előkészítve)
    st.subheader("🌤️ Időjárás előrejelzés - Következő 7 nap")

    for location, forecast in weather_forecast.items():
        if location in [loc for project in projects for loc in project.get("locations", [])]:
            st.write(f"**📍 {location}:**")
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            cols = [col1, col2, col3, col4, col5, col6, col7]
            
            for i, (day, weather) in enumerate(zip(days, forecast)):
                with cols[i]:
                    st.write(f"**{day}**")
                    st.write(weather)
            
            # Weather warnings
            if "🌧️" in forecast:
                st.warning(f"⚠️ **{location}:** Eső várható, betonozást halaszd el!")

    st.markdown("---")

    # Weather impact analysis
    st.subheader("📈 Időjárás hatás elemzés")
    
    # Count rainy days by location
    weather_impact = {}
    for location, forecast in weather_forecast.items():
        rainy_days = sum(1 for day in forecast if "🌧️" in day)
        weather_impact[location] = {
            'Esős napok': rainy_days,
            'Hatás': 'Magas' if rainy_days > 2 else 'Közepes' if rainy_days > 0 else 'Alacsony'
        }
    
    if weather_impact:
        impact_df = pd.DataFrame([
            {'Helyszín': loc, 'Esős napok': data['Esős napok'], 'Hatás': data['Hatás']}
            for loc, data in weather_impact.items()
        ])
        
        fig_weather = px.bar(
            impact_df,
            x='Helyszín',
            y='Esős napok',
            color='Hatás',
            title="Időjárás hatás helyszín szerint",
            color_discrete_map={'Magas': '#dc3545', 'Közepes': '#ffc107', 'Alacsony': '#28a745'}
        )
        fig_weather.update_layout(height=400)
        st.plotly_chart(fig_weather, use_container_width=True)

with tab5:
    # 5. Riasztások (Alert box)
    st.subheader("🚨 Riasztások")

    # Collect all alerts
    red_alerts = []  # sürgős teendő
    yellow_alerts = []  # figyelmeztetés
    green_alerts = []  # minden rendben

    # Red alerts (urgent)
    if len(overdue_projects_list) > 0:
        red_alerts.append(f"🔴 **Sürgős:** {len(overdue_projects_list)} lejárt projekt")

    if any("túllépés" in dev for dev in budget_deviations.values()):
        red_alerts.append("🔴 **Sürgős:** Költségtúllépés észlelve")

    if any("🌧️" in forecast for forecast in weather_forecast.values()):
        red_alerts.append("🔴 **Sürgős:** Eső várható - kültéri munkák halasztása")

    # Yellow alerts (warnings)
    if overdue_projects > 0:
        yellow_alerts.append(f"🟡 **Figyelmeztetés:** {overdue_projects} projekt késésben")

    if len(resource_overload) > 0:
        yellow_alerts.append(f"🟡 **Figyelmeztetés:** {len(resource_overload)} erőforrás túlterhelt")

    # Check for upcoming deadlines (next 7 days)
    upcoming_deadlines = []
    for project in projects:
        try:
            end_date = datetime.strptime(project.get("end", "2025-12-31"), "%Y-%m-%d").date()
            days_until = (end_date - today).days
            if 0 <= days_until <= 7 and project.get("status") not in ["Lezárt"]:
                upcoming_deadlines.append(project)
        except:
            pass

    if upcoming_deadlines:
        yellow_alerts.append(f"🟡 **Figyelmeztetés:** {len(upcoming_deadlines)} projekt határidője közeledik")

    # Green alerts (all good)
    if len(red_alerts) == 0 and len(yellow_alerts) == 0:
        green_alerts.append("🟢 **Minden rendben:** Nincs aktív riasztás")

    # Display alerts
    if red_alerts:
        for alert in red_alerts:
            st.error(alert)

    if yellow_alerts:
        for alert in yellow_alerts:
            st.warning(alert)

    if green_alerts:
        for alert in green_alerts:
            st.success(alert)

    st.markdown("---")
    
    # Alert summary
    st.subheader("📊 Riasztás összefoglaló")
    
    alert_summary = {
        'Sürgős (Piros)': len(red_alerts),
        'Figyelmeztetés (Sárga)': len(yellow_alerts),
        'Rendben (Zöld)': len(green_alerts)
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sürgős riasztások", len(red_alerts), delta="🔴")
    
    with col2:
        st.metric("Figyelmeztetések", len(yellow_alerts), delta="🟡")
    
    with col3:
        st.metric("Rendben", len(green_alerts), delta="🟢")

st.markdown("---")
st.caption("💡 **Tipp:** Használd a fenti tabokat a különböző területek megtekintéséhez.")