import streamlit as st
import pandas as pd
import base64
from string import Template
import hydralit_components as hc

# Configuración de la página
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Definir el menú de navegación
menu_data = [
    {'icon': "far fa-copy", 'label':"Vista Cliente"},
    {'icon': "far fa-copy", 'label':"Cerrar Sesión"},
]

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Home',
    login_name='Cerrar Sesión',
    hide_streamlit_markers=False, 
    sticky_nav=True,
    sticky_mode='pinned', 
)

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
        flex-direction: column;
    }
    .logo {
        width: 150px;
    }
    .title-test {
        font-weight: bold;
        padding: 3px;
        border-radius: 6px;
        margin-top: 10px;
    }
    .login-form {
        margin-top: 20px;
    }
    </style>
    <div class="header">
        <img src="data:image/png;base64,$logo" class="logo">
        <h1 class="title-test">Bienvenido LCM</h1>
    </div>
""")

# Path to the logo
logo_image_path = "static/img/logo.png"

def login():
    st.markdown(html_title_template.substitute(logo=load_logo(logo_image_path)), unsafe_allow_html=True)
    
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "Usuario1" and password == "LCM2024":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.markdown('</div>', unsafe_allow_html=True)

# Function for client view
def client_view(df):
    questions = {
        "P09": "Genera o recibe algún tipo de ingreso (salarios, ventas, remesa, renta, jubilación, etc:)",
        "P46": "Calificación e índice al trabajo realizado por el alcalde(sa) del municipio",
        "P47": "Imagen del alcalde(sa) del municipio",
        "CGM1CPM": "Conocimiento de los problemas del municipio",
        "CGM2ROP": "Resolución oportuna de problemas",
        "CGM3CRPM": "Capacidad para resolver los problemas del municipio",
        "CGM4CC": "Comunicación con la ciudadanía",
        "CGM5CGPM": "Confianza que generan en la población del municipio",
        "LC": "Licencia Ciudadana Municipal",
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Seleccionar pregunta")
        selected_question_key = st.selectbox("Seleccionar pregunta", options=list(questions.keys()), format_func=lambda x: questions[x])
        graph_type_key = selected_question_key + "_graph_type"
        graph_type = st.radio("Seleccionar tipo de gráfico", options=["Gráfico de barras", "Gráfico de barras horizontales", "Gráfico de pastel"], key=graph_type_key)
        st.subheader(questions[selected_question_key])
       
    with col2:
        st.subheader("Gráfico")
        colores = ["#00B050", "#FFC000", "#C00000", "#0070C0"]
        plot_question(df, selected_question_key, graph_type, questions, font_size=18, colors=colores)

# Function to plot questions' responses
def plot_question(df, question, graph_type, questions, font_size=18, colors=None):
    opciones_respuesta = df[question].value_counts(normalize=True) * 100
    labels = opciones_respuesta.index
    values = opciones_respuesta.values
    
    st.write(f"Media de la pregunta: {opciones_respuesta.mean():.2f}%")
    
    # Generate graph based on type selected
    if graph_type == "Gráfico de barras":
        st.bar_chart(opciones_respuesta)
    elif graph_type == "Gráfico de barras horizontales":
        st.bar_chart(opciones_respuesta, use_container_width=True)
    elif graph_type == "Gráfico de pastel":
        fig = px.pie(values=values, names=labels, color=labels, color_discrete_sequence=colors)
        st.plotly_chart(fig)

# Log out functionality
def logout():
    if st.button("Cerrar Sesión"):
        del st.session_state["logged_in"]
        st.experimental_rerun()

# Main logic
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    # Simulate loading a DataFrame
    df = pd.DataFrame({
        "P09": ["Sí", "No", "Sí", "Sí", "No"],
        "P46": ["Bueno", "Regular", "Muy bueno", "Bueno", "Regular"],
        "P47": ["Buena", "Regular", "Excelente", "Buena", "Regular"]
    })
    client_view(df)
    logout()
