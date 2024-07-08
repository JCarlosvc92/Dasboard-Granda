import streamlit as st
import pandas as pd
import base64
import plotly.express as px
from string import Template

# Path to the logo
logo_image_path = "static/img/logo.png"

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
        <h1 class="title-test">Bienvenido al Municipio de Granada </h1>
    </div>
""")

# Path to the logo
logo_image_path = "static/img/logo.png"

def login():
    st.sidebar.title("Inicio de Sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Iniciar Sesión"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

def load_logo(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    return encoded_logo

def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    login()  # Call login function to authenticate user
    
    # Check if user is logged in
    if st.session_state.get("logged_in"):
        st.success("Inicio de sesión exitoso")
        
        # Navigation Menu
        selected = st.selectbox(
            "Selecciona una opción:",
            ["Inicio", "Caracterización", "Administrador", "Cerrar Sesión"]
        )

        if selected == "Inicio":
            st.session_state.admin = False
            client_view()

        elif selected == "Caracterización":
            st.session_state.admin = False
            caracterizacion()

        elif selected == "Administrador":
            st.session_state.admin = True
            admin_dashboard()

        elif selected == "Cerrar Sesión":
            st.session_state["logged_in"] = False
            st.info("Has cerrado sesión.")
    
    else:
        st.warning("Por favor, inicia sesión para acceder.")

def caracterizacion():
    st.title("Municipio de Deria")
    st.write("""
    **Municipio de Granada**
    Fundada en 21 de abril de 1524, es conocida como “La gran sultana”, constituyéndose en uno de los asentamientos coloniales más antiguos de Centroamérica. Se distingue por la fusión de elementos arquitectónicos en la construcción de la ciudad.
    """)
    
    # Continuar con el resto de la función caracterización...

def admin_dashboard():
    st.title("Dashboard de Administrador")
    # Implementar el dashboard de administrador aquí...

def client_view():
    static_csv_path = "static/data/LCMG1_Granada2024.csv"
    df = pd.read_csv(static_csv_path, header=0)
    # Implementar la vista de cliente aquí...

if __name__ == "__main__":
    main()
