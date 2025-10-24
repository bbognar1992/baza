import streamlit as st
from default_data import get_default_phases

def render_team_tab(project, project_index):
    """Render the team tab for project details."""
    st.subheader("👥 Dolgozók a projekten")
    members = project.get("members", [])
    if members:
        # Group members by their profession/position
        profession_groups = {}
        member_details = {}
        
        for member_name in members:
            # Find the resource details
            member_resource = None
            member_index = None
            for idx, resource in enumerate(st.session_state.resources):
                if resource.get("Név") == member_name:
                    member_resource = resource
                    member_index = idx
                    break
            
            if member_resource:
                # Use position as profession, fallback to type if position is empty
                profession = member_resource.get('Pozíció', 'Nincs megadva')
                if profession == 'Nincs megadva' or not profession.strip():
                    profession = member_resource.get('Típus', 'Ismeretlen')
                
                # Group by profession
                if profession not in profession_groups:
                    profession_groups[profession] = []
                
                profession_groups[profession].append({
                    'name': member_name,
                    'resource': member_resource,
                    'index': member_index
                })
                member_details[member_name] = {
                    'resource': member_resource,
                    'index': member_index
                }
        
        st.write(f"A projekt **{len(members)}** tagot tartalmaz **{len(profession_groups)}** szakmában:")
        st.write("")  # Add some spacing
        
        # Calculate work hours for each member based on completed tasks
        phases_def = get_default_phases()
        member_work_hours = {}
        
        # Initialize work hours for all members
        for member_name in members:
            member_work_hours[member_name] = {
                'total_hours': 0,
                'total_cost': 0,
                'tasks_completed': 0,
                'hourly_rate': 0
            }
            
            # Get member's hourly rate
            member_resource = member_details[member_name]['resource']
            hourly_rate = member_resource.get('Órabér', 0)
            member_work_hours[member_name]['hourly_rate'] = hourly_rate
        
        # Calculate work hours based on completed tasks
        for pi, phase in enumerate(phases_def):
            if pi < len(project.get("phases_checked", [])):
                for ti, task in enumerate(phase["tasks"]):
                    if project["phases_checked"][pi][ti]:  # Task is completed
                        # Get task details
                        if isinstance(task, dict):
                            task_duration_days = task.get("duration_days", 1)
                            required_people = task.get("required_people", 1)
                            task_profession = task.get("profession", "")
                            
                            # Calculate hours per person for this task (8 hours per day)
                            hours_per_person = (task_duration_days * 8) / max(required_people, 1)
                            
                            # Find members who could work on this task
                            for member_name in members:
                                member_resource = member_details[member_name]['resource']
                                member_profession = member_resource.get('Pozíció', '')
                                if not member_profession.strip():
                                    member_profession = member_resource.get('Típus', '')
                                
                                # If member's profession matches task profession or if no specific profession required
                                if not task_profession or task_profession == member_profession:
                                    member_work_hours[member_name]['total_hours'] += hours_per_person
                                    member_work_hours[member_name]['tasks_completed'] += 1
                                    member_work_hours[member_name]['total_cost'] += hours_per_person * member_work_hours[member_name]['hourly_rate']
        
        # Display each profession group in separate panels
        for profession, group_members in profession_groups.items():
            with st.expander(f"🛠️ {profession} ({len(group_members)} tag)", expanded=True):
                # Create a table for better organization
                for member_data in group_members:
                    member_name = member_data['name']
                    member_resource = member_data['resource']
                    member_index = member_data['index']
                    
                    # Get work hours data
                    work_data = member_work_hours[member_name]
                    
                    # Create columns for member info and work hours
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        member_type = member_resource.get('Típus', 'Ismeretlen')
                        member_availability = member_resource.get('Elérhetőség', 'Elérhető')
                        
                        if st.button(f"👤 {member_name}", 
                                   key=f"member_link_{profession}_{member_name}", 
                                   help=f"Kattints a '{member_name}' erőforrás részleteinek megtekintéséhez",
                                   use_container_width=True):
                            # Set the selected resource and navigate to resource details
                            st.session_state.selected_resource_index = member_index
                            st.switch_page("pages/resource_details.py")
                        
                        st.caption(f"{member_type} ({member_availability})")
                    
                    with col2:
                        st.metric("⏱️ Munkaóra", f"{work_data['total_hours']:.1f} h")
                    
                    with col3:
                        st.metric("💰 Költség", f"{work_data['total_cost']:,.0f} Ft")
                    
                    with col4:
                        st.metric("📋 Feladatok", f"{work_data['tasks_completed']}")
                    
                    st.divider()
        
        # Summary section
        st.subheader("📊 Összesítés")
        total_hours = sum(data['total_hours'] for data in member_work_hours.values())
        total_cost = sum(data['total_cost'] for data in member_work_hours.values())
        total_tasks = sum(data['tasks_completed'] for data in member_work_hours.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Összes munkaóra", f"{total_hours:.1f} h")
        with col2:
            st.metric("💰 Összes költség", f"{total_cost:,.0f} Ft")
        with col3:
            st.metric("📋 Összes feladat", f"{total_tasks}")
            
    else:
        st.info("Nincs hozzárendelt tag a projekthez.")
