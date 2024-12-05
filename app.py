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
    {'icon': "far fa-copy", 'label':"Vista Cliente"},
    {'icon': "fa-solid fa-info-circle", 'label':"Caracterización"},
    {'icon': "fas fa-tachometer-alt", 'label':"Admin Dashboard",'ttip':"Dashboard de administración"},
    {'icon': "far fa-copy", 'label':"Cerrar Sesión"},
]

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Home',
    login_name='Cerrar Sesión',
    hide_streamlit_markers=False, # Muestra la hamburguesa de Streamlit
    sticky_nav=True, # Navegación fija en la parte superior
    sticky_mode='pinned', # Pegado en la parte superior
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


# Functions for data visualization and analysis
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


def caracterizacion():
    st.title("Municipio de Granada")
    st.write("""
    **Municipio de Granada**
    Fundada en 21 de abril de 1524, es conocida como “La gran sultana”, constituyéndose en uno de los asentamientos coloniales más antiguos de Centroamérica. Se distingue por la fusión de elementos arquitectónicos en la construcción de la ciudad.
    """)
    
    col1, col2 = st.columns(2)
    
    selected_info = col1.radio("Seleccionar información:", ["Extensión territorial", "Limita", "Población estimada",
                                                         "Población urbana", "Población Rural", "Densidad poblacional",
                                                         "Organización Territorial", "Religión más practicada",
                                                         "Principal actividad económica", "Elecciones Municipales"])
    
    if selected_info == "Extensión territorial":
        col2.write("""
        529.1km², representa el 56.95% del departamento.
        """)

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
    else:
        opciones_respuesta = df[pregunta].value_counts(normalize=True) * 100
        return opciones_respuesta.round(1)

def plot_question(df, question, graph_type, questions, font_size=18, colors=None):
    opciones_respuesta = calcular_opciones_respuesta(df, question)

    if question in ["P46", "P47", "CGM1CPM", "CGM2ROP", "CGM3CRPM", "CGM4CC", "CGM5CGPM"]:
        labels = list(opciones_respuesta.keys())
        values = list(opciones_respuesta.values())
    else:
        data = df[question].value_counts(normalize=True) * 100
        labels = data.index.tolist()
        values = data.values.tolist()

    # Calculando la media de las respuestas (numéricas si aplica)
    try:
        all_responses = df[df[question].apply(lambda x: str(x).isdigit())][question].astype(int)
        mean_response = all_responses.mean()
        st.write(f"Media de la pregunta: {mean_response:.2f}%")
    except ValueError:
        st.warning("No hay suficientes datos numéricos para calcular la media.")

    # Configurar el gráfico según el tipo seleccionado
    if graph_type == "Gráfico de barras":
        fig = px.bar(
            x=labels, 
            y=values, 
            labels={'x': 'Categoría', 'y': 'Porcentaje (%)'},
            title=f"Distribución de respuestas para '{questions[question]}'",
            text=values,
            color_discrete_sequence=colors if colors else px.colors.qualitative.Plotly
        )
    elif graph_type == "Gráfico de barras horizontales":
        fig = px.bar(
            x=values, 
            y=labels, 
            orientation='h',
            labels={'x': 'Porcentaje (%)', 'y': 'Categoría'},
            title=f"Distribución de respuestas para '{questions[question]}'",
            text=values,
            color_discrete_sequence=colors if colors else px.colors.qualitative.Plotly
        )
    elif graph_type == "Gráfico de pastel":
        fig = px.pie(
            names=labels,
            values=values,
            title=f"Distribución de respuestas para '{questions[question]}'",
            color_discrete_sequence=colors if colors else px.colors.qualitative.Plotly
        )
    else:
        st.error("Tipo de gráfico no válido seleccionado.")

    fig.update_layout(font=dict(size=font_size))
    st.plotly_chart(fig, use_container_width=True)


# Main function to handle routing
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if st.session_state["logged_in"]:
        if menu_id == 'Vista Cliente':
            df = pd.read_csv("static/data/LCMG1_Granada2024.csv")
            client_view(df)
        elif menu_id == 'Caracterización':
            caracterizacion()
        elif menu_id == 'Admin Dashboard':
            admin_dashboard()
        elif menu_id == 'Cerrar Sesión':
            st.session_state["logged_in"] = False
            st.experimental_rerun()  # Reinicia la aplicación para volver a la pantalla de login
    else:
        login()

if __name__ == "__main__":
    main()


