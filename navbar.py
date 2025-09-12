import streamlit as st
import base64
from PIL import Image
import io

def create_user_profile_html(name, company, avatar_size=48):
    """Create HTML string for user profile with avatar and company info"""
    user_avatar = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=0D8ABC&color=fff&size={avatar_size * 2}"
    
    html_string = f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <img src="{user_avatar}" alt="Avatar" style="border-radius: 50%; width:{avatar_size}px; height:{avatar_size}px; border:2px solid #0D8ABC;">
        <div>
            <div style="font-weight:600; font-size:1.1rem; color:#0D8ABC;">{name}</div>
            <div style="font-size:0.95rem; color:#888;">{company}</div>
        </div>
    </div>
    """
    return html_string

def render_sidebar_navigation():
    """Render the sidebar navigation that matches the main app"""
    
    # User info
    st.sidebar.markdown(
        create_user_profile_html("Nagy Péter", "NagyBau KFT."),
        unsafe_allow_html=True
    )
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
    
    # Logout section
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Kijelentkezés", use_container_width=True, key="sidebar_logout"):
        logout_user()

def render_navbar():
    """Render a simple header without navigation"""
    
    # Simple header with just the brand
    with st.container():
        col_title, col_logout = st.columns([4, 1])
        
        with col_title:
            st.markdown("### 🏗️ ÉpítAI")
        
        with col_logout:
            if st.button("🚪 Kijelentkezés", use_container_width=True, key="navbar_logout_btn"):
                logout_user()
        
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

def logout_user():
    """Clear session state and redirect to landing page"""
    # Clear all session state except for default data
    for key in list(st.session_state.keys()):
        if key not in ["resources", "profession_types", "project_types"]:  # Keep default data
            del st.session_state[key]

    st.session_state.user_logged_in = False
    # Redirect to landing page
    st.switch_page("pages/Landing.py")

def handle_user_not_logged_in():
    """Handle user not logged in"""
    if not st.session_state.get("user_logged_in", False):
        st.switch_page("pages/Login.py")

def set_current_page(page_name):
    """Set the current page name for navbar highlighting"""
    st.session_state.current_page = page_name
