import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
import time
from streamlit_option_menu import option_menu
from string import Template
import hydralit_components as hc
import datetime
import numpy as np
import os

# Function to load logo and convert to base64
def load_logo(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
        return encoded_logo
    except FileNotFoundError:
        st.error(f"El archivo de logo no se encontró en la ruta: {logo_path}")
        return None

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
        <h1 class="title-test">Bienvenido al Municipio de Diria</h1>
    </div>
    
""")

# Path to the logo
logo_image_path = "static/img/logo.png"
static_csv_path = "static/data/data.csv"  # Asegúrate de que esta ruta sea correcta

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
    # Definir las preguntas que deben ser procesadas por esta función
    preguntas_procesadas = ["P46", "P47", "CGM1CPM", "CGM2ROP", "CGM3CRPM", "CGM4CC", "CGM5CGPM"]  # Reemplaza con las preguntas que deseas procesar

    # Verificar si la pregunta especificada debe ser procesada
    if pregunta in preguntas_procesadas:
        # Crear una nueva columna para representar la categoría combinada
        df['categoria_combinada'] = df[pregunta].replace({
            '9 Bueno': 'Bueno/Muy bueno', '10 Muy bueno': 'Bueno/Muy bueno',
            '6 Pésimo': 'Pésimo/Malo', '7 Malo': 'Pésimo/Malo',
            '8 Regular': 'Regular', '5': 'NsNr/No conoce'
        })

        

        # Calcular opciones de respuesta normalizadas
        opciones_respuesta = df['categoria_combinada'].value_counts(normalize=True) * 100

        # Crear un diccionario para almacenar las sumas de las categorías combinadas
        sumas_categorias = {'Muy bueno/bueno': 0, 'Regular': 0, 'Malo/Pésimo': 0, 'NsNr/No conoce': 0}

        # Iterar sobre las opciones de respuesta y sumar las categorías combinadas
        for categoria, valor in opciones_respuesta.items():
            if 'Bueno' in categoria o 'Muy bueno' in categoria:
                sumas_categorias['Muy bueno/bueno'] += valor
            elif 'Regular' in categoria:
                sumas_categorias['Regular'] += valor
            elif 'Pésimo' in categoria o 'Malo' in categoria:
                sumas_categorias['Malo/Pésimo'] += valor
            elif 'NsNr' in categoria o 'No conoce' in categoria:
                sumas_categorias['NsNr/No conoce'] += valor

        # Redondear las sumas de las categorías combinadas
        sumas_categorias = {categoria: round(valor, 1) for categoria, valor in sumas_categorias.items()}

        return sumas_categorias
    else:
        # Si la pregunta no debe ser procesada, devolver las opciones de respuesta normales
        opciones_respuesta = df[pregunta].value_counts(normalize=True) * 100
        return opciones_respuesta.round(1)

def plot_question(df, question, graph_type, questions, font_size=18, colors=None):
    opciones_respuesta = calcular_opciones_respuesta(df, question)  # Calcular opciones de respuesta

    if question in ["P46", "P47", "CGM1CPM", "CGM2ROP", "CGM3CRPM", "CGM4CC", "CGM5CGPM"]:
        data = opciones_respuesta
        labels = list(opciones_respuesta.keys())
        values = list(opciones_respuesta.values())
    else:
        data = df[question].value_counts(normalize=True) * 100
        labels = data.index
        values = data.values
    
    # Calcular la media de todas las respuestas
    all_responses = df[df[question].apply(lambda x: str(x).isdigit())][question].astype(int)
    mean_response = all_responses.mean()
    
    # Mostrar la media encima del gráfico
    st.write(f"Media de la pregunta: {mean_response:.2f}%")

    # Verificar si 'No opina/no conoce' está en las etiquetas y si hay datos para esta categoría
    if "No opina/No conoce" in labels and len(df[df[question] == "No opina/No conoce"]) > 0:
     show_no_opina = True
     no_opina_index = labels.index("No opina/No conoce")
    else:
     show_no_opina = False

    # Filtrar los valores de 'No opina/no conoce'
    if "No opina/No conoce" in labels and not show_no_opina:
        idx = labels.index("No opina/No conoce")
        del labels[idx]
        del values[idx]



    if question == "P09":
        if colors:
            # Definir colores personalizados para sí y no
            custom_colors = ['#00B050' if label == 'Sí' else '#C00000' for label in labels]
            if show_no_opina:
                custom_colors.append("#808080")  # Agregar un color para 'No opina/no conoce'
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        else:
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'})
    elif question == "P43":
        if colors:
            # Definir colores personalizados para muy seguro, algo seguro, algo inseguro y muy inseguro
            custom_colors = ['#00B050' if label == 'Muy seguro' else '#FFC000' if label == 'Algo seguro' else '#FFFF00' if label == 'Algo inseguro' else '#C00000' for label in labels]
            if show_no_opina:
                custom_colors.append("#808080")  # Agregar un color para 'No opina/no conoce'
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        else:
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'})
    else:
        fig = px.pie(values=values, names=labels, title=questions[question])
        fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.1] * len(values))

    fig.update_layout(
        title={'text': questions[question], 'x': 0.5},
        font=dict(size=font_size),
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig)

# Function to handle login logic
def handle_login():
    st.session_state['logged_in'] = True
    st.experimental_rerun()

# Function to display login screen
def display_login_screen(logo_image_path):
    encoded_logo = load_logo(logo_image_path)
    if encoded_logo:
        st.markdown(html_title_template.substitute(logo=encoded_logo), unsafe_allow_html=True)
        # Formulario de inicio de sesión
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button("Iniciar Sesión")

            if login_button:
                # Aquí deberías verificar las credenciales del usuario
                if username == "admin" and password == "admin":
                    handle_login()
                else:
                    st.error("Usuario o contraseña incorrectos")

# Main function to display the app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        display_login_screen(logo_image_path)
    else:
        st.title("Dashboard del Municipio de Diria")

        # Verificar si el archivo CSV existe antes de cargarlo
        st.write(f"Ruta del archivo CSV: {static_csv_path}")  # Mostrar la ruta del archivo CSV para depuración

        if os.path.exists(static_csv_path):
            df = pd.read_csv(static_csv_path, header=0)
        else:
            st.error(f"El archivo CSV no se encontró en la ruta: {static_csv_path}")
            return

        df['P13'] = df['P13'].replace({1: "Si", 2: "No"})
        df['P20'] = df['P20'].replace({1: "Si", 2: "No"})
        df['P22'] = df['P22'].replace({1: "Si", 2: "No"})
        df['P31'] = df['P31'].replace({1: "Si", 2: "No"})
        df['P33'] = df['P33'].replace({1: "Si", 2: "No"})

        # Añadir opciones de navegación
        options = ["Análisis Descriptivo", "Mapas Interactivos", "Tablas Cruzadas"]
        choice = st.sidebar.selectbox("Seleccione una opción", options)

        if choice == "Análisis Descriptivo":
            st.header("Análisis Descriptivo")
            questions = {
                'P01': '1. ¿Cuál es su edad?',
                'P02': '2. ¿Con qué género se identifica?',
                'P03': '3. ¿Cuál es su nivel educativo?',
                'P09': '9. ¿Se siente seguro en su comunidad?',
                'P43': '43. ¿Cómo calificaría la seguridad en su comunidad?'
            }

            selected_question = st.selectbox("Seleccione una pregunta", list(questions.keys()), format_func=lambda x: questions[x])
            selected_graph_type = st.radio("Seleccione el tipo de gráfico", ["Barras", "Torta"])

            plot_question(df, selected_question, selected_graph_type, questions)

        elif choice == "Mapas Interactivos":
            st.header("Mapas Interactivos")
            # Aquí puedes añadir la lógica para mostrar los mapas SVG

        elif choice == "Tablas Cruzadas":
            st.header("Tablas Cruzadas")
            questions = [col for col in df.columns if col.startswith("P")]
            selected_questions = st.multiselect("Seleccione las preguntas para la tabla cruzada", questions)

            if selected_questions:
                selected_question_key = st.selectbox("Seleccione la pregunta de la columna", questions)
                tabla_cruzada = calcular_tabla_cruzada(df, selected_questions, selected_question_key)

                if tabla_cruzada is not None:
                    st.table(tabla_cruzada)

if __name__ == "__main__":
    main()
