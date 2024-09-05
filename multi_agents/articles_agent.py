from fastapi import FastAPI, HTTPException, status, Form
from pydantic import BaseModel
from uuid import uuid4
from database.supa import supabase_user
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from decouple import config
import os

os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI

class ArticleRequest(BaseModel):
    prompt: str
    courseid: str
    projectid: str
    memberid: str
    organizationid: str

# Definir el prompt detallado para la generación de artículos
article_prompt_template = """
Escribe un artículo extenso y detallado sobre el siguiente tema:

Tema: {topic}

El artículo debe incluir:

1. **Introducción**:
    - Proporciona una visión general del tema.
    - Menciona la importancia y relevancia en el contexto actual.
    - Introduce los puntos clave que se abordarán.

2. **Desarrollo**:
    - **Antecedentes Históricos**: Describe brevemente la evolución del tema.
    - **Estado Actual**: Explica cómo se percibe y utiliza el tema en la actualidad.
    - **Principales Desafíos y Oportunidades**: Detalla los retos y oportunidades asociados al tema.
    - **Aplicaciones Prácticas**: Proporciona ejemplos específicos de cómo se aplica este tema en diversas industrias o campos.

3. **Perspectivas Futuras**:
    - Discute las posibles tendencias y desarrollos futuros relacionados con el tema.
    - Menciona cualquier investigación emergente o tecnologías disruptivas que puedan influir en el futuro del tema.

4. **Conclusión**:
    - Resume los puntos clave discutidos en el artículo.
    - Proporciona una reflexión final sobre la importancia del tema y sus implicaciones.

5. **Referencias**:
    - Incluye referencias relevantes y actualizadas que respalden la información proporcionada en el artículo.

**Formato**:
- Utiliza lenguaje formal pero accesible.
- Mantén la coherencia en la estructura y el flujo del artículo.
- Evita jergas técnicas excesivas, a menos que sean necesarias y se expliquen adecuadamente.

CONTESTA EN EL IDIOMA QUE TE HABLAN

Comienza el artículo a continuación:
"""

# Función para generar el artículo usando LangGraph
async def make_article(topic: str):
    print(f"\033[94m[INFO] Iniciando la generación del artículo para el tema: {topic}\033[0m")

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        print(f"\033[92m[INFO] Modelo LLM 'gemini-1.5-pro' inicializado correctamente.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al inicializar el modelo LLM: {e}\033[0m")
        raise

    try:
        # Crear el agente usando LangGraph
        app = create_react_agent(
            model=llm, 
            tools=[], 
            state_modifier=f"Eres un asistente útil. Responde en un lenguaje formal y enfocado en proveer información precisa y completa sobre el tema '{topic}'."
        )
        print(f"\033[92m[INFO] Agente creado exitosamente.\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Error al crear el agente: {e}\033[0m")
        raise

    try:
        # Generar el artículo
        print(f"\033[94m[INFO] Enviando solicitud para generar el artículo...\033[0m")
        messages =   app.invoke({"messages": [("human", article_prompt_template.format(topic=topic))]})
        print(f"\033[92m[INFO] Artículo generado con éxito.\033[0m")
        print(messages)
        return messages["messages"][-1].content
    except Exception as e:
        print(f"\033[91m[ERROR] Error al generar el artículo: {e}\033[0m")
        raise