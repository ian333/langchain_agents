# main.py
from uuid import uuid4  # Importa esta biblioteca en la parte superior de tu archivo

# Importaciones de librerías estándar
from datetime import datetime
import time
import asyncio

# Importaciones de FastAPI
from fastapi import FastAPI, HTTPException, Request, Security, BackgroundTasks, Header
from fastapi import status

# Importaciones de Langchain y herramientas relacionadas
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

# Importaciones de utilidades y modelos propios
from utils.db_utils import save_reminder
from models.chat_models import ChatRequest, QueryRequest
from examples.chat_examples import chat_examples
from multi_agents.agent_executor import run_agent
from multi_agents.agent_utils import process_course_info  
from starlette.middleware.cors import CORSMiddleware

# Importaciones de configuración y utilidades adicionales
from decouple import config
from supabase import create_client

# Proyecto Admin
import os
from langchain.globals import set_debug
set_debug(False)

from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA
from multi_agents.web_search import WebSearch
from multi_agents.follow_up import run_follow
from database.supa import supabase_user


os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

url_admin: str = config("SUPABASE_ADMIN_URL")
key_admin: str = config("SUPABASE_ADMIN_KEY")

supabase_admin = create_client(supabase_url=url_admin,supabase_key= key_admin)

from Config.config import set_language, get_language

# Configuración de la aplicación FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origins
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

HEADER_NAME = "X-API-KEY"
api_key_header = Header(HEADER_NAME)

async def validate_api_key(api_key_header: str = Security(api_key_header)):
    API_KEY: str = config("API_KEY")
    print(API_KEY)
    print(api_key_header)
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key_header

@app.post("/chat", status_code=status.HTTP_200_OK)
async def chat_endpoint(request_body: ChatRequest, background_tasks: BackgroundTasks, api_key: str = validate_api_key):
    """
    Endpoint para procesar solicitudes de chat, interactuar con un agente y guardar la información en la base de datos.

    Args:
    - request_body (ChatRequest): Datos de la solicitud de chat.

    Returns:
    - dict: Respuesta del agente y otros detalles relevantes.
    """
    start_time = time.time()

    # Desempaquetar los datos recibidos
    courseid = request_body.courseid
    memberid = request_body.memberid
    prompt = request_body.prompt
    threadid = request_body.threadid  # Asume que ya viene generado si es necesario
    followup = request_body.followup
    email = request_body.email
    orgid = request_body.organizationid
    web = request_body.web

    if not threadid:
        threadid = str(uuid4())

    # Obtener instrucciones de la empresa desde la tabla de admin
    response = supabase_admin.table("courses_tb").select("*").eq("id", courseid).execute()
    processed_info = {}
    reference_videos = {}

    if response.data:
        admin_data = response.data[0]
        processed_info, reference_videos = process_course_info(admin_data)
        print(processed_info)

    language_data = supabase_admin.table("companies_tb").select("*").eq("id", courseid).execute()

    if language_data.data:
        language_data = language_data.data[0]
        new_language = language_data["language"]
        set_language(new_language)
        print(f"\033[92mSe definió el lenguaje 😁😁 como {get_language()}\033[0m")
    else:
        set_language("english")
        print(f"\033[92mSe definió el lenguaje 😁😁 como {get_language()}\033[0m")

    user_data = {   
        "courseid": courseid,
        "memberid": memberid,
        "prompt": prompt,
        "threadid": threadid,
        "followup": followup,
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "orgid": orgid
    }
    print(f"\033[94mUser data: {user_data}\033[0m")

    # Ejecutar las tareas en segundo plano
    background_tasks.add_task(process_request, threadid, courseid, memberid, prompt, followup, email, orgid, web, processed_info)

    # Esperar 8 segundos antes de devolver la respuesta
    await asyncio.sleep(8)
    end_time = time.time()
    response_time = end_time - start_time
    print(f"\033[93mTiempo de procesamiento: {response_time} segundos\033[0m")
    
    return {"thread_id": threadid}

async def process_request(threadid, courseid, memberid, prompt, followup, email, orgid, web, processed_info):
    try:
        start_time = time.time()

        if web == False:
            print("\033[96mHello 😒😒😒😒😒😒😒😒😒😒😒\033[0m")
            videos = VideosQA(courseid=courseid, thread_id=threadid)
            sources = SourcesQA(courseid=courseid, orgid=orgid)
            follow_task = run_follow(query=prompt, history=followup)
            
            # Ejecuta las tareas en paralelo
            video_task = videos.query(prompt)
            source_task = sources.query(prompt)
            video, source, follow_up_questions = await asyncio.gather(video_task, source_task, follow_task)
        else:
            print("\033[96m------------------------\033[0m")
            print("\033[96mHEY ENTRAMOS A WEB\033[0m")
            websearch = WebSearch(courseid=courseid, id=threadid, orgid=orgid)
            websearch_task = await asyncio.create_task(websearch.query(prompt))

        id, agent_task = await run_agent(query=prompt, courseid=courseid, member_id=memberid, custom_prompt=processed_info, prompt=prompt, thread_id=threadid, history=followup, orgid=orgid, web=web, videos=video, sources=source, follow_up_questions=follow_up_questions)

        end_time = time.time()
        response_time = end_time - start_time
        print(f"\033[93mTiempo de procesamiento total: {response_time} segundos\033[0m")

        # Guardar el tiempo de respuesta en la base de datos
        try:
            supabase_user.table("responses_tb").update({"response_sec": response_time}).eq("id", id).execute()
        except Exception as e:
            print(f"\033[91mError al actualizar la base de datos con el tiempo de respuesta: {e}\033[0m")

    except Exception as e:
        print(f"\033[91mError processing request: {e}\033[0m")

from database.Vector_database import VectorDatabaseManager
print("Se estan inicializando las VEctorDatabase")
vector_db_manager = VectorDatabaseManager()
print("Se estan inicializando las VEctorDatabase")

@app.post("/query")
async def query_database(request: QueryRequest):
    try:
        print(f"\033[94mReceived query request: {request}\033[0m")
        result = await vector_db_manager.query_instance(courseid=request.courseid, query_text=request.query_text, type=request.type)
        print(f"\033[94mQuery result: {result}\033[0m")
        return result
    except Exception as e:
        print(f"\033[91mError processing query: {e}\033[0m")
        raise HTTPException(status_code=500, detail=str(e))
