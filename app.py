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
        <h1 class="title-test">Bienvenido al Municipio de Granada</h1>
    </div>
""")

# Function for login
def login():
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

# Function for logout
def logout():
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]

# Main function
def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
    # Check if user is logged in
    if "logged_in" not in st.session_state:
        login()
        return
    
    # Display main content if logged in
    st.title("Contenido Principal")
    st.write("Aquí va el contenido principal de tu aplicación.")
    
    # Example of how to integrate other parts of your application
    # For example, displaying a DataFrame
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6]
    })
    st.write(df)

    # Example of plotting with Plotly Express
    fig = px.bar(df, x="A", y="B", title="Gráfico de Barras")
    st.plotly_chart(fig)

    # Example of downloading a CSV
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="datos.csv">Descargar CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Example of logging out
    if st.button("Cerrar Sesión"):
        logout()

if __name__ == "__main__":
    main()
