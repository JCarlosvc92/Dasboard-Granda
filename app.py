import base64
from io import BytesIO
from PIL import Image
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px

logo_image_path = "static/img/logo.png"
background_image_path = "static/img/fondo.png"

def load_logo(logo_path):
    with open(logo_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def html_title_template():
    return """
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{}' width='150'>
    </div>
    """

def main():
    logo_base64 = load_logo(logo_image_path)
    st.markdown(html_title_template().format(logo_base64), unsafe_allow_html=True)
    
    # Add background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/png;base64,{base64.b64encode(open(background_image_path, "rb").read()).decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login()
    else:
        navigation()

def login():
    st.title("Inicio de sesión")
    
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar sesión"):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.session_state.admin = True
            st.success("Sesión iniciada como Administrador")
        elif username == "user" and password == "user":
            st.session_state.authenticated = True
            st.session_state.admin = False
            st.success("Sesión iniciada como Usuario")
        else:
            st.error("Usuario o contraseña incorrecta")

def navigation():
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Caracterización", "Administrador", "Cerrar Sesión"],
        icons=["house", "person", "gear", "door-closed"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Inicio":
        client_view()
    elif selected == "Caracterización":
        caracterizacion()
    elif selected == "Administrador":
        admin_dashboard()
    elif selected == "Cerrar Sesión":
        st.session_state.authenticated = False
        st.session_state.admin = False
        login()

def caracterizacion():
    st.title("Municipio de Deria")
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
        col2.write("529.1km², representa el 56.95% del departamento.")
    elif selected_info == "Limita":
        col2.write("""
        Al Norte con Tipitapa. 
        Al Sur con Nandaime. 
        Al Este con San Lorenzo y el lago Cocibolca. 
        Al Oeste con Tisma, Masaya, Diría, Diriomo, Nandaime y laguna de apoyo.
        """)
    elif selected_info == "Población estimada":
        col2.write("132,054 que representa el 61.62%")
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
        colores = ["#00B050", "#FFC000", "#C00000", "#0070C0"]
        plot_question(df, selected_question_key, graph_type, questions, font_size=18, colors=colores)
        with st.expander(f" '{questions[selected_question_key]}'"):
            opciones_respuesta = calcular_opciones_respuesta(df, selected_question_key)
            st.write(opciones_respuesta)

def calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key):
    try:
        preguntas = [pregunta.split(":")[0].strip() for pregunta in preguntas_seleccionadas]
        preguntas.append(selected_question_key)
        df[selected_question_key] = df[selected_question_key].replace({
            '9 Bueno': 'Bueno/Muy bueno', '10 Muy bueno': 'Bueno/Muy bueno',
            '6 Pésimo': 'Pésimo/Malo', '7 Malo': 'Pésimo/Malo',
            '8 Regular': 'Regular', '0': 'No opina/No conoce'
        })
        tabla_cruzada = pd.crosstab(index=[df[p] for p in preguntas[:-1]], columns=df[preguntas[-1]])
        tabla_cruzada_porcentaje = tabla_cruzada.div(tabla_cruzada.sum(axis=1), axis=0) * 100
        tabla_cruzada_porcentaje = tabla_cruzada_porcentaje.apply(lambda x: x.map('{:.1f}%'.format))
        return tabla_cruzada_porcentaje
    except KeyError as e:
        st.error(f"Error: {e}. Alguna de las preguntas seleccionadas no existe en el DataFrame.")
        st.write(f"Preguntas disponibles en el DataFrame: {list(df.columns)}")
        return None

def calcular_opciones_respuesta(df, selected_question_key):
    opciones_respuesta = df[selected_question_key].value_counts().reset_index()
    opciones_respuesta.columns = ["Opción de Respuesta", "Total"]
    total_respuestas = opciones_respuesta["Total"].sum()
    opciones_respuesta["Porcentaje"] = opciones_respuesta["Total"] / total_respuestas * 100
    opciones_respuesta = opciones_respuesta.round(1)
    return opciones_respuesta

def plot_question(df, question_key, graph_type, questions, font_size=18, colors=None):
    opciones_respuesta = df[question_key].value_counts().reset_index()
    opciones_respuesta.columns = ["Opción de Respuesta", "Total"]
    if graph_type == "Gráfico de barras":
        fig = px.bar(opciones_respuesta, x="Opción de Respuesta", y="Total", color="Opción de Respuesta", title=questions[question_key], color_discrete_sequence=colors)
        fig.update_layout(font=dict(size=font_size), showlegend=False)
        st.plotly_chart(fig)
    elif graph_type == "Gráfico de barras horizontales":
        fig = px.bar(opciones_respuesta, x="Total", y="Opción de Respuesta", color="Opción de Respuesta", orientation="h", title=questions[question_key], color_discrete_sequence=colors)
        fig.update_layout(font=dict(size=font_size), showlegend=False)
        st.plotly_chart(fig)
    elif graph_type == "Gráfico de pastel":
        fig = px.pie(opciones_respuesta, values="Total", names="Opción de Respuesta", title=questions[question_key], color_discrete_sequence=colors)
        fig.update_layout(font=dict(size=font_size))
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
