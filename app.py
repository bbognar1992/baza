import streamlit as st

if __name__ == "__main__":
    # Check if user is already logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    
    if is_logged_in:
        # User is logged in, redirect to landing page with insights
        st.switch_page("pages/home.py")
    else:
        # User is not logged in, redirect to login page
        st.switch_page("pages/landing.py")
