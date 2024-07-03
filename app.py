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
        <h1 class="title-test">Bienvenido al Municipio de Granada </h1>
    </div>
    
""")

# Path to the logo
logo_image_path = "static/img/logo.png"

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
            if 'Bueno' in categoria or 'Muy bueno' in categoria:
                sumas_categorias['Muy bueno/bueno'] += valor
            elif 'Regular' in categoria:
                sumas_categorias['Regular'] += valor
            elif 'Pésimo' in categoria or 'Malo' in categoria:
                sumas_categorias['Malo/Pésimo'] += valor
            elif 'NsNr' in categoria or 'No conoce' in categoria:
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
    elif question == "LC":  # Condiciones de color específicas para la pregunta "Licencia Ciudadana Municipal"
        custom_colors = []
        for label in labels:
            if label == "Aprobación":
                custom_colors.append("#00B050")  # Aprobación en verde
            elif label == "Apropiación":
                custom_colors.append("#92D050")  # Apropiación en un tono de verde más claro
            elif label == "Aceptación":
                custom_colors.append("#FFC000")  # Aceptación en amarillo
            elif label == "Rechazo":
                custom_colors.append("#C00000")  # Rechazo en rojo
        if show_no_opina:
            custom_colors.append("#808080")  # Agregar un color para 'No opina/no conoce'
        if graph_type == "Gráfico de barras":
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        elif graph_type == "Gráfico de barras apiladas":
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)},
                         barmode='stack')
        elif graph_type == "Gráfico de líneas":
            fig = px.line(x=labels, y=values,
                          labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                          markers=True)
        elif graph_type == "Gráfico de dispersión":
            fig = px.scatter(x=labels, y=values,
                             labels={'x': 'Respuesta', 'y': 'Porcentaje'})
        else:
            st.error("Tipo de gráfico no soportado para esta pregunta.")
            return
    elif question in ["P46", "P47", "CGM1CPM", "CGM2ROP", "CGM3CRPM", "CGM4CC", "CGM5CGPM"]:
        if colors:
            custom_colors = []
            for label in labels:
                if 'Bueno' in label:
                    custom_colors.append("#00B050")  # Bueno/Muy bueno en verde
                elif 'Regular' in label:
                    custom_colors.append("#FFC000")  # Regular en amarillo
                elif 'Pésimo' in label or 'Malo' in label:
                    custom_colors.append("#C00000")  # Malo/Pésimo en rojo
                elif 'NsNr' in label or 'No conoce' in label:
                    custom_colors.append("#808080")  # NsNr/No conoce en gris
            if show_no_opina:
                custom_colors.append("#808080")  # Agregar un color para 'No opina/no conoce'
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Categoría', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        else:
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Categoría', 'y': 'Porcentaje'})
    else:
        if graph_type == "Gráfico de barras":
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'})
        elif graph_type == "Gráfico de barras apiladas":
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         barmode='stack')
        elif graph_type == "Gráfico de líneas":
            fig = px.line(x=labels, y=values,
                          labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                          markers=True)
        elif graph_type == "Gráfico de dispersión":
            fig = px.scatter(x=labels, y=values,
                             labels={'x': 'Respuesta', 'y': 'Porcentaje'})
        else:
            st.error("Tipo de gráfico no soportado para esta pregunta.")
            return

    fig.update_layout(
        font=dict(size=font_size),
        xaxis_title="",
        yaxis_title="",
        title=dict(text=question, font=dict(size=font_size + 4), x=0.5)
    )
    
    st.plotly_chart(fig)

# Define functions for different pages
def login():
    st.title("Inicio de Sesión")
    st.markdown(html_title_template.substitute(logo=load_logo(logo_image_path)), unsafe_allow_html=True)
    st.subheader("Inicio de Sesión")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        if username == "admin" and password == "admin":  # Example credentials check
            st.session_state.logged_in = True
            st.success("Inicio de sesión exitoso")
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

def view1(df):
    st.title("Vista 1")
    st.markdown(html_title_template.substitute(logo=load_logo(logo_image_path)), unsafe_allow_html=True)
    st.subheader("Vista 1: Análisis de Datos")
    
    st.write("Esta es la primera vista de tu aplicación.")

    st.write("### Tabla cruzada")
    preguntas_disponibles = df.columns
    preguntas_seleccionadas = st.multiselect("Selecciona las preguntas:", preguntas_disponibles)
    selected_question_key = st.selectbox("Selecciona la pregunta para cruzar:", preguntas_disponibles)

    if st.button("Generar tabla cruzada"):
        tabla_cruzada = calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key)
        if tabla_cruzada is not None:
            st.write(tabla_cruzada)

def view2(df):
    st.title("Vista 2")
    st.markdown(html_title_template.substitute(logo=load_logo(logo_image_path)), unsafe_allow_html=True)
    st.subheader("Vista 2: Visualización de Preguntas")

    st.write("Esta es la segunda vista de tu aplicación.")

    st.write("### Visualización de preguntas")
    preguntas_disponibles = df.columns
    selected_question = st.selectbox("Selecciona la pregunta para visualizar:", preguntas_disponibles)
    graph_type = st.selectbox("Selecciona el tipo de gráfico:", ["Gráfico de barras", "Gráfico de barras apiladas", "Gráfico de líneas", "Gráfico de dispersión"])
    font_size = st.slider("Tamaño de la fuente:", 10, 30, 18)

    if st.button("Generar gráfico"):
        plot_question(df, selected_question, graph_type, preguntas_disponibles, font_size)

def logout():
    st.session_state.logged_in = False
    st.success("Has cerrado sesión")
    st.experimental_rerun()

# Main application logic
def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Load data
    df = pd.read_csv("datos/archivo_limpio.csv")

    # Page navigation
    if st.session_state.logged_in:
        menu = ["Vista 1", "Vista 2", "Cerrar Sesión"]
        choice = st.sidebar.selectbox("Menú", menu)

        if choice == "Vista 1":
            view1(df)
        elif choice == "Vista 2":
            view2(df)
        elif choice == "Cerrar Sesión":
            logout()
    else:
        login()

if __name__ == "__main__":
    main()
