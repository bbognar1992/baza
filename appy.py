import streamlit as st
from default_data import ensure_base_session_state
from navbar import render_sidebar_navigation

# Configure page
st.set_page_config(
    page_title="ÉpítAI",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
ensure_base_session_state(st)

# Render sidebar navigation
render_sidebar_navigation()

# Main content area
st.title("🏗️ ÉpítAI")
st.write("Üdvözöllek az ÉpítAI alkalmazásban! Használd a bal oldali menüt a navigációhoz.")
