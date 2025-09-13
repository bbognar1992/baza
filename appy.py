import streamlit as st
from default_data import ensure_base_session_state

# Configure page
st.set_page_config(
    page_title="ÉpítAI",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
ensure_base_session_state(st)

if __name__ == "__main__":
    # Check if user is already logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    has_projects = len(st.session_state.get("projects", [])) > 0
    
    if is_logged_in or has_projects:
        # User is logged in, redirect to landing page with insights
        st.switch_page("pages/landing.py")
    else:
        # User is not logged in, redirect to login page
        st.switch_page("pages/login.py")
