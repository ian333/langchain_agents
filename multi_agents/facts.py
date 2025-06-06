import json
from supabase import create_client
from decouple import config

import os 


from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate

from supabase import create_client
from decouple import config
# Proyecto Admin




def process_questions(questions_text):
    # Separar la cadena de texto en una lista de preguntas usando punto y coma como separador
    questions = questions_text.split(';')

    # Limpiar espacios en blanco y saltos de línea
    questions = [q.strip() for q in questions if q.strip()]

    # Convertir cada pregunta en un diccionario con la estructura deseada
    followups = [{"question": q, "url": "https://ejemplo.com"} for q in questions]

    return {"followup": followups}


def save_followups_to_db(followups, table_name):
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase = create_client(url_user, key_user)

    # Insertar los datos en la tabla de Supabase
    response = supabase.table(table_name).insert(followups).execute()
    print(response)

def run_follow(query):
    prompt_template = ChatPromptTemplate.from_template(    """
    Tu trabajo es darme una lista de preguntas relacionadas a {query}.
    Por favor, devuelve las preguntas en formato de lista separadas por punto y coma (;) de esta manera:
    Pregunta1;Pregunta2;Pregunta3
    """)
    model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    chain = prompt_template | model

    result = chain.invoke({"query": query})
    print(result.content)

    followups = process_questions(result.content)
    # save_followups_to_db(followups, "your_table_name")

    return followups
