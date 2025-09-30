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

st.markdown('''
<style>
.stApp [data-testid="stToolbar"]{
    display:none;
}
</style>
''', unsafe_allow_html=True)

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
            # Logo
            with st.container(border=False):
                left_co, cent_co,last_co = st.columns(3)
                with cent_co:
                    st.image("assets/logo_sm.png", use_container_width=True)
            
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
                        "Bejelentkezés", 
                        use_container_width=True,
                        type="secondary"
                    )
                
                # Login logic
                if login_btn:
                    if check_login(username, password):
                        st.success("✅ Sikeres bejelentkezés!")
                        st.balloons()
                        st.session_state.user_logged_in = True
                        st.switch_page("pages/home.py")
                    else:
                        st.error("❌ Hibás felhasználónév vagy jelszó")
            

if __name__ == "__main__":
    # Check if user is already logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    
    if is_logged_in:
        # User is already logged in, redirect to home
        st.switch_page("pages/home.py")
    else:
        # Show login page
        login_page()
