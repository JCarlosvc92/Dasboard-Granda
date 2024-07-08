import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
import time
from streamlit_option_menu import option_menu
from string import Template

# Path to the logo
logo_image_path = "static/img/logo.png"

def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "admin" and password == "lcm2024":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

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
        <h1 class="title-test">Bienvenido a LCM</h1>
    </div>
""")

def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    # Check if logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login()
        return
    
    # Navigation Menu
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Caracterización", "Administrador", "Cerrar Sesion"],
        icons=["house", "person", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
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

    else:
        st.session_state.admin = False
        client_view()

def caracterizacion():
    st.title("Municipio de Deria")
    st.write("""
    **Municipio de Granada**
    Fundada en 21 de abril de 1524, es conocida como “La gran sultana”, constituyéndose en uno de los asentamientos coloniales más antiguos de Centroamérica. Se distingue por la fusión de elementos arquitectónicos en la construcción de la ciudad.
    """)
    
    # Resto del código para caracterización...

def cargar_csv():
    st.subheader("Cargar CSV")
    uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        st.success("Archivo CSV cargado exitosamente")
        return df
    return None

def descargar_csv(dataframe):
    if dataframe is not None:
        csv = dataframe.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="datos.csv">Descargar CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

def admin_dashboard():
    st.title("Dashboard de Administrador")
    df = cargar_csv()
    if df is not None:
        st.subheader("Guardar CSV")
        if st.button("Descargar datos"):
            descargar_csv(df)


def client_view():
    static_csv_path = "static/data/LCMG1_Granada2024.csv"

    df = pd.read_csv(static_csv_path, header=0)
    
    # Resto del código para la vista del cliente...

if __name__ == "__main__":
    main()
