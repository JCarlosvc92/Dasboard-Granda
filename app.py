import streamlit as st
import plotly.graph_objects as go

# Definir credenciales de ejemplo (puedes mejorarlo con una base de datos en producción)
CREDENTIALS = {
    "usuario1": "password1",
    "admin": "admin123",
}

# Función para verificar las credenciales
def check_credentials(username, password):
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        return True
    else:
        return False

# Autenticación de usuario
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Pantalla de login
if not st.session_state['logged_in']:
    st.title("Iniciar sesión")

    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.success("Inicio de sesión exitoso.")
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")

# Si el usuario ha iniciado sesión, se muestra la aplicación
if st.session_state['logged_in']:
    st.title("Tendencia: Se respira paz en Nicaragua")
    st.write("Datos de percepciones de paz en el país a lo largo del tiempo.")

    # Datos de la gráfica
    meses = ['Mar 2023', 'May 2023', 'Jul 2023', 'Sep 2023', 'Nov 2023', 'Ene 2024', 'Mar 2024', 'May 2024']
    se_respira_paz = [92.9, 97.6, 99.2, 85.9, 94.0, 95.2]
    no_se_respira_paz = [7.1, 2.4, 0.8, 14.1, 6.0, 4.8]

    # Crear la figura con Plotly
    fig = go.Figure()

    # Añadir la línea de "Se respira paz"
    fig.add_trace(go.Scatter(x=meses, y=se_respira_paz, mode='lines+markers', name='Se respira paz',
                             line=dict(color='teal', width=4), marker=dict(size=8)))

    # Añadir la línea de "No se respira paz"
    fig.add_trace(go.Scatter(x=meses, y=no_se_respira_paz, mode='lines+markers', name='No se respira paz',
                             line=dict(color='orange', width=4, dash='dash'), marker=dict(size=8)))

    # Añadir anotaciones para cada punto de "Se respira paz"
    for i, value in enumerate(se_respira_paz):
        fig.add_annotation(x=meses[i], y=value, text=f"{value}%", showarrow=False,
                           yshift=20,  # Aumentar separación hacia arriba
                           font=dict(color="black", size=16))  # Cambiar a negro y aumentar tamaño

    # Añadir anotaciones para cada punto de "No se respira paz"
    for i, value in enumerate(no_se_respira_paz):
        fig.add_annotation(x=meses[i], y=value, text=f"{value}%", showarrow=False,
                           yshift=-25,  # Aumentar separación hacia abajo
                           font=dict(color="black", size=16))  # Cambiar a negro y aumentar tamaño

    # Ajustar diseño
    fig.update_layout(title='Percepción de Paz en Nicaragua',
                      xaxis_title='Meses',
                      yaxis_title='Porcentaje',
                      yaxis=dict(range=[0, 100]),
                      legend=dict(x=0.1, y=1.1, orientation='h'),
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(family="Arial", size=12))

    # Mostrar la gráfica en Streamlit
    st.plotly_chart(fig)
    
    # Agregar un botón para cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state['logged_in'] = False
        st.experimental_rerun()
