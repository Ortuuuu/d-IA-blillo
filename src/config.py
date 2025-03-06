import os
import utils
import streamlit as st

from openai import AzureOpenAI
from dotenv import load_dotenv

# dotenv
load_dotenv()
MODELO = os.getenv("MODELO")
ENDPOINT = os.getenv("ENDPOINT")
KEY = os.getenv("KEY")
VERSION = os.getenv("VERSION")

client = AzureOpenAI(
    azure_endpoint = ENDPOINT,
    api_key = KEY,
    api_version = VERSION
)

lista_tools = [
    {
        "type": "function",
        "function": {
            "name": "obtener_contexto_callejero",
            "description": "Proporciona una breve descripción del uso de modismos y jerga en la región indicada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Región a consultar",
                        "enum": ["mexico", "españa", "argentina"]
                    }
                },
                "required": ["region"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_dato_psicologico",
            "description": "Devuelve un dato curioso o una pseudo-estadística sobre el tema indicado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tema": {
                        "type": "string",
                        "description": "Tema a consultar",
                        "enum": ["ansiedad", "estrés", "depresión"]
                    }
                },
                "required": ["tema"]
            }
        }
    }
]

aux_funcs = {
    "obtener_contexto_callejero": utils.obtener_contexto_callejero,
    "obtener_dato_psicologico": utils.obtener_dato_psicologico
}

# Calcula la ruta absoluta de la carpeta 'data'
# 'config.py' y la carpeta 'data' están al mismo nivel dentro de 'src'
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Construye la ruta completa al archivo 'frases_graciosas.txt'
FRASES_GRACIOSAS_PATH = os.path.join(DATA_DIR, "frases_graciosas.txt")
# Lee el contenido del archivo y guárdalo en la variable main_template
with open(FRASES_GRACIOSAS_PATH, "r", encoding="utf-8") as f:
    # Lee todo el contenido como un solo string
    contenido = f.read()
# Separa las frases usando la coma como delimitador y elimina espacios en blanco alrededor
frases_graciosas = [frase.strip() for frase in contenido.split("\n") if frase.strip()]


#TEMPLATE ORQUESTADOR
MAIN_TEMPLATE_PATH = os.path.join(DATA_DIR, "main_template.txt")
with open(MAIN_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    main_template = f.read()


#TEMPLATE DRDESCARO
TEMPLATE_DRDESCARO_PATH = os.path.join(DATA_DIR, "template_drDescaro.txt")
with open(TEMPLATE_DRDESCARO_PATH, "r", encoding="utf-8") as f:
    template_drDescaro = f.read()


#TEMPLATE TRADUCTORGROSERO
TEMPLATE_TRADUCTORGROSERO_PATH = os.path.join(DATA_DIR, "template_traductorGrosero.txt")
with open(TEMPLATE_TRADUCTORGROSERO_PATH, "r", encoding="utf-8") as f:
    template_traductorGrosero = f.read()


#TEMPLATE INSOLENTEAMARGADO
TEMPLATE_INSOLENTEAMARGADO_PATH = os.path.join(DATA_DIR, "template_insolenteAmargado.txt")
with open(TEMPLATE_INSOLENTEAMARGADO_PATH, "r", encoding="utf-8") as f:
    template_insolenteAmargado = f.read()
    