import json

def obtener_contexto_callejero(region='españa'):
    """
    Proporciona una breve descripción del uso de modismos y jerga en la región indicada.
    Esto permite ajustar el tono según el contexto cultural.
    """
    contextos = {
        "mexico": "En México, el lenguaje callejero se caracteriza por expresiones coloridas y un toque irreverente.",
        "españa": "En España, se emplean modismos que pueden sonar bruscos pero reflejan la autenticidad de su cultura urbana.",
        "argentina": "En Argentina, el lunfardo y las expresiones del barrio son parte del habla cotidiana."
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