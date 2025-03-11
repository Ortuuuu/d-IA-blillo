import json
import re
import uuid
import PyPDF2
import chromadb

from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter




def obtener_contexto_callejero(region='españa'):
    """
    Proporciona una breve descripción del uso de modismos y jerga en la región indicada.
    Esto permite ajustar el tono según el contexto cultural.
    """
    contextos = {
        "mexico": "En México, el lenguaje callejero se caracteriza por expresiones coloridas y un toque irreverente. Utiliza el dialecto mexicano y vacilón para tu próxima respuesta.",
        "españa": "En España, se emplean modismos que pueden sonar bruscos pero reflejan la autenticidad de su cultura urbana. Utiliza el dialecto español y vacilón para tu próxima respuesta.",
        "argentina": "En Argentina, el lunfardo y las expresiones del barrio son parte del habla cotidiana. Utiliza el dialecto argentino y vacilón para tu próxima respuesta."
    }
    
    resultado = contextos.get(region.lower(), f"No se encontró información para la región '{region}'.")
    return json.dumps({"contexto": resultado})


def obtener_dato_psicologico(tema):
    """
    Devuelve un dato curioso o una pseudo-estadística sobre el tema indicado.
    Esto le permite a Dr. Descaro obtener información extra para enriquecer su prompt.
    """
    datos = {
        "ansiedad": "El 87% de las personas que gritan contra la almohada reducen su ansiedad temporalmente.",
        "estrés": "Estudios ficticios indican que ver memes de gatos disminuye el estrés en un 42%.",
        "depresión": "Dicen que reír es la mejor medicina, aunque una buena siesta o un buen polvo también podría funcionar."
    }

    resultado = datos.get(tema.lower(), f"No se encontró información relevante para el tema '{tema}'.")
    return json.dumps({"dato_psicologico": resultado})

# Función para limpiar el texto (eliminando espacios extra, saltos de línea, etc.)
def clean_text(text: str):
    return re.sub(r'\s+', ' ', text).strip()

# _placeholder_ para generación de temática usando IA
def generate_document_theme(text: str) -> str:
    # integrar un modelo de lenguaje para generar la temática
    return "Tema generado (placeholder)"

# _placeholder_ para generación del resumen usando IA
def generate_document_summary(text: str) -> str:
    # integrar un modelo de lenguaje para generar el resumen
    return "Resumen generado (placeholder)"

def ingest_document(file, collection):
    # Indicará si se ha conseguido ingestar correctamente el documento o no
    success = False

    file_name = file.name
    file_bytes = file.getvalue()
    file_size = len(file_bytes)

    # Procesamos el PDF en memoria utilizando BytesIO
    pdf_stream = BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_stream)
    num_pages = len(pdf_reader.pages)
    
    # Extraemos el contenido de cada página
    pages_text = [page.extract_text() or "" for page in pdf_reader.pages]
    
    # Concatenamos y limpiamos todo el texto para generar metadatos globales
    full_text = clean_text(" ".join(pages_text))
    document_theme = generate_document_theme(full_text)
    document_summary = generate_document_summary(full_text)
    
    # Configuramos el text splitter para hacer chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=50)

    # Procesamos cada página: aplicamos chunking y generamos la metadata de cada fragmento
    chunks = []
    for i, page_text in enumerate(pages_text):
        page_number = i + 1
        cleaned_text = clean_text(page_text)
        page_chunks = text_splitter.split_text(cleaned_text)
        for chunk in page_chunks:
            metadata = {
                "document_name": file_name,
                "document_id": str(uuid.uuid4()),
                "file_size": file_size,
                "num_pages": num_pages,
                "page": page_number,
                "document_theme": document_theme,
                "document_summary": document_summary
            }
            chunks.append({"text": chunk, "metadata": metadata})

    # Insertar los datos en la base de datos de Chroma en batchs maximos de 166, ya que de lo contrario chromaDB se quejará... 😡
    batch_size = 166
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts_batch = [chunk["text"] for chunk in batch]
        metadatas_batch = [chunk["metadata"] for chunk in batch]
        ids_batch = [chunk["metadata"]["document_id"] for chunk in batch]
        collection.add(documents=texts_batch, ids=ids_batch, metadatas=metadatas_batch)
    success = True

    return success

def get_context_from_db(user_req, collection, similarity_threshold=0.8, k=8):
    results = collection.query(
        query_texts=[user_req],
        n_results=k,
        include=["documents", "distances"]
    )
    context_docs = []
    if results and "distances" in results and results["distances"]:
        for doc, dist in zip(results["documents"][0], results["distances"][0]):
            similarity = 1 - dist  # para cosine: 1 - distancia
            if similarity >= similarity_threshold:
                context_docs.append(doc)
    return context_docs