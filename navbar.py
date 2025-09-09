import streamlit as st

def render_sidebar_navigation():
    """Render the sidebar navigation that matches the main app"""
    
    # Profile picture placeholder (you can replace with actual image)
    col1, col2, col3 = st.sidebar.columns([3, 2, 1])
    with col2:
        st.sidebar.image("assets/profile.png", width=80)
    
    # User name (you can make this dynamic based on session state)
    st.sidebar.markdown("**Admin User**")
    st.sidebar.markdown("*Építésvezető*")

    st.sidebar.markdown("### 📁 Projektmenedzsment")
    st.sidebar.page_link('pages/Home.py', label='Főoldal')
    st.sidebar.page_link('pages/Projects.py', label='Projektek')
    st.sidebar.page_link('pages/Resources.py', label='Erőforrások')
    st.sidebar.page_link('pages/utemezes.py', label='Ütemezés')

    st.sidebar.markdown("### 🤖 AI Asszisztensek")
    st.sidebar.page_link('pages/AnyagarAjanlatkeresAI.py', label='AI Ajánlatkérés')
    st.sidebar.page_link('pages/SzerzodeskeszitesAI.py', label='AI Szerződés')

    st.sidebar.markdown("### ⚙️ Beállítások")
    st.sidebar.page_link('pages/ProfessionTypes.py', label='Szakmák')
    st.sidebar.page_link('pages/ProjektTipusok.py', label='Projekt Típusok')

def render_navbar():
    """Render a simple header without navigation"""
    
    # Simple header with just the brand
    with st.container():
        st.markdown("### 🏗️ ÉpítAI")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🏠 Dashboard", use_container_width=True, key="navbar_dashboard_btn"):
                st.switch_page("pages/Home.py")

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
