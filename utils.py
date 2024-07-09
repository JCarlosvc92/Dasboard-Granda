import streamlit as st

# Sample user database
users_db = {
    "admin": {"password": "admin_pass", "role": "admin"},
    "user": {"password": "user_pass", "role": "user"}
}

def check_credentials(username, password):
    user = users_db.get(username)
    if user and user["password"] == password:
        return True
    return False

def login_user(username):
    user_role = users_db[username]["role"]
    st.session_state['logged_in'] = True
    st.session_state['user_role'] = user_role
    return user_role

def is_logged_in():
    return st.session_state.get('logged_in', False)

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
