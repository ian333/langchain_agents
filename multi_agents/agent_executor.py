from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent,create_structured_chat_agent,agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from datetime import datetime
from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA
from supabase import create_client
from decouple import config
# Proyecto Admin
from multi_agents.follow_up import run_follow

import uuid
import os
os.environ["FIREWORKS_API_KEY"] =config("FIREWORKS_API_KEY")



from langchain_core.prompts import ChatPromptTemplate
from langchain_fireworks import Fireworks

from langchain_openai import ChatOpenAI
from datetime import datetime

async def run_agent(query, member_id=None, courseid=None, custom_prompt=None, thread_id=None, prompt=None, videos=None,history=None,orgid=None):
    # Configurar el prompt y el modelo
    prompt_template = ChatPromptTemplate.from_template("""
                You are an advanced conversational model designed to provide accurate and contextually relevant responses. Your current role and the nature of this interaction are defined by the following specific context: {custom_prompt}. This context is crucial as it shapes your understanding, responses, and the way you engage with the user.

                Please review the history of this chat: {history}. Each interaction provides valuable insights into the ongoing conversation's direction and tone. This historical context is essential for maintaining a coherent and relevant dialogue. It helps you understand the progression of the conversation and adjust your responses accordingly.

                Your primary task is to address the user's question presented as: {user_message}. It’s imperative that you analyze both the provided context and the entirety of the chat history to tailor your response effectively. Your answer should directly address the user's inquiry, leveraging the specific details and nuances of the preceding interactions.
                """)

    model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    llm = Fireworks(
                        model="accounts/fireworks/models/mixtral-8x7b-instruct", # see models: https://fireworks.ai/models
                        temperature=0.6,
                        max_tokens=100,
                        top_p=1.0,
                        top_k=40,
                    )
    chain = prompt_template | model

    # Crear el contexto y el mensaje del usuario para la consulta
    user_message = query  # Asumiendo que query contiene el mensaje actual del usuario

    # Ejecutar la cadena y obtener el resultado
    result = chain.invoke({"history": history, "user_message": user_message,"custom_prompt":custom_prompt})
    result=result.content
    print("-------------😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍----")
    print(result)
    print("-------------😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍😍----")
    # Guardar la respuesta en la base de datos
    id,first_response,thread_id= await save_agent_response(thread_id=thread_id, member_id=member_id, courseid=courseid, answer=result, prompt=query, videos=videos,orgid=orgid)
    # yield result,id
    try:
            print("Hello 😒😒😒😒😒😒😒😒😒😒😒")
            videos = VideosQA(courseid=courseid, id=id,first_response=first_response,thread_id=thread_id)
            sources = SourcesQA(courseid=courseid, id=id)
            
            # Envía las tareas en segundo plano y continúa sin esperar a que finalicen
            # executor.submit(videos.query, prompt)
            # executor.submit(sources.query, prompt)
            video_task = asyncio.create_task(videos.query(prompt))
            source_task = asyncio.create_task(sources.query(prompt))
                # Esperar a que finalicen las tareas
            await video_task
            await source_task
    finally:        
        pass
        # return result,id



from concurrent.futures import ThreadPoolExecutor
import asyncio
loop = asyncio.get_event_loop()



async def save_agent_response(thread_id,answer,courseid=None,member_id=None,prompt=None, followup=None, videos=None, sources=None, fact=None,orgid=None):
    url_user: str = config("SUPABASE_USER_URL")
    key_user: str = config("SUPABASE_USER_KEY")
    supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)
    first_response=False
    # Preparar los datos para insertar
    thread_exists = supabase_user.table("threads_tb").select("*").eq("id", thread_id).execute().data

    if not thread_exists:
        first_response=True
        thread_data = {
            "id": thread_id,
            "threadname":prompt,
            # Añadir aquí más campos si son necesarios, por ejemplo:
            "memberid": member_id,
            "courseid": courseid,
            "created_at": datetime.now().isoformat(),
            "organizationid":orgid,
            "first_response":answer
        }
        print(thread_data)
        response=supabase_user.table("threads_tb").insert(thread_data).execute()


    followup=""
    response_data = {
        "threadid": thread_id,
        "prompt": prompt,
        "created_at": datetime.now().isoformat(),
        "answer": answer,
        "followup": followup,
        "videos": "",
        "sources": sources,
        "fact": fact,
        "memberid":member_id,
        "organizationid":orgid
    }
    # Insertar los datos en la tabla responses_tb
    print(response_data)
    response = supabase_user.table("responses_tb").insert(response_data).execute()
    id=response.data[0]["id"]
    loop.create_task(run_follow(prompt,id=id))



    return id,first_response,thread_id
    
