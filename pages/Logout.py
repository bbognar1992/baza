import streamlit as st
from default_data import ensure_base_session_state

# Configure page
st.set_page_config(
    page_title="ÉpítAI - Kijelentkezés",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def logout_page():
    """Logout page with goodbye message"""
    with st.container():
        # Center the content using columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Header section
            st.markdown("## 👋 Sajnáljuk, hogy távozik!")
            
            # Goodbye message
            with st.container(border=True):
                st.markdown("""
                ### Kijelentkezett

                Az Ön munkamenete ezen az eszközön befejeződött. Bármikor újra bejelentkezhet.
                """)
                
                if st.button("Újra bejelentkezés", type="secondary"):
                    st.switch_page("pages/Login.py")


def perform_logout():
    """Clear session state and show logout page"""
    # Clear all session state except for default data
    for key in list(st.session_state.keys()):
        if key not in ["resources", "profession_types", "project_types"]:  # Keep default data
            del st.session_state[key]
    
    st.session_state.user_logged_in = False

if __name__ == "__main__":
    # Perform logout if user was logged in
    if st.session_state.get("user_logged_in", False):
        perform_logout()
    
    # Show logout page
    logout_page()
