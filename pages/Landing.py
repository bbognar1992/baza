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
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
