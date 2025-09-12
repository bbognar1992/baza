import streamlit as st
from default_data import ensure_base_session_state

# Configure page
st.set_page_config(
    page_title="ÉpítAI - Bejelentkezés",
    page_icon="🔐",
    layout="wide"
)

# Initialize session state
ensure_base_session_state(st)

def check_login(username, password):
    """Check login credentials"""
    # Replace this with your actual login logic (database, API calls, etc.)
    return username == "admin" and password == "admin"

def login_page():
    """Modern login page using only Streamlit components"""
    with st.container():
        # Center the login form using columns
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Header section
            st.markdown("## 🏗️ ÉpítAI")
            
            # Login form using st.form for better UX
            with st.form("login_form"):
                st.markdown("### 🔐 Bejelentkezés")
                
                # Input fields
                username = st.text_input(
                    "Felhasználónév", 
                    key="username_input",
                    placeholder="Adja meg a felhasználónevet",
                    help="Írja be a felhasználónevét"
                )
                
                password = st.text_input(
                    "Jelszó", 
                    type='password', 
                    key="password_input",
                    placeholder="Adja meg a jelszót",
                    help="Írja be a jelszavát"
                )
                
                # Login button
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    login_btn = st.form_submit_button(
                        "🚀 Bejelentkezés", 
                        use_container_width=True,
                        type="primary"
                    )
                
                # Login logic
                if login_btn:
                    if check_login(username, password):
                        st.success("✅ Sikeres bejelentkezés!")
                        st.balloons()
                        st.session_state.user_logged_in = True
                        st.switch_page("pages/Home.py")
                    else:
                        st.error("❌ Hibás felhasználónév vagy jelszó")
            
            # Additional info section
            st.markdown("---")
            
            # Info expander
            with st.expander("💡 Bejelentkezési információk", expanded=False):
                st.info("**Tesztelési adatok:**")
                st.code("Felhasználónév: admin\nJelszó: admin")
                st.markdown("Használja ezeket az adatokat a rendszer teszteléséhez.")
            
            # Footer
            st.markdown("---")
            col_footer1, col_footer2, col_footer3 = st.columns(3)
            with col_footer2:
                st.caption("© 2024 ÉpítAI - Construction Management System")

if __name__ == "__main__":
    # Check if user is already logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    
    if is_logged_in:
        # User is already logged in, redirect to home
        st.switch_page("pages/Home.py")
    else:
        # Show login page
        login_page()
