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
        elif graph_type == "Gráfico de barras horizontales":
            fig = px.bar(x=values, y=labels, orientation='h',
                         labels={'y': 'Respuesta', 'x': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        elif graph_type == "Gráfico de pastel":
            fig = px.pie(names=labels,
                         values=values,
                         title=f"Frecuencia de respuestas para {questions[question]}",
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
    else:
        if graph_type == "Gráfico de barras":
            if colors:
                fig = px.bar(x=labels, y=values,
                             labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                             color=labels,
                             color_discrete_map={val: col for val, col in zip(labels, colors)})
            else:
                fig = px.bar(x=labels, y=values,
                             labels={'x': 'Respuesta', 'y': 'Porcentaje'})
        elif graph_type == "Gráfico de barras horizontales":
            if colors:
                fig = px.bar(x=values, y=labels, orientation='h',
                             labels={'y': 'Respuesta', 'x': 'Porcentaje'},
                             color=labels,
                             color_discrete_map={val: col for val, col in zip(labels, colors)})
            else:
                fig = px.bar(x=values, y=labels, orientation='h',
                             labels={'y': 'Respuesta', 'x': 'Porcentaje'})
        elif graph_type == "Gráfico de pastel":
            if colors:
                fig = px.pie(names=labels,
                             values=values,
                             title=f"Frecuencia de respuestas para {questions[question]}",
                             color=labels,
                             color_discrete_map={val: col for val, col in zip(labels, colors)})
            else:
                fig = px.pie(names=labels,
                             values=values,
                             title=f"Frecuencia de respuestas para {questions[question]}")

    if fig:
        fig.update_traces(texttemplate='%{value:.1f}%', textfont_size=font_size)
        fig.update_layout(font=dict(size=font_size))  # Ajustar el tamaño de fuente global
        st.plotly_chart(fig)

def main():
    # Load and display the title and logo
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
    
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
    
    # Dividir en dos columnas
    col1, col2 = st.columns(2)
    
    # Menú desplegable para seleccionar el título
    selected_info = col1.radio("Seleccionar información:", ["Extensión territorial", "Limita", "Población estimada",
                                                         "Población urbana", "Población Rural", "Densidad poblacional",
                                                         "Organización Territorial", "Religión más practicada",
                                                         "Principal actividad económica", "Elecciones Municipales"])
    
    # Mostrar la información correspondiente en la segunda columna
    if selected_info == "Extensión territorial":
        col2.write("""
        529.1km², representa el 56.95% del departamento.
        """)
        # Agregar imagen en la segunda columna

    elif selected_info == "Limita":
        col2.write("""
        Al Norte con Tipitapa. 
        Al Sur con Nandaime. 
        Al Este con San Lorenzo y el lago Cocibolca. 
        Al Oeste con Tisma, Masaya, Diría, Diriomo, Nandaime y laguna de apoyo.
        """)
    elif selected_info == "Población estimada":
        col2.write("""
        132,054 que representa el 61.62%
        """)
    # Continuar con el resto de los casos...

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

    col1, col2 = st.columns([1, 1])  # Column width adjustment

    with col1:
        st.subheader("Seleccionar pregunta")
        selected_question_key = st.selectbox("Seleccionar pregunta", options=list(questions.keys()), format_func=lambda x: questions[x])
        graph_type_key = selected_question_key + "_graph_type"  # Unique key for graph type radio button
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

        if len(preguntas_seleccionadas) == 1:  # Only allow one selection
            df = pd.read_csv(static_csv_path, header=0)
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
        colores = ["#00B050", "#FFC000", "#C00000", "#0070C0"]  # Lista de colores específicos
        plot_question(df, selected_question_key, graph_type, questions, font_size=18, colors=colores)  # Llamada a plot_question() con la lista de colores

        with st.expander(f" '{questions[selected_question_key]}'"):
            opciones_respuesta = calcular_opciones_respuesta(df, selected_question_key)
            st.write(opciones_respuesta)

 # Carrusel de imágenes en la sección de "Inicio"
   

if __name__ == "__main__":
    main()

