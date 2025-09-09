import streamlit as st

def render_navbar():
    """Render a simple header without navigation"""
    
    # Simple header with just the brand
    with st.container():
        st.markdown("### 🏗️ ÉpítAI")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🏠 Dashboard", use_container_width=True, key="navbar_dashboard_btn"):
                st.switch_page("Home.py")

        with col2:
            if st.button("📁 Projektek", use_container_width=True, key="navbar_projects_btn"):
                st.switch_page("pages/Projects.py")

        with col3:
            if st.button("👥 Erőforrások", use_container_width=True, key="navbar_resources_btn"):
                st.switch_page("pages/Resources.py")

        with col4:
            if st.button("📊 Ütemezés", use_container_width=True, key="navbar_schedule_btn"):
                st.switch_page("pages/utemezes.py")

def set_current_page(page_name):
    """Set the current page name for navbar highlighting"""
    st.session_state.current_page = page_name
