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
import os
os.environ["FIREWORKS_API_KEY"] =config("FIREWORKS_API_KEY")



from langchain_core.prompts import ChatPromptTemplate
from langchain_fireworks import Fireworks

from langchain_openai import ChatOpenAI
from datetime import datetime

def run_agent(query, member_id=None, courseid=None, custom_prompt=None, thread_id=None, prompt=None, videos=None,history=None):
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
    print("-----------------")
    print(result)
    print("-----------------")
    # Guardar la respuesta en la base de datos
    id=save_agent_response(thread_id=thread_id, member_id=member_id, courseid=courseid, answer=result, prompt=query, videos=videos)

    return result,id




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
        "videos": "",
        "sources": sources,
        "fact": fact,
        "memberid":member_id
    }
    
    # Insertar los datos en la tabla responses_tb
    print(response_data)

    response = supabase_user.table("responses_tb").insert(response_data).execute()
    id=response.data[0]["id"]

    return response.data[0]["id"]
    
