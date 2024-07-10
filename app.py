import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
from streamlit_option_menu import option_menu
from string import Template
import datetime
import numpy as np

# Path to the logo
logo_image_path = "static/img/logo.png"

def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True

    st.title("Inicio de Sesión")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión"):
            if username == "admin" and password == "admin":
                st.session_state["logged_in"] = True
            else:
                st.error("Usuario o contraseña incorrectos")

    return False

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
        fig = px.bar(x=labels, y=values,
                     labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                     color=labels,
                     color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
    else:
        fig = px.bar(x=labels, y=values,
                     labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                     color=labels,
                     color_discrete_sequence=colors)
    
    fig.update_layout(
        title=f"Distribución de respuestas para la pregunta: {questions[question]}",
        xaxis_title="Respuesta",
        yaxis_title="Porcentaje",
        font=dict(size=font_size)
    )
    
    st.plotly_chart(fig)

def show_table(df, question, questions):
    st.write(f"Tabla de datos para la pregunta: {questions[question]}")
    st.dataframe(df[[question]])

def select_departament():
    st.sidebar.subheader("Seleccione un departamento")
    departamentos = ["Departamento 1", "Departamento 2", "Departamento 3"]  # Lista de departamentos
    departamento = st.sidebar.selectbox("Departamentos", departamentos)
    return departamento

def upload_csv():
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        return df
    return None

def update_map_data(selected_departamento, df):
    # Filtra los datos por el departamento seleccionado
    filtered_data = df[df["departamento"] == selected_departamento]
    return filtered_data

def plot_map(filtered_data):
    st.map(filtered_data)

def display_data(df, questions):
    st.sidebar.subheader("Seleccione una pregunta para visualizar")
    question_keys = list(questions.keys())
    selected_question_key = st.sidebar.selectbox("Preguntas", question_keys)
    graph_type = st.sidebar.selectbox("Tipo de gráfico", ["Barra", "Línea", "Dispersión"])
    font_size = st.sidebar.slider("Tamaño de fuente", 10, 30, 18)
    colors = st.sidebar.color_picker("Seleccione el color", "#00f900")

    if selected_question_key:
        st.header(f"Visualización para la pregunta: {questions[selected_question_key]}")
        plot_question(df, selected_question_key, graph_type, questions, font_size, colors)
        show_table(df, selected_question_key, questions)

def main():
    # Load the logo
    logo_base64 = load_logo(logo_image_path)

    # Display the title with the logo
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)

    if login():
        st.sidebar.title("Opciones de Visualización")
        departamento = select_departament()
        df = upload_csv()
        if df is not None:
            filtered_data = update_map_data(departamento, df)
            plot_map(filtered_data)

            questions = {
                "P01": "Pregunta 1",
                "P02": "Pregunta 2",
                "P03": "Pregunta 3"
                # Agregar todas las preguntas relevantes aquí
            }
            display_data(df, questions)
        else:
            st.write("Por favor, cargue un archivo CSV.")

if __name__ == "__main__":
    main()
