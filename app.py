import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import base64
from streamlit_option_menu import option_menu
from string import Template
import hydralit_components as hc
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
        flex-direction: column;
    }
    .logo {
        width: 150px;  /* Adjust the logo size here */
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

# Functions for data visualization and analysis
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

# Functions for CSV handling
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

# Functions for data analysis
def calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key):
    try:
        preguntas = [pregunta.split(":")[0].strip() for pregunta in preguntas_seleccionadas]
        preguntas.append(selected_question_key)
        df[selected_question_key] = df[selected_question_key].replace({'9 Bueno': 'Bueno/Muy bueno', '10 Muy bueno': 'Bueno/Muy bueno',
                                                                     '6 Pésimo': 'Pésimo/Malo', '7 Malo': 'Pésimo/Malo', '8 Regular': 'Regular'})

        df = df[preguntas].dropna()
        tabla_cruzada = pd.crosstab(df[selected_question_key], df[preguntas[0]], normalize='columns') * 100
        return tabla_cruzada
    except KeyError:
        return None

def calcular_opciones_respuesta(df, selected_question_key):
    opciones_respuesta = df[selected_question_key].value_counts(normalize=True) * 100
    return opciones_respuesta

def plot_question(df, question, graph_type, questions, font_size=14, colors=None):
    if colors is None:
        colors = px.colors.qualitative.Safe  # Default colors if not provided

    question_data = df[question].value_counts(normalize=True) * 100
    question_data = question_data.sort_index()  # Ensure the categories are sorted

    if graph_type == "Gráfico de barras":
        fig = px.bar(question_data, x=question_data.index, y=question_data.values, title=questions[question], text=question_data.values, color=question_data.index, color_discrete_sequence=colors)
    elif graph_type == "Gráfico de barras horizontales":
        fig = px.bar(question_data, y=question_data.index, x=question_data.values, title=questions[question], text=question_data.values, orientation='h', color=question_data.index, color_discrete_sequence=colors)
    elif graph_type == "Gráfico de pastel":
        fig = px.pie(question_data, values=question_data.values, names=question_data.index, title=questions[question], color=question_data.index, color_discrete_sequence=colors)

    fig.update_layout(title={'text': questions[question], 'x': 0.5}, font=dict(size=font_size))
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# Main function to handle routing
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # Sidebar for navigation
        st.sidebar.title("Menú de Navegación")
        role = st.sidebar.selectbox("Seleccionar Rol", ["Usuario", "Administrador"])

        if role == "Usuario":
            menu = option_menu(
                menu_title="Menú",
                options=["Visión General", "Visualización de Datos", "Caracterización"],
                icons=["house", "graph-up-arrow", "person-badge"],
                menu_icon="cast",
                default_index=0,
            )

            if menu == "Visión General":
                st.title("Visión General del Usuario")
                st.write("Aquí va el contenido general para el usuario.")

            elif menu == "Visualización de Datos":
                client_view()

            elif menu == "Caracterización":
                caracterizacion()

        elif role == "Administrador":
            menu = option_menu(
                menu_title="Menú de Administrador",
                options=["Panel de Control", "Subir Datos", "Gestión de Usuarios"],
                icons=["tools", "upload", "person-badge"],
                menu_icon="cast",
                default_index=0,
            )

            if menu == "Panel de Control":
                admin_dashboard()

            elif menu == "Subir Datos":
                cargar_csv()

            elif menu == "Gestión de Usuarios":
                st.write("Funcionalidades de gestión de usuarios (pendiente de implementación).")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state["logged_in"] = False
            st.experimental_rerun()
    else:
        login()

if __name__ == "__main__":
    main()
