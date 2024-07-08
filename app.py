import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
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
        <h1 class="title-test">Bienvenido al LCM</h1>
    </div>
""")

# Function for login
def login():
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "Usuario1" and password == "lcm2024":
            st.session_state["logged_in"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

# Function for logout
def logout():
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]

# Function for redirection
def redirect_to_info():
    st.session_state.page = "info"

# Main function
def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    if st.session_state.page == "login":
        if "logged_in" not in st.session_state:
            login()
            if "logged_in" in st.session_state:
                redirect_to_info()
        else:
            redirect_to_info()
    
    if st.session_state.page == "info":
        display_info_page()
        if st.button("Cerrar Sesión"):
            logout()
            st.session_state.page = "login"

def display_info_page():
    st.title("Municipio de Deria")
    st.write("""
    **Municipio de Granada**
    Fundada en 21 de abril de 1524, es conocida como “La gran sultana”, constituyéndose en uno de los asentamientos coloniales más antiguos de Centroamérica. Se distingue por la fusión de elementos arquitectónicos en la construcción de la ciudad.
    """)
    
    # Dividir en dos columnas
    col1, col2 = st.columns(2)
    
    # Menú desplegable para seleccionar el título
    selected_info = col1.radio("Seleccionar información:", ["Extensión territorial", "Limita", "Población estimada",
                                                         "Población urbana", "Población Rural", "Densidad poblacional",
                                                         "Organización Territorial", "Religión más practicada",
                                                         "Principal actividad económica", "Elecciones Municipales"])
    
    # Mostrar la información correspondiente en la segunda columna
    if selected_info == "Extensión territorial":
        col2.write("""
        529.1km², representa el 56.95% del departamento.
        """)
        # Agregar imagen en la segunda columna

    elif selected_info == "Limita":
        col2.write("""
        Al Norte con Tipitapa. 
        Al Sur con Nandaime. 
        Al Este con San Lorenzo y el lago Cocibolca. 
        Al Oeste con Tisma, Masaya, Diría, Diriomo, Nandaime y laguna de apoyo.
        """)
    elif selected_info == "Población estimada":
        col2.write("""
        132,054 que representa el 61.62%
        """)
    # Continuar con el resto de los casos...

if __name__ == "__main__":
    main()
