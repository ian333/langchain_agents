# main.py
from uuid import uuid4
from datetime import datetime
import time
import asyncio

from fastapi import FastAPI, HTTPException, Request, Security, BackgroundTasks, Header, status
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

from utils.db_utils import save_reminder
from models.chat_models import ChatRequest, QueryRequest
from examples.chat_examples import chat_examples
from multi_agents.agent_executor import run_agent
from multi_agents.agent_utils import process_course_info
from starlette.middleware.cors import CORSMiddleware

from decouple import config
from supabase import create_client,Client

from langchain.globals import set_debug
set_debug(False)

from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA
from multi_agents.web_search import WebSearch
from multi_agents.follow_up import run_follow
from database.supa import supabase_user
import os

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

url_admin = config("SUPABASE_ADMIN_URL")
key_admin = config("SUPABASE_ADMIN_KEY")

supabase_admin :Client= create_client(supabase_url=url_admin, supabase_key=key_admin)


# Proyecto Usuario
url_user: str = config("SUPABASE_USER_URL")
key_user: str = config("SUPABASE_USER_KEY")
supabase_user:Client= create_client(supabase_url=url_user,supabase_key= key_user)


from Config.config import set_language, get_language

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADER_NAME = "X-API-KEY"
api_key_header = Header(HEADER_NAME)

async def validate_api_key(api_key_header: str = Security(api_key_header)):
    API_KEY = config("API_KEY")
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key_header

@app.post("/chat", status_code=status.HTTP_200_OK)
async def chat_endpoint(request_body: ChatRequest, background_tasks: BackgroundTasks, api_key: str = validate_api_key):
    print(f"\033[96m-----esto es request:{request_body} -------------------\033[0m")

    start_time = time.time()

    courseid = request_body.courseid
    memberid = request_body.memberid
    prompt = request_body.prompt
    threadid = request_body.threadid
    followup = request_body.followup
    email = request_body.email
    orgid = request_body.organizationid
    web = request_body.web

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

    start_time = time.time()
    video=""
    source=""
    follow_up_questions=""
    if web == False:
        print("\033[96mHello 😒😒😒😒😒😒😒😒😒😒😒\033[0m")
        videos = VideosQA(courseid=courseid, thread_id=threadid)
        sources = SourcesQA(courseid=courseid, orgid=orgid)
        follow_task = run_follow(query=prompt, history=followup)
        
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

    # Guardar el tiempo de respuesta en la base de datos
    try:
        supabase_user.table("responses_tb").update({"response_sec": response_time}).eq("id", id).execute()
    except Exception as e:
        print(f"\033[91mError al actualizar la base de datos con el tiempo de respuesta: {e}\033[0m")

    return {"thread_id": threadid}

@app.post("/create-thread", status_code=status.HTTP_200_OK)
async def create_thread(request_body: ChatRequest, background_tasks: BackgroundTasks, api_key: str = validate_api_key):
    """
    Endpoint para crear un nuevo thread y luego llamar al chat_endpoint para continuar con el proceso de chat.

    Args:
    - request_body (ChatRequest): Datos de la solicitud de chat.

    Returns:
    - dict: Respuesta del agente y otros detalles relevantes.
    """

    # Crear un nuevo thread ID
    new_thread_id = str(uuid4())
        # Actualizar el request_body con el nuevo thread ID
    request_body.threadid = new_thread_id

    # Guardar el nuevo thread en la base de datos
    thread_data = {
        "id": new_thread_id,
        "threadname": request_body.prompt,
        "memberid": request_body.memberid,
        "courseid": request_body.courseid,
        "created_at": datetime.now().isoformat(),
        "organizationid": request_body.organizationid,
        "first_response": None
    }
    thread_supa=supabase_user.table("threads_tb").insert(thread_data).execute()



    # Llamar al chat_endpoint para continuar el proceso de chat
    print(f"\033[96m-----esto es request:{request_body} -------------------\033[0m")
    background_tasks.add_task(chat_endpoint, request_body, background_tasks, api_key)

    return {"thread_id": new_thread_id}

from database.Vector_database import VectorDatabaseManager
print("Se estan inicializando las VectorDatabase")
vector_db_manager = VectorDatabaseManager()
print("Se estan inicializando las VectorDatabase")

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
