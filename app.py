import streamlit as st
from utils import login_user, check_credentials, is_logged_in

# Define the Streamlit app
def main():
    st.set_page_config(page_title="Login Page", layout="centered")
    
    # Custom CSS for background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("static/img/fondo.png");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    if is_logged_in():
        user_role = st.session_state.get('user_role', 'user')
        if user_role == 'admin':
            st.write("Redirecting to Admin Dashboard...")
            st.experimental_rerun()
        else:
            st.write("Redirecting to User Dashboard...")
            st.experimental_rerun()
    else:
        st.title("Login Page")
        st.image("static/img/logo.png", width=200)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")
        
        if login_button:
            if check_credentials(username, password):
                user_role = login_user(username)
                if user_role == 'admin':
                    st.experimental_set_query_params(page='admin')
                    st.write("Redirecting to Admin Dashboard...")
                    st.experimental_rerun()
                else:
                    st.experimental_set_query_params(page='user')
                    st.write("Redirecting to User Dashboard...")
                    st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        
    # Redirect to the appropriate dashboard based on the query parameter
    query_params = st.experimental_get_query_params()
    page = query_params.get('page', [''])[0]
    if page == 'admin':
        import admin_page
        admin_page.show_admin_dashboard()
    elif page == 'user':
        import user_page
        user_page.show_user_dashboard()

if __name__ == "__main__":
    main()
