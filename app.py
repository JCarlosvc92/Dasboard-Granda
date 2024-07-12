import streamlit as st

# Simulación de roles
roles = ["Administrador", "Usuario"]

# Simulación de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Función para mostrar el formulario de inicio de sesión
def login():
    st.image("static/img/logo.png")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        # Autenticación simulada
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.session_state.role = "Administrador"
        elif username == "user" and password == "user":
            st.session_state.authenticated = True
            st.session_state.role = "Usuario"
        else:
            st.error("Credenciales incorrectas")

# Mostrar el menú principal si está autenticado
if st.session_state.authenticated:
    selected_role = st.session_state.role

    st.sidebar.title("Menú de Navegación")
    st.sidebar.selectbox("Seleccionar Rol", roles, index=roles.index(selected_role))

    if selected_role == "Administrador":
        st.sidebar.title("Menú de Administrador")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.authenticated = False

        st.markdown("# Panel de Control del Administrador")
        st.button("Subir Datos")
        st.button("Gestión de Usuarios")
    elif selected_role == "Usuario":
        st.sidebar.title("Menú de Usuario")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.authenticated = False

        st.markdown("# Panel de Control del Usuario")
        st.button("Subir Datos")
else:
    login()
