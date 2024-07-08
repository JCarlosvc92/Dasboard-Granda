import streamlit as st
import pandas as pd
import base64
from string import Template
import plotly.express as px

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

def plot_question(df, question, graph_type, questions, font_size=18, colors=None):
    # Function to plot the question
    pass  # Implement your plot function here

def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    if "logged_in" not in st.session_state:
        login()
        return
    
    st.title("Bienvenido al Municipio de Granada")
    st.write("""
        Fundada el 21 de abril de 1524, Granada es conocida como “La gran sultana”,
        constituyéndose en uno de los asentamientos coloniales más antiguos de Centroamérica.
        Se distingue por la fusión de elementos arquitectónicos en la construcción de la ciudad.
    """)
    
    # Example of data visualization based on user role
    if st.session_state.get("admin"):
        st.header("Dashboard de Administrador")
        st.write("Aquí se muestra el dashboard y funcionalidades administrativas.")
        # Implementar funcionalidades administrativas

    else:
        st.header("Vista de Cliente")
        st.write("Aquí se muestra la vista para los usuarios regulares.")
        # Implementar funcionalidades para usuarios regulares

if __name__ == "__main__":
    main()
