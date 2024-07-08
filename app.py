import streamlit as st

def main():
    # Configurar la página
    st.set_page_config(page_title='Login Personalizado', layout='wide')

    # Fondo de la página
    page_bg_img = '''
    <style>
    body {
        background-image: url("https://www.google.com/url?sa=i&url=https%3A%2F%2Fes.pngtree.com%2Ffreebackground%2Fdark-blue-background-abstract-with-modern-banner_1739950.html&psig=AOvVaw24lMw90jAKwFeDDvLX-ue3&ust=1720540782402000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCNDv54Tol4cDFQAAAAAdAAAAABAE");
        background-size: cover;
        background-position: center;
        height: 100vh; /* Ajusta la altura de la página */
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Contenedor para centrar el contenido
    st.markdown(
        '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">'
        '<img src="static/img/logo.png" style="width: 200px;">'
        '</div>',
        unsafe_allow_html=True
    )

    # Título
    st.title('Inicio de Sesión')

    # Formulario de inicio de sesión
    username = st.text_input('Usuario')
    password = st.text_input('Contraseña', type='password')
    if st.button('Iniciar Sesión'):
        # Lógica de autenticación aquí (por ejemplo, verificar en una base de datos)
        if username == 'usuario' and password == 'contraseña':
            st.success('Inicio de sesión exitoso')
        else:
            st.error('Credenciales incorrectas')

if __name__ == '__main__':
    main()
