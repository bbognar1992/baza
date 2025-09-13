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
    st.sidebar.page_link('pages/home.py', label='Főoldal')
    st.sidebar.page_link('pages/projects.py', label='Projektek')
    st.sidebar.page_link('pages/resources.py', label='Erőforrások')
    st.sidebar.page_link('pages/scheduling.py', label='Ütemezés')

    st.sidebar.markdown("### 🤖 AI Asszisztensek")
    st.sidebar.page_link('pages/material_quote_ai.py', label='AI Ajánlatkérés')
    st.sidebar.page_link('pages/contract_creation_ai.py', label='AI Szerződés')

    st.sidebar.markdown("### ⚙️ Beállítások")
    st.sidebar.page_link('pages/profession_types.py', label='Szakmák')
    st.sidebar.page_link('pages/project_types.py', label='Projekt Típusok')
    
    # Logout section
    st.sidebar.markdown("---")
    if st.sidebar.button("Kijelentkezés", use_container_width=True, key="sidebar_logout"):
        logout_user()

def logout_user():
    """Redirect to logout page"""
    # Redirect to logout page (logout page will handle session clearing)
    st.switch_page("pages/logout.py")

def handle_user_not_logged_in():
    """Handle user not logged in"""
    if not st.session_state.get("user_logged_in", False):
        st.switch_page("pages/login.py")

def set_current_page(page_name):
    """Set the current page name for navbar highlighting"""
    st.session_state.current_page = page_name
