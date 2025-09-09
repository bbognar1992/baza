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


def login_page():
    # Use only Streamlit components for layout and styling
    with st.container():
        # Center the login form using columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.subheader("Please enter your credentials")
            username = st.text_input("Username", key="username_input")
            password = st.text_input("Password", type='password', key="password_input")
            login_btn = st.button("Login", use_container_width=True)
            if login_btn:
                if check_login(username, password):
                    st.success("✅ Logged in successfully!")
                    st.switch_page("pages/Home.py")
                else:
                    st.error("❌ Invalid credentials")

def check_login(username, password):
    # Replace this with your actual login logic (database, API calls, etc.)
    return username == "admin" and password == "admin"

if __name__ == "__main__":
    login_page()
