import streamlit as st

def main():
    # Configurar la página
    st.set_page_config(page_title='Login Personalizado', layout='wide')

    # Fondo de la página
    page_bg_img = '''
    <style>
    body {
        background-image: url("https://url_de_tu_imagen_de_fondo.jpg");
        background-size: cover;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Centro de la página
    col1, col2, col3 = st.beta_columns([1, 3, 1])  # Ajusta los valores según sea necesario

    # Logo de la empresa centrado
    with col2:
        st.image('static/img/logo.png', width=200)  # Ajusta el tamaño del logo aquí

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
