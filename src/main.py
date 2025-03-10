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
        with st.spinner("Pensando...🤓🤓", show_time=False):
            # Agregar mensaje del usuario al estado sl
            st.session_state.messages.append({"role": "user", "content": user_req, 'avatar': avatar_usuario})
            # Agregar mensaje del usuario al estado historial
            st.session_state.historial.append({"role": "user", "content": user_req})
            with st.chat_message("user", avatar=avatar_usuario):
                st.markdown(user_req,)

            historial = st.session_state.historial[-25:]
            # Enviar la consulta y el prompt del orquestador al modelo
            messages = [
                {"role": "system", "content": config.main_template},
                {"role": "user", "content": user_req}
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
                    result = AGENTES[selected_agent](user_req, historial)

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
    # Si se inserta un PDF:
    elif uploaded_file is not None:
        with st.spinner("Procesando documento... 🤖🤖", show_time=False):
            # Validamos que el archivo sea un PDF
            if not uploaded_file.name.lower().endswith('.pdf'):
                st.error("El formato del documento no está soportado!")
                return

            st.info(f"Cargando {uploaded_file.name}...")

            collection = config.db_client.get_or_create_collection(name="users_docs", metadata={"hnsw:space": "cosine"}, embedding_function=config.embeddingModel)

            config.utils.ingest_document(uploaded_file, config.embeddingModel, collection, config.DATA_DIR, config.db_client)

        st.success("Documento ingresado correctamente en la base de datos vectorial (ChromaDB)!")


if __name__ == "__main__":
    main()