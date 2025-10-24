import streamlit as st
from default_data import ensure_base_session_state
from database import get_db_session
from models.user import User

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

def check_login(email, password):
    """Check login credentials against database"""
    try:
        with get_db_session() as session:
            # Find user by email
            user = session.query(User).filter(User.email == email).first()
            
            if user and user.check_password(password):
                # Store user info in session state
                st.session_state.current_user = {
                    'user_id': user.user_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'department': user.department
                }
                return True
            return False
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

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
                email = st.text_input(
                    "E-mail", 
                    key="email_input",
                    placeholder="Adja meg a e-mail címét",
                    help="Írja be a e-mail címét"
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
                    if check_login(email, password):
                        st.success("✅ Sikeres bejelentkezés!")
                        st.balloons()
                        st.session_state.user_logged_in = True
                        st.switch_page("pages/home.py")
                    else:
                        st.error("❌ Hibás e-mail cím vagy jelszó")
            

if __name__ == "__main__":
    # Check if user is already logged in
    is_logged_in = st.session_state.get("user_logged_in", False)
    
    if is_logged_in:
        # User is already logged in, redirect to home
        st.switch_page("pages/home.py")
    else:
        # Show login page
        login_page()