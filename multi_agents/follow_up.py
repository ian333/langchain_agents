import json
from supabase import create_client
from decouple import config

import os 


from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate

from supabase import create_client
from decouple import config
# Proyecto Admin

    ### Gemini
import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AIzaSyDqRltPWDD4-HUxSJ9FzkEuCQ3T1F2lqKg"
from langchain_google_genai import ChatGoogleGenerativeAI



def process_questions(questions_text):
    # Separar la cadena de texto en una lista de preguntas usando punto y coma como separador
    questions = questions_text.split(';')

    # Limpiar espacios en blanco y saltos de línea
    questions = [q.strip() for q in questions if q.strip()]

    # Convertir cada pregunta en un diccionario con la estructura deseada
    followups = [{"question": q} for q in questions]
    print(followups)

    return {"followup": followups}


def save_followups_to_db(followups, table_name):
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase = create_client(url_user, key_user)

    # Insertar los datos en la tabla de Supabase
    response = supabase.table(table_name).insert(followups).execute()
    print(response)

async def run_follow(query,id=None):
    prompt_template = ChatPromptTemplate.from_template(    """
Your job is to give me a list of questions related to {query}.
IMPORTANT -------------------------------
Please, return only 4 questions in list format separated by semicolon (;) in this manner:
Question1;Question2;Question3;Question4
IMPORTANT -------------------------------
FOLLOW THE INSTRUCTIONS TO THE LETTER SEPARATED BY SEMICOLON
#example 1
What's the best way to store dried herbs?;What are some low-impact exercises suitable for seniors?;Can you recommend some easy beginner woodworking projects?;Is it possible to propagate succulent plants using leaves?

#example 2
How do I make homemade pasta without a machine?;Which vegetables grow well in containers?;Are there any good online resources for learning new languages?;Should I use oil or butter when cooking with garlic?

Additionally, please respond in the same language as the query. For example, if the query is in Spanish, your response should also be in Spanish.

                                                       
    """)
        # Initialize the language model
    llm = ChatGoogleGenerativeAI(model="gemini-pro")



    chain = prompt_template | llm
    

    result = chain.invoke({"query": query})
    print(result.content)

    followups = process_questions(result.content)

    if id is not None:
        url_user: str = config("SUPABASE_USER_URL")
        key_user: str = config("SUPABASE_USER_KEY")
        
        supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)
        supabase_user.table("responses_tb").update({"followup": followups}).eq("id", id).execute()
    return followups
