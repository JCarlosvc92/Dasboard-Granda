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
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username == "admin" and password == "lcm2024":
            st.session_state["logged_in"] = True
        else:
            st.error("Usuario o contraseña incorrectos")
            
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
        data = opciones_respuesta
        labels = list(opciones_respuesta.keys())
        values = list(opciones_respuesta.values())
    else:
        data = df[question].value_counts(normalize=True) * 100
        labels = data.index
        values = data.values
    
    all_responses = df[df[question].apply(lambda x: str(x).isdigit())][question].astype(int)
    mean_response = all_responses.mean()
    
    st.write(f"Media de la pregunta: {mean_response:.2f}%")

    if "No opina/No conoce" in labels and len(df[df[question] == "No opina/No conoce"]) > 0:
     show_no_opina = True
     no_opina_index = labels.index("No opina/No conoce")
    else:
     show_no_opina = False

    if "No opina/No conoce" in labels and not show_no_opina:
        idx = labels.index("No opina/No conoce")
        del labels[idx]
        del values[idx]

    if question == "P09":
        if colors:
            custom_colors = ['#00B050' if label == 'Sí' else '#C00000' for label in labels]
            if show_no_opina:
                custom_colors.append("#808080")
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'},
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, custom_colors)})
        else:
            fig = px.bar(x=labels, y=values,
                         labels={'x': 'Respuesta', 'y': 'Porcentaje'})
    elif question == "LC":
        custom_colors = []
        for label in labels:
            if label == "Aprobación":
                custom_colors.append("#00B050")
            elif label == "Apropiación":
                custom_colors.append("#92D050")
            elif label == "Aceptación":
                custom_colors.append("#FFC000")
            elif label == "Rechazo":
                custom_colors.append("#C00000")
        if show_no_opina:
            custom_colors.append("#808080")
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
            fig = px.bar(x=values, y=labels, orientation='h',
                         labels={'y': 'Respuesta', 'x': 'Porcentaje'},
                             color=labels,
                             color_discrete_map={val: col for val, col in zip(labels, colors)})
        elif graph_type == "Gráfico de pastel":
            fig = px.pie(names=labels,
                         values=values,
                         title=f"Frecuencia de respuestas para {questions[question]}",
                         color=labels,
                         color_discrete_map={val: col for val, col in zip(labels, colors)})

    fig.update_layout(title=f"Frecuencia de respuestas para {questions[question]}",
                      xaxis_title='Respuesta',
                      yaxis_title='Porcentaje',
                      font=dict(size=font_size))

    return fig

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        logo_base64 = load_logo(logo_image_path)
        st.markdown(html_title_template.substitute(logo=logo_base64), unsafe_allow_html=True)
        st.sidebar.title("Menú de Opciones")
        selected = option_menu("Menú", ["Página Principal", "Gráfico de barras", "Tabla cruzada"],
                               icons=["house", "bar-chart", "table"],
                               menu_icon="cast", default_index=0)

        df = pd.read_csv('prueba.csv')
        preguntas = df.columns

        if selected == "Página Principal":
            st.title("Bienvenido a la Página Principal")
            st.write("Aquí puedes colocar información general de la aplicación.")

        elif selected == "Gráfico de barras":
            st.title("Gráfico de barras")
            selected_question = st.selectbox("Selecciona una pregunta", preguntas)
            graph_type = st.selectbox("Selecciona el tipo de gráfico", ["Gráfico de barras", "Gráfico de barras horizontales", "Gráfico de pastel"])
            font_size = st.slider("Tamaño de la fuente", 10, 30, 18)
            colors = st.color_picker("Elige un color")
            colors = [colors] * len(df[selected_question].unique())
            fig = plot_question(df, selected_question, graph_type, questions, font_size=font_size, colors=colors)
            st.plotly_chart(fig)

        elif selected == "Tabla cruzada":
            st.title("Tabla cruzada")
            preguntas_seleccionadas = st.multiselect("Selecciona las preguntas", preguntas)
            selected_question_key = st.selectbox("Selecciona la pregunta de columna", preguntas)
            if st.button("Calcular tabla cruzada"):
                tabla_cruzada = calcular_tabla_cruzada(df, preguntas_seleccionadas, selected_question_key)
                if tabla_cruzada is not None:
                    st.table(tabla_cruzada)

# Run the main function
if __name__ == "__main__":
    main()
