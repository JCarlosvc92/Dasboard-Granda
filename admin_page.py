import streamlit as st
import pandas as pd
from utils import logout_user

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    # File upload functionality
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

    if st.button("Logout"):
        logout_user()
        st.experimental_rerun()