from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent,create_structured_chat_agent,agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from datetime import datetime

from supabase import create_client
from decouple import config
# Proyecto Admin
from multi_agents.follow_up import run_follow

import uuid



from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from datetime import datetime

def run_agent(query, member_id=None, courseid=None, custom_prompt=None, thread_id=None, prompt=None, videos=None,history=None):
    # Configurar el prompt y el modelo
    prompt_template = ChatPromptTemplate.from_template("Este es tu contexto de quien eres{custom_prompt},This is the story of the chat, lo unico que quiero que respondas es user_message {history} esto es para darte contexto de lo que esta pasando, this is the question of the user, solo responde esto {user_message}, return the answer of the user")
    model = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
    chain = prompt_template | model

    # Crear el contexto y el mensaje del usuario para la consulta
    user_message = query  # Asumiendo que query contiene el mensaje actual del usuario

    # Ejecutar la cadena y obtener el resultado
    result = chain.invoke({"history": history, "user_message": user_message,"custom_prompt":custom_prompt})
    print(result.content)

    # Guardar la respuesta en la base de datos
    save_agent_response(thread_id=thread_id, member_id=member_id, courseid=courseid, answer=result.content, prompt=query, videos=videos)

    return result.content





def save_agent_response(thread_id,answer,courseid=None,member_id=None,prompt=None, followup=None, videos=None, sources=None, fact=None):
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)
    # Preparar los datos para insertar
    thread_exists = supabase_user.table("threads_tb").select("*").eq("id", thread_id).execute().data
    if not thread_exists:
        thread_data = {
            "id": thread_id,
            "threadname":prompt,
            # Añadir aquí más campos si son necesarios, por ejemplo:
            "memberid": member_id,
            "courseid": courseid,
            "created_at": datetime.now().isoformat()
        }
        print(thread_data)
        supabase_user.table("threads_tb").insert(thread_data).execute()

    followup=run_follow(prompt)
    response_data = {
        "threadid": thread_id,
        "prompt": prompt,
        "created_at": datetime.now().isoformat(),
        "answer": answer,
        "followup": followup,
        "videos": videos,
        "sources": sources,
        "fact": fact
    }
    
    # Insertar los datos en la tabla responses_tb
    print(response_data)

    # response = supabase_user.table("responses_tb").select("*").eq("threadid", "4a37be7f-ce2c-4f19-aaaa-15f6d334a908").execute().data[0]
    response = supabase_user.table("responses_tb").insert(response_data).execute()
    
    # Verificar y manejar la respuesta
    print(response)