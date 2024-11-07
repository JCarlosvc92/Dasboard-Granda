import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
from string import Template
import hydralit_components as hc
import datetime
import numpy as np

# Configuración de la página
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# Definir el menú de navegación
menu_data = [
    {'icon': "far fa-copy", 'label':"Dashboard"},
]

if 'logged_in' in st.session_state and st.session_state['logged_in']:
    menu_data.append({'icon': "far fa-sign-out", 'label':"Cerrar Sesión"})

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Dashboard',
    login_name='Cerrar Sesión',
    hide_streamlit_markers=False,  # Muestra la hamburguesa de Streamlit
    sticky_nav=True,  # Navegación fija en la parte superior
    sticky_mode='pinned',  # Pegado en la parte superior
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

def logout():
    st.session_state["logged_in"] = False
    st.experimental_rerun()

# Functions for data visualization and analysis
def Dashboard(df):
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
       
        preguntas_seleccionadas = st.multiselect(
            "Seleccionar preguntas para tabla cruzada",
            options=[
                "Sector: Sector",
                "SexoEntrevistado: Sexo Entrevistado [Generaciones del Entrevistado]",
                "GENERACIONES: GENERACIONES"
            ],
            format_func=lambda option: option.split(":")[1].strip()
        )

        if len(preguntas_seleccionadas) == 1:
            tabla_cruzada = calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key)
            if tabla_cruzada is not None:
                with st.expander("Ver tabla cruzada"):
                    st.write(tabla_cruzada.round(1))
            else:
                st.warning("Alguna de las variables seleccionadas no existe en el DataFrame.")
        elif len(preguntas_seleccionadas) > 1:
            st.warning("Solo se permite seleccionar una variable para la tabla cruzada.")
            

    with col2:
        st.subheader("Gráfico")
        colores = ["#00B050", "#FFC000", "#C00000", "#0070C0"]
        plot_question(df, selected_question_key, graph_type, questions, font_size=18, colors=colores)

        with st.expander(f" '{questions[selected_question_key]}'"):
            opciones_respuesta = calcular_opciones_respuesta(df, selected_question_key)
            st.write(opciones_respuesta)

def logout_action():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        logout()

# Functions for data analysis
def calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key):
    try:
        preguntas = [pregunta.split(":")[0].strip() for pregunta in preguntas_seleccionadas]
        preguntas.append(selected_question_key)
        df[selected_question_key] = df[selected_question_key].replace({'9 Bueno': 'Bueno/Muy bueno', '10 Muy bueno': 'Bueno/Muy bueno',
                                                                     '6 Pésimo': 'Pésimo/Malo', '7 Malo': 'Pésimo/Malo',
                                                                     '8 Regular': 'Regular', '0': 'No opina/No conoce'})
        tabla_cruzada = pd.crosstab(index=[df[p] for p in preguntas[:-1]], columns=df[preguntas[-1]])
        tabla_cruzada_porcentaje = tabla_cruzada.div(tabla_cruzada.sum(axis=1), axis=0) * 100
        tabla_cruzada_porcentaje = tabla_cruzada_porcentaje.apply(lambda x: x.map('{:.1f}%'.format))
        return tabla_cruzada_porcentaje
    except KeyError as e:
        st.error(f"Error: {e}. Alguna de las preguntas seleccionadas no existe en el DataFrame.")
        st.write(f"Preguntas disponibles en el DataFrame: {list(df.columns)}")
        return None


def calcular_opciones_respuesta(df, pregunta):
    preguntas_procesadas = ["P46", "P47", "CGM1CPM", "CGM2ROP", "CGM3CRPM", "CGM4CC", "CGM5CGPM"]

    if pregunta in preguntas_procesadas:
        df['categoria_combinada'] = df[pregunta].replace({
            '9 Bueno': 'Bueno/Muy bueno', '10 Muy bueno': 'Bueno/Muy bueno',
            '6 Pésimo': 'Pésimo/Malo', '7 Malo': 'Pésimo/Malo',
            '8 Regular': 'Regular', '5': 'NsNr/No conoce'
        })

        opciones_respuesta = df['categoria_combinada'].value_counts(normalize=True) * 100

        sumas_categorias = {'Muy bueno/bueno': 0, 'Regular': 0, 'Malo/Pésimo': 0, 'NsNr/No conoce': 0}

        for categoria, valor in opciones_respuesta.items():
            if 'Bueno' in categoria or 'Muy bueno' in categoria:
                sumas_categorias['Muy bueno/bueno'] += valor
            elif 'Regular' in categoria:
                sumas_categorias['Regular'] += valor
            elif 'Pésimo' in categoria or 'Malo' in categoria:
                sumas_categorias['Malo/Pésimo'] += valor
            elif 'NsNr' in categoria or 'No conoce' in categoria:
                sumas_categorias['NsNr/No conoce'] += valor

        sumas_categorias = {categoria: round(valor, 1) for categoria, valor in sumas_categorias.items()}

        return sumas_categorias


def plot_question(df, selected_question_key, graph_type, questions, font_size=18, colors=None):
    pregunta = questions[selected_question_key]
    opciones_respuesta = df[selected_question_key].value_counts(normalize=True) * 100

    if graph_type == "Gráfico de barras":
        fig = px.bar(x=opciones_respuesta.index, y=opciones_respuesta.values, color=opciones_respuesta.index,
                     color_discrete_sequence=colors, labels={selected_question_key: pregunta},
                     title=f"{pregunta} - Gráfico de barras", width=600, height=400)
        fig.update_layout(font_size=font_size)
        st.plotly_chart(fig, use_container_width=True)

    elif graph_type == "Gráfico de barras horizontales":
        fig = px.bar(x=opciones_respuesta.values, y=opciones_respuesta.index, color=opciones_respuesta.index,
                     color_discrete_sequence=colors, labels={selected_question_key: pregunta},
                     title=f"{pregunta} - Gráfico de barras horizontales", width=600, height=400)
        fig.update_layout(font_size=font_size)
        st.plotly_chart(fig, use_container_width=True)

    elif graph_type == "Gráfico de pastel":
        fig = px.pie(names=opciones_respuesta.index, values=opciones_respuesta.values, title=f"{pregunta} - Gráfico de pastel",
                     labels={selected_question_key: pregunta}, width=600, height=400)
        fig.update_layout(font_size=font_size)
        st.plotly_chart(fig, use_container_width=True)

# Control de sesión
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    # Aquí se debe cargar el CSV o los datos a analizar
    df = pd.read_csv("data.csv")  # Ejemplo de cómo cargar un archivo CSV
    Dashboard(df)

    logout_action()  # Botón para cerrar sesión
