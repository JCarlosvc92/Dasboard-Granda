import streamlit as st

def main():
    # Configurar la página
    st.set_page_config(page_title='Login Personalizado', layout='wide')

    # Rutas de las imágenes
    fondo_path = 'static/img/fondo.png'
    logo_image_path = 'static/img/logo.png'

    # Fondo de la página
    page_bg_img = f'''
    <style>
    body {{
        background-image: url("{fondo_path}");
        background-size: cover;
        background-position: center;
        height: 100vh; /* Ajusta la altura de la página */
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Contenedor para centrar el contenido
 st.markdown(
    f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">'
    f'<img src="{logo_image_path}" style="width: 400px;">'  # Ajusta el tamaño del logo aquí
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
