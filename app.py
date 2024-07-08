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

    # Logo de la empresa
    st.image('url_del_logo_de_la_empresa.png', use_column_width=True)

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
