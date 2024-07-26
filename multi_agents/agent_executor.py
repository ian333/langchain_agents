from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent, create_structured_chat_agent, agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from datetime import datetime
from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA
from multi_agents.web_search import WebSearch
from supabase import create_client, Client
from decouple import config
# Proyecto Admin
from multi_agents.follow_up import run_follow

import os
os.environ["FIREWORKS_API_KEY"] = config("FIREWORKS_API_KEY")

from database.supa import supabase_admin, supabase_user

from langchain_core.prompts import ChatPromptTemplate
from langchain_fireworks import Fireworks

from langchain_openai import ChatOpenAI
from datetime import datetime

import asyncio
loop = asyncio.get_event_loop()

### Gemini
import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")
from langchain_google_genai import ChatGoogleGenerativeAI
from Prompt_languages import spanish,english

## Idiomas
from Prompt_languages import english, spanish

import time

async def run_agent(query, member_id=None, courseid=None, custom_prompt=None, thread_id=None, prompt=None, history=None, orgid=None, language="english", web="", videos="", sources="", follow_up_questions="",type=None,custom_ai=None):
    start_time = time.time()
    print(f"\033[94mStarting run_agent at {start_time}\033[0m")

    # Proyecto Usuario
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase_user: Client = create_client(supabase_url=url_user, supabase_key=key_user)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")


    tb = supabase_user.table("threads_tb").select("*").eq("courseid", courseid).execute().data
    user_data = ""
    thread_metrics = ""
    for data in tb:
        user_data = user_data + str(data["thread_summary"])
        thread_metrics = thread_metrics + str(data["thread_metrics"])

    if language == "english":
        main_prompt = english.main_prompt
        if custom_prompt=="AI_companion":
            main_prompt=english.ai_companion
    elif language == "spanish":
        
        main_prompt = spanish.main_prompt
        if custom_prompt=="AI_companion":
            main_prompt=spanish.ai_companion
    if custom_ai:
        # main_prompt=custom_ai
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")




    # Configurar el prompt y el modelo
    prompt_template = ChatPromptTemplate.from_template(main_prompt)


    chain = prompt_template | llm
    # Crear el contexto y el mensaje del usuario para la consulta
    user_message = query  # Asumiendo que query contiene el mensaje actual del usuario

    # Ejecutar la cadena y obtener el resultado
    result = chain.invoke({"history": history,
                           "user_message": user_message,
                           "custom_prompt": custom_prompt,
                           "user_information": user_data,
                           "thread_metrics": "",
                           "web": web,
                           "videos": videos,
                           "sources": sources
                           })
    result = result.content
    print("-------------😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍----")
    print("Esto es lo que mandamos a la IA 🤖", {"history": history, "user_message": user_message, "custom_prompt": custom_prompt, "user_information": user_data, "thread_metrics": ""})
    print(result)
    print("-------------😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍----")

    try:
        id, first_response, thread_id = await save_agent_response(thread_id=thread_id, member_id=member_id, courseid=courseid, answer=result, prompt=query, videos=videos, sources=sources, orgid=orgid, history=history, follow_up_questions=follow_up_questions,type=type)
    finally:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"\033[93mrun_agent completed in {response_time:.4f} seconds\033[0m")
        
    return id, first_response

async def save_agent_response(thread_id, answer, courseid=None, member_id=None, prompt=None, followup=None, videos=None, sources=None, fact=None, orgid=None, history=None, follow_up_questions=None,type="Chat"):
    first_response = False
    start_time = time.time()
    print(f"\033[94mStarting save_agent_response at {start_time}\033[0m")

    # Proyecto Usuario
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase_user: Client = create_client(supabase_url=url_user, supabase_key=key_user)
    
    # Preparar los datos para insertar
    thread_exists = supabase_user.table("threads_tb").select("*").eq("id", thread_id).execute().data

    if not thread_exists:
        first_response = True
        thread_data = {
            "id": thread_id,
            "threadname": prompt,
            # Añadir aquí más campos si son necesarios, por ejemplo:
            "memberid": member_id,
            "courseid": courseid,
            "created_at": datetime.now().isoformat(),
            "organizationid": orgid,
            "first_response": answer,
        }
        print(thread_data)
        response = supabase_user.table("threads_tb").insert(thread_data).execute()

    response_data = {
        "threadid": thread_id,
        "prompt": prompt,
        "created_at": datetime.now().isoformat(),
        "answer": answer,
        "followup": follow_up_questions,
        "videos": videos,
        "sources": sources,
        "fact": fact,
        "memberid": member_id,
        "organizationid": orgid,
        "typeOf":type

    }
    # Insertar los datos en la tabla responses_tb
    print(response_data)
    response = supabase_user.table("responses_tb").insert(response_data).execute()
    id = response.data[0]["id"]

    end_time = time.time()
    response_time = end_time - start_time
    print(f"\033[93msave_agent_response completed in {response_time:.4f} seconds\033[0m")

    return id, first_response, thread_id
