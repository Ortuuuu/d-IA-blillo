import random
import streamlit as st
import config

from models.drDescaro import drDescaro
from models.elInsolenteAmargado import elInsolenteAmargado
from models.traductorGrosero import traductorGrosero
from PIL import Image

AGENTES = {
    "drDescaro": drDescaro,
    "traductorGrosero": traductorGrosero,
    "elInsolenteAmargado": elInsolenteAmargado,
}

def main():
    # Al iniciar la sesión, creamos el token si no existe
    if "token" not in st.session_state:
        config.utils.reset_token(config.TOKEN_EXPIRY_MINUTES, config.SECRET_KEY, config.ALGORITHM)

    # Si la sesión ha expirado, se le indica al usuario que debe refrescar
    if config.utils.session_expired(config.TOKEN_EXPIRY_MINUTES):
        st.error("Tu sesión ha expirado. Por favor, refresca la página para continuar.")
        return
    
    # Configuración de la app
    st.set_page_config(page_title="d(IA)blillo", page_icon="😈")
    st.title("😈d(IA)blillo😈")

    st.markdown('''
    ¡Bienvenido! ¿Preparado para que te vacile un rato? Escribe tu consulta y jódete con mi respuesta.
    Cuando no aguantes más mi genialidad, simplemente escribe 'Salir' y vete a soplar gaitas por ahí :)
    ''')

    # Inyectar CSS para cambiar bg y colores (cuadros de input, letra...)
    st.markdown(
        """
        <style>
        /* Cambiar el fondo general */
        [data-testid="stAppViewContainer"] {
            background-color: #2B2D42; /* azul grisáceo oscuro */
        }

        /* Cambiar el color de texto por defecto */
        html, body, [class*="css"], p  {
            color: #FFFFFF; /* blanco */
        }

        /* Ajustar el fondo y color de los mensajes del chat */
        [data-testid="stChatMessage"] {
            background: rgba(255, 255, 255, 0.1);
            color: #FFFFFF;
        }

        /* Ajustar el fondo del input de chat */
        [data-testid="stChatInputContainer"] {
            background: rgba(255, 255, 255, 0.3);
            color: #000000; /* Texto más oscuro en el input */
        }

        /* Ajustar título */
        h1 {
            color: red !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
    avatar_usuario = Image.open("./src/data/user.png")
    avatar_asistente = Image.open("./src/data/bot.jfif")

    # Estado de la conversación
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Creamos el historial de mensajes relevantes de retroalimentación de la app
    if "historial" not in st.session_state:
        st.session_state.historial = []

    # Mostrar historial de conversación
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message['avatar']):
            st.markdown(message["content"])

    # Entrada del usuario, puede ser texto o pdf
    # Cuadro de inserción de texto
    user_req = st.chat_input("Escribe tu consulta:")
    # Cuadro de inserción de pdf's
    uploaded_file = st.file_uploader("Carga un archivo PDF", type='pdf')

    #Si se inserta una consulta:
    if user_req:
        # Antes de procesar, comprobamos si la sesión ha expirado
        if config.utils.session_expired(config.TOKEN_EXPIRY_MINUTES):
            st.error("Tu sesión ha expirado. Por favor, refresca la página para continuar.")
            return
        
        with st.spinner("Pensando...🤓🤓", show_time=True):
            # Agregar mensaje del usuario al estado sl
            st.session_state.messages.append({"role": "user", "content": user_req, 'avatar': avatar_usuario})
            # Agregar mensaje del usuario al estado historial
            st.session_state.historial.append({"role": "user", "content": user_req})
            with st.chat_message("user", avatar=avatar_usuario):
                st.markdown(user_req,)

            historial = st.session_state.historial[-25:]

            # Intentamos obtener contexto útil de la BD. 
            # Se asume que la colección "users_docs" ya existe o fue creada al ingestar PDFs previamente.
            context_docs = config.utils.get_context_from_db(user_req, config.collection, similarity_threshold=0.8, k=8)
            if context_docs:
                context_str = "\n".join(context_docs)
                prompt = f"Utiliza el siguiente contexto para responder:\n{context_str}\n\nPregunta: {user_req}"
            else:
                prompt = user_req

            # Enviar la consulta y el prompt del orquestador al modelo
            messages = [
                {"role": "system", "content": config.main_template},
                {"role": "user", "content": prompt}
            ]

            try:
                response = config.client.chat.completions.create(
                    model = config.MODELO,
                    messages = messages,
                )
            except Exception as e:
                print(f"ERROR: {e}")
                response = random.choice(config.frases_graciosas)

            # Si salta la excepción por el filtro de azure, no se llega a instanciar response nunca, por lo que le meto yo un string del txt de frases
            if isinstance(response, str):
                with st.chat_message("assistant", avatar = avatar_asistente):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response, 'avatar': avatar_asistente})
                st.session_state.historial.append({"role": "assistant", "content": response})
            else:
                # Extraer el nombre del agente seleccionado
                selected_agent = response.choices[0].message.content.strip()

                # Verificar si el nombre corresponde a un agente definido
                if selected_agent in AGENTES:
                    # Llamar a la función del agente seleccionado, pasando la consulta original
                    result = AGENTES[selected_agent](prompt, historial)

                    # Si salta el filtro en la respuesta y, por lo tanto, al cliente le viene como respuesta el objeto None, se controla dicha situación:
                    if result == None:
                        result = random.choice(config.frases_graciosas)
                        # Mostrar respuesta del bot
                        with st.chat_message("assistant", avatar = avatar_asistente):
                            st.markdown(result)
                        st.session_state.messages.append({"role": "assistant", "content": result, 'avatar': avatar_asistente})
                        st.session_state.historial.append({"role": "assistant", "content": result})
                    else:
                        # Mostrar respuesta del bot
                        with st.chat_message("assistant", avatar = avatar_asistente):
                            st.markdown(result)
                        st.session_state.messages.append({"role": "assistant", "content": result, 'avatar': avatar_asistente})
                        st.session_state.historial.append({"role": "assistant", "content": result})
                else:
                    st.write("No se reconoció el agente seleccionado. Intenta de nuevo.")
                    print("ORQUESTADOR FALLANDO!!!!!!!")
            # Tras una interacción exitosa, reseteamos el token para mantener la sesión viva
            config.utils.reset_token(config.TOKEN_EXPIRY_MINUTES, config.SECRET_KEY, config.ALGORITHM)
    # Si se inserta un PDF:
    elif uploaded_file is not None:
        # Antes de procesar, comprobamos si la sesión ha expirado
        if config.utils.session_expired(config.TOKEN_EXPIRY_MINUTES):
            st.error("Tu sesión ha expirado. Por favor, refresca la página para continuar.")
            return
        
        with st.spinner("Procesando documento... 🤖🤖", show_time=True):
            # Validamos que el archivo sea un PDF
            if not uploaded_file.name.lower().endswith('.pdf'):
                st.error("El formato del documento no está soportado!")
                return
            
            if config.utils.ingest_document(uploaded_file, config.collection) == True:
                st.success("Documento procesado correctamente.")
            else:
                st.error("No ha sido posible procesar el documento.")

            # Tras una interacción exitosa, reseteamos el token para mantener la sesión viva
            config.utils.reset_token(config.TOKEN_EXPIRY_MINUTES, config.SECRET_KEY, config.ALGORITHM)

if __name__ == "__main__":
    main()