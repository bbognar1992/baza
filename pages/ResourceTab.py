import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation

st.set_page_config(page_title="Erőforrás Dashboard – ÉpítAI", layout="wide")

# Initialize session state
ensure_base_session_state(st)

# Render sidebar navigation
render_sidebar_navigation()

st.title("👥 Erőforrás Dashboard")

# Calculate key metrics
resources = st.session_state.resources
projects = st.session_state.projects

# Resource utilization
total_resources = len(resources)
available_resources = len([r for r in resources if r.get("Elérhetőség") == "Elérhető"])

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

# Resource workload analysis
st.subheader("📊 Erőforrás terhelés elemzés")

# Calculate resource workload
resource_workload = {}
for resource in resources:
    if resource.get("Elérhetőség") == "Elérhető":
        # Count how many projects this resource is assigned to
        assigned_projects = 0
        for project in projects:
            if project.get("status") in ["Folyamatban", "Késésben"]:
                if resource.get("Név") in project.get("members", []):
                    assigned_projects += 1
        resource_workload[resource.get("Név", "Névtelen")] = assigned_projects

if resource_workload:
    # Create resource workload chart
    workload_data = []
    for name, project_count in resource_workload.items():
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

st.markdown("---")

# Resource details table
st.subheader("📋 Erőforrás részletek")

# Create a detailed resource table
if resources:
    # Prepare data for the table
    resource_data = []
    for resource in resources:
        # Count assigned projects
        assigned_projects = 0
        project_names = []
        for project in projects:
            if resource.get("Név") in project.get("members", []):
                assigned_projects += 1
                project_names.append(project.get("name", "Névtelen"))
        
        resource_data.append({
            'Név': resource.get('Név', 'Névtelen'),
            'Pozíció': resource.get('Pozíció', 'Nincs megadva'),
            'Típus': resource.get('Típus', 'Nincs megadva'),
            'Elérhetőség': resource.get('Elérhetőség', 'Ismeretlen'),
            'Órabér': f"{resource.get('Órabér', 0):,} Ft" if resource.get('Órabér', 0) > 0 else "N/A",
            'Tapasztalat': f"{resource.get('Tapasztalat', 0)} év",
            'Projektek': assigned_projects,
            'Aktív projektek': ', '.join(project_names[:3]) + ('...' if len(project_names) > 3 else '')
        })
    
    # Display as a table
    resource_df = pd.DataFrame(resource_data)
    st.dataframe(
        resource_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Név": st.column_config.TextColumn("Név", width="medium"),
            "Pozíció": st.column_config.TextColumn("Pozíció", width="medium"),
            "Típus": st.column_config.TextColumn("Típus", width="small"),
            "Elérhetőség": st.column_config.TextColumn("Elérhetőség", width="small"),
            "Órabér": st.column_config.TextColumn("Órabér", width="small"),
            "Tapasztalat": st.column_config.TextColumn("Tapasztalat", width="small"),
            "Projektek": st.column_config.NumberColumn("Projektek", width="small"),
            "Aktív projektek": st.column_config.TextColumn("Aktív projektek", width="large")
        }
    )
else:
    st.info("Nincs erőforrás adat megjelenítéshez.")

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

# Check for overloaded resources
overloaded_count = len([name for name, count in resource_workload.items() if count > 2])
if overloaded_count > 0:
    resource_alerts.append(f"⚠️ **{overloaded_count} erőforrás** túlterhelt (3+ projekt)")

if resource_alerts:
    for alert in resource_alerts:
        st.warning(alert)
else:
    st.success("✅ Nincs aktív erőforrás figyelmeztetés")

st.markdown("---")

# Quick actions
st.subheader("🚀 Gyors műveletek")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Új projekt", use_container_width=True, key="resourcetab_new_project"):
        st.switch_page("pages/Projects.py")

with col2:
    if st.button("📁 Projektek", use_container_width=True, key="resourcetab_projects"):
        st.switch_page("pages/Projects.py")

with col3:
    if st.button("👥 Erőforrások", use_container_width=True, key="resourcetab_resources"):
        st.switch_page("pages/Resources.py")

with col4:
    if st.button("📊 Ütemezés", use_container_width=True, key="resourcetab_schedule"):
        st.switch_page("pages/utemezes.py")

st.markdown("---")
st.caption("💡 **Tipp:** Használd a bal oldali menüt a részletes funkciók eléréséhez.")
