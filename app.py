import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
from streamlit_option_menu import option_menu
from string import Template

# Path to the logo
logo_image_path = "static/img/logo.png"

# Function to load logo and convert to base64
def load_logo(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    return encoded_logo

# HTML Title with style and logo using Template
html_title_template = Template("""
    <style>
    body {
        font-family: 'Oswald', sans-serif;
    }
    .header {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo {
        width: 100px;  /* Adjust the logo size here */
        margin-right: 20px;
    }
    .title-test {
        font-weight: bold;
        padding: 3px;
        border-radius: 6px;
    }
    .description {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
    <div class="header">
        <img src="data:image/png;base64,$logo" class="logo">
        <h1 class="title-test">Bienvenido al Municipio de Granada</h1>
    </div>
""")

# Function for login
def login():
    st.sidebar.title("Inicio de Sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Iniciar Sesión"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            return True
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")
    return False

# Main function
def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    if not login():
        return
    
    # Redirection after successful login
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.experimental_set_query_params(page="client_view")

    # Navigation Menu
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Caracterización", "Administrador", "Cerrar Sesion"],
        icons=["house", "person", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Inicio" or st.experimental_get_query_params().get("page", [""])[0] == "client_view":
        st.session_state.admin = False
        client_view()

    elif selected == "Caracterización":
        st.session_state.admin = False
        caracterizacion()

    elif selected == "Administrador":
        st.session_state.admin = True
        admin_dashboard()

    elif selected == "Cerrar Sesion":
        if "logged_in" in st.session_state:
            del st.session_state["logged_in"]

    else:
        st.session_state.admin = False
        client_view()

# The rest of your functions (caracterizacion, admin_dashboard, client_view, etc.) remain unchanged

if __name__ == "__main__":
    main()
