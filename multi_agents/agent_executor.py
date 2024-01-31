from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from datetime import datetime

from supabase import create_client
from decouple import config
# Proyecto Admin

import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# Definición de las herramientas personalizadas
@tool
def add_one_one() -> int:
    """Suma 1 + 1."""
    return 1 + 1

@tool
def add_two_two() -> int:
    """Suma 2 + 2."""
    return 2 + 2

# Configuración de las herramientas para el agente
def setup_tools():
    tools = [add_one_one, add_two_two]
    return tools

# Creación del agente
def create_agent(context=None):
    tools = setup_tools()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    if context:
        print(context)
        custom_prompt = hub.pull("hwchase17/openai-functions-agent")
        custom_prompt.messages[0].prompt.template=context
        print(type(custom_prompt))
        print(custom_prompt.messages[0].prompt.template)
        print("----------")
        print(custom_prompt[0])
        print(custom_prompt[1])

    
    agent = create_openai_functions_agent(llm, tools, custom_prompt)
    return agent, tools

# Creación del ejecutor del agente
def create_agent_executor(custom_prompt=None):
    agent, tools = create_agent(context=custom_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

# Función para ejecutar el agente con una consulta dada
def run_agent(query,member_id=None, courseid=None,custom_prompt=None,thread_id=None,prompt=None,videos=None):
    print(custom_prompt)
    agent_executor = create_agent_executor(custom_prompt=custom_prompt)
    result = agent_executor.invoke({"input": query})
    save_agent_response(thread_id=thread_id,memberid=member_id,courseid=courseid,answer=result["output"],prompt=query,videos=videos)
    return result





def save_agent_response(thread_id,answer,courseid=None,memberid=None,prompt=None, followup=None, videos=None, sources=None, fact=None):
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
            "memberid": memberid,
            "courseid": courseid,
            "created_at": datetime.now().isoformat()
        }
        print(thread_data)
        supabase_user.table("threads_tb").insert(thread_data).execute()


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



    
#   "videos": [
#     {
#       "url": "https://www.youtube.com/watch?v=SEps-sO9GyM",
#       "title": "Women Leaders | Path to Management | New York Life Insurance Company",
#       "thumbnailUrl": "https://i.ytimg.com/vi/SEps-sO9GyM/maxresdefault.jpg"
#     },

    response = supabase_user.table("responses_tb").insert(response_data).execute()
    
    # Verificar y manejar la respuesta
    print(response)