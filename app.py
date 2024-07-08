import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
from string import Template
import datetime
import numpy as np

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

def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "Usuario1" and password == "lcm2024":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

def logout():
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]

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
        else:
            fig = px.pie(values=values, names=labels,
                         labels={'names': 'Respuesta', 'values': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
    else:
        if graph_type == "Gráfico de barras":
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_sequence=colors)
        else:
            fig = px.pie(values=values, names=labels,
                         labels={'names': 'Respuesta', 'values': 'Porcentaje'},
                         color=labels,
                         color_discrete_sequence=colors)

    # Agregar media de la pregunta como anotación en el gráfico
    fig.add_annotation(
        text=f"Media: {mean_response:.2f}%",
        x=0.5, y=1.1,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=font_size, color="black")
    )
    
    return fig

# App starts here
def main():
    st.write(html_title_template.substitute(logo=load_logo(logo_image_path)), unsafe_allow_html=True)

    if "logged_in" not in st.session_state:
        login()
    else:
        if st.button("Cerrar Sesión"):
            logout()
            st.experimental_rerun()

        st.title("Encuesta de Licencia Ciudadana Municipal")

        # File upload
        st.subheader("Subir datos")
        uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            st.subheader("Seleccionar opciones")
            graph_type = st.selectbox("Selecciona el tipo de gráfico", ["Gráfico de barras", "Gráfico de pastel"])
            questions = df.columns.tolist()
            selected_question = st.selectbox("Selecciona la pregunta que deseas visualizar", questions)

            # Color selection
            custom_colors = st.color_picker("Seleccione color para las respuestas", value='#00B050', key="color_picker")
            colors = [custom_colors]

            if st.button("Generar gráfico"):
                fig = plot_question(df, selected_question, graph_type, questions, colors=colors)
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()
