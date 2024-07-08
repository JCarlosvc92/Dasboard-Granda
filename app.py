import streamlit as st

def main():
    # Configurar la página
    st.set_page_config(page_title='Login Personalizado', layout='wide')

    # Fondo de la página con CSS para centrar contenido
    page_bg_img = '''
    <style>
    body {
        background-image: url("https://url_de_tu_imagen_de_fondo.jpg");
        background-size: cover;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh; /* Ajusta el alto de la página al 100% del viewport */
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Contenedor para el contenido principal
    container = st.container()

    # Centrar el contenido dentro del contenedor
    with container:
        # Logo de la empresa
        st.image('static/img/logo.png', width=200, caption='Logo de la empresa')  # Ajusta el tamaño del logo aquí

        # Espacio para separación
        st.write('')
        
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
