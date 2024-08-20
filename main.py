from fastapi import FastAPI, HTTPException, status, Form
# main.py
from uuid import uuid4
from datetime import datetime
import time
import asyncio
import random


from fastapi import FastAPI, HTTPException, Security, BackgroundTasks, Header, status
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler

from utils.db_utils import save_reminder
from models.chat_models import ChatRequest, QueryRequest
from examples.chat_examples import chat_examples
from multi_agents.agent_executor import run_agent
from multi_agents.agent_utils import process_course_info
from starlette.middleware.cors import CORSMiddleware

from decouple import config
from supabase import create_client, Client

from langchain.globals import set_debug
set_debug(False)

from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA
from multi_agents.web_search import WebSearch
from multi_agents.follow_up import run_follow
from multi_agents.articles_agent import ArticleRequest,make_article
from database.supa import supabase_user
import os

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

# Singleton pattern for Supabase clients
class SupabaseClient:
    _admin_client = None
    _user_client = None

    @staticmethod
    def get_admin_client():
        if SupabaseClient._admin_client is None:
            url_admin = config("SUPABASE_ADMIN_URL")
            key_admin = config("SUPABASE_ADMIN_KEY")
            print(f"Admin URL: {url_admin}")
            print(f"Admin Key: {key_admin[:5]}...")  # Print only the first few characters for security
            SupabaseClient._admin_client = create_client(supabase_url=url_admin, supabase_key=key_admin)
            # Test admin client
            SupabaseClient._admin_client.table("courses_tb").select("*").limit(1).execute()
            print("Admin client created successfully.")

        return SupabaseClient._admin_client

    @staticmethod
    def get_user_client():
        if SupabaseClient._user_client is None:
            url_user = config("SUPABASE_USER_URL")
            key_user = config("SUPABASE_USER_KEY")
            print(f"User URL: {url_user}")
            print(f"User Key: {key_user[:5]}...")  # Print only the first few characters for security
            SupabaseClient._user_client = create_client(supabase_url=url_user, supabase_key=key_user)
        # Test user client
            SupabaseClient._user_client.table("threads_tb").select("*").limit(1).execute()
            print("User client created successfully.")

        return SupabaseClient._user_client

supabase_admin = SupabaseClient.get_admin_client()
supabase_user = SupabaseClient.get_user_client()

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




def should_activate_ai_companion() -> bool:
    # Decide randomly whether to activate the AI Companion
    return random.random() < 0.25  # 25% probability

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
    first_response=False
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


    if not threadid:
        threadid = str(uuid4())
        first_response=True
        custom_ai="Da la Bienvenida al estudiante y responde un poco de su pregunta pero responde rapido y amable"
    else:
        first_response=False
        custom_ai=None
    try:
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
        video = ""
        source = ""
        follow_up_questions = ""
        if web == False :
            print("\033[96mHello 😒😒😒😒😒😒😒😒😒😒😒\033[0m")
            videos = VideosQA(courseid=courseid, thread_id=threadid)
            sources = SourcesQA(courseid=courseid, orgid=orgid)
            follow_task = run_follow(query=prompt, history=followup)
            
            video_task = videos.query(prompt)
            source_task = sources.query(prompt)
            video, source, follow_up_questions = await asyncio.gather(video_task, source_task, follow_task)
        if web == True:
            print("\033[96m------------------------\033[0m")
            print("\033[96mHEY ENTRAMOS A WEB\033[0m")
            websearch = WebSearch(courseid=courseid, id=threadid, orgid=orgid)
            source = await asyncio.create_task(websearch.query(prompt))

        id, agent_task = await run_agent(query=prompt, courseid=courseid, member_id=memberid, custom_prompt=processed_info, prompt=prompt, thread_id=threadid, history=followup, orgid=orgid, web=web, videos=video, sources=source, follow_up_questions=follow_up_questions,custom_ai=custom_ai)
        end_time = time.time()
        response_time = end_time - start_time

        # Guardar el tiempo de respuesta en la base de datos
        try:
            supabase_user.table("responses_tb").update({"response_sec": response_time}).eq("id", id).execute()
        except Exception as e:
            print(f"\033[91mError al actualizar la base de datos con el tiempo de respuesta: {e}\033[0m")


                # Activar AI Companion aleatoriamente en segundo plano
        if should_activate_ai_companion():
            background_tasks.add_task(run_ai_companion, request_body)

        return {"thread_id": threadid}

    except Exception as e:
        print(f"\033[91mUnexpected Error: {e}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


async def run_ai_companion(request_body: ChatRequest):
    print(f"\033[91Running AI Companion\033[0m")
    courseid = request_body.courseid
    memberid = request_body.memberid
    prompt = request_body.prompt
    threadid = request_body.threadid
    followup = request_body.followup
    email = request_body.email
    orgid = request_body.organizationid

    query = "AI COMPANION"
    custom_prompt="AI_companion"

    try:
        await run_agent(query=query, courseid=courseid, member_id=memberid, custom_prompt=custom_prompt, prompt=prompt, thread_id=threadid, history=followup, orgid=orgid,type="companion")
    except Exception as e:
        print(f"\033[91mError running AI Companion: {e}\033[0m")


@app.post("/create-thread", status_code=status.HTTP_200_OK)
async def create_thread(request_body: ChatRequest, background_tasks: BackgroundTasks, api_key: str = validate_api_key):
    new_thread_id = str(uuid4())
    request_body.threadid = new_thread_id

    thread_data = {
        "id": new_thread_id,
        "threadname": request_body.prompt,
        "memberid": request_body.memberid,
        "courseid": request_body.courseid,
        "created_at": datetime.now().isoformat(),
        "organizationid": request_body.organizationid,
        "first_response": None
    }
    try:
        supabase_user.table("threads_tb").insert(thread_data).execute()

    except Exception as e:
        print(f"\033[91mUnexpected Error: {e}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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





@app.post("/articles/new", status_code=status.HTTP_201_CREATED)
async def create_article(
    prompt: str = Form(...),
    courseid: str = Form(...),
    projectid: str = Form(...),
    memberid: str = Form(...),
    organizationid: str = Form(...)
):
    try:
        print(f"\033[94m[INFO] Recibiendo datos del formulario...\033[0m")
        print(f"\033[94mPrompt: {prompt}\033[0m")
        print(f"\033[94mCourse ID: {courseid}\033[0m")
        print(f"\033[94mProject ID: {projectid}\033[0m")
        print(f"\033[94mMember ID: {memberid}\033[0m")
        print(f"\033[94mOrganization ID: {organizationid}\033[0m")

        # Generar el contenido del artículo usando el prompt proporcionado
        content = await make_article(prompt)

        # Guardar el artículo en la base de datos utilizando Supabase
        result = supabase_user.table("articles_tb").insert({
            "prompt": prompt,
            "content": content,
            "courseid": courseid,
            "projectid": projectid,
            "memberid": memberid,
            "organizationid": organizationid,
        }).execute()

        if not result or "error" in result:
            raise HTTPException(status_code=500, detail="Error saving article to database")

        # Devolver el ID del artículo creado
        article_id = result.data[0]['id']
        print(f"\033[92m[INFO] Artículo guardado exitosamente en la base de datos con ID: {article_id}\033[0m")
        return {"id": article_id}

    except Exception as e:
        print(f"\033[91m[ERROR] Error creating article: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")