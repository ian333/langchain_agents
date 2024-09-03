from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status, Form
# main.py
from uuid import uuid4
from datetime import datetime
import time
import asyncio
import random

import uuid
import asyncio
import time
from fastapi import FastAPI, HTTPException, status, Form, BackgroundTasks
from datetime import datetime, timezone
from uuid import uuid4
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
from multi_agents.path_agent import generate_path_details,generate_path_topics,save_to_supabase,save_subtopics_to_db,generate_subtopics_for_topic,create_article_for_topic
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


from database.Vector_database import VectorDatabaseManager
async def initialize_supabase_clients():
    global supabase_admin, supabase_user
    supabase_admin = SupabaseClient.get_admin_client()
    supabase_user = SupabaseClient.get_user_client()

# Inicialización de VectorDatabase en segundo plano
async def initialize_vector_database():
    global vector_db_manager
    print("Se están inicializando las VectorDatabase en segundo plano...")
    vector_db_manager = VectorDatabaseManager()
    print("VectorDatabase inicializadas exitosamente.")

# Función de arranque para inicializar componentes al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    print("Iniciando la aplicación...")
    background_tasks = BackgroundTasks()
    background_tasks.add_task(initialize_supabase_clients)
    background_tasks.add_task(initialize_vector_database)
    print("Tareas de inicialización añadidas a BackgroundTasks.")
    await background_tasks()



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
 
 
#  TODO : @ian333 QUITAR ESTA FUNCION DE CUSTOM AI



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

        # # Guardar el tiempo de respuesta en la base de datos
        # try:
        # #     supabase_user.table("responses_tb").update({"response_sec": response_time}).eq("id", id).execute()
        # except Exception as e:
        #     print(f"\033[91mError al actualizar la base de datos con el tiempo de respuesta: {e}\033[0m")


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


@app.post("/path/new")
async def get_path(
    background_tasks: BackgroundTasks,
    prompt: str = Form(..., example="Aprender Python desde cero"),
    courseid: str = Form(..., example="661659eb-3afa-4c8e-8c4e-25a9115eed69"),
    memberid: str = Form(..., example="8b013804-faa6-426e-bfcc-43227f58e3c8"),
    projectid: str = Form(..., example="28722c50-cc1b-4b92-811b-0709320063e5"),
    orgid: str = Form(..., example="6c0bfedb-258a-4c77-9bad-b0e87c0d9c98"),
    isDefault: bool = Form(..., example=True)
):
    
    start_time = time.time()  # Capturar el tiempo de inicio
    pathid = str(uuid4())
    try:
        print(f"\033[94m[INFO] Recibiendo datos del formulario...\033[0m")
        name, description = await generate_path_details(prompt, pathid)
        
        # Guardar pathid en Supabase
        await save_to_supabase("paths_tb", {
            "id": pathid,
            "base_prompt": prompt,
            "name": name,
            "courseid": courseid,
            "description": description,
            "memberid": memberid,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "isDefault": isDefault,
            "icon": "😍",
            "level": 1,
            "orgid": orgid,
        })

        # Generar topics
        topics = await generate_path_topics(path_name=name, max_items=5, language="en")
        
        # Iniciar las tareas en segundo plano
        background_tasks.add_task(process_remaining_tasks, topics, pathid, name, courseid, projectid, memberid, orgid)
        
        duration = time.time() - start_time  # Calcular la duración
        print(f"\033[92m[INFO] Path creado exitosamente en {duration:.2f} segundos.\033[0m")

        # Retornar el pathid, topics, y duración
        return {"id": pathid, "topics": topics, "duration": f"{duration:.2f} segundos"}

    except Exception as e:
        print(f"\033[91m[ERROR] Error creando el Path: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Función que procesa las tareas restantes en segundo plano
async def process_remaining_tasks(topics, pathid, name, courseid, projectid, memberid, orgid):
    try:
        # Crear tareas para paralelizar la creación de artículos y subtopics
        tasks = []
        for order, topic in enumerate(topics, start=1):
            topicid = str(uuid.uuid4())  # Generar un nuevo ID para el topic
            await save_to_supabase("paths_topics_tb", {
                "id": topicid,
                "pathid": pathid,
                "name": topic,
                "order": order,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            
            # Crear tareas para la generación de artículos y subtopics
            task = asyncio.create_task(create_article_and_subtopics_for_topic(
                topic_name=topic,
                pathid=pathid,
                topicid=topicid,
                courseid=courseid,
                projectid=projectid,
                memberid=memberid,
                orgid=orgid,
                path_name=name
            ))
            tasks.append(task)

        # Ejecutar todas las tareas en paralelo
        await asyncio.gather(*tasks)

    except Exception as e:
        print(f"\033[91m[ERROR] Error procesando las tareas en segundo plano: {str(e)}\033[0m")


# Función para manejar la creación de artículos y subtopics en paralelo
async def create_article_and_subtopics_for_topic(topic_name: str, pathid: str, topicid: str, courseid: str, projectid: str, memberid: str, orgid: str, path_name: str):
    try:
        # Crear la tarea para crear el artículo, sin await aquí
        article_task = create_article_for_topic(topic_name=topic_name, pathid=pathid, courseid=courseid, projectid=projectid, memberid=memberid, orgid=orgid)

        subtopics_task = asyncio.create_task(generate_subtopics_for_topic(topic_name, path_name))
        subtopics = (await asyncio.gather(subtopics_task))  # Desempaquetar la lista

        # Crear tareas para guardar subtopics en paralelo
        subtopic_tasks = [save_subtopics_to_db(pathid, topicid, subtopic, path_name=path_name, topic_name=topic_name) for subtopic in subtopics]

        # Ejecutar la creación del artículo y los subtopics en paralelo
        await asyncio.gather(article_task, *subtopic_tasks)

    except Exception as e:
        print(f"\033[91m[ERROR] Error en create_article_and_subtopics_for_topic: {str(e)}\033[0m")
        raise










from multi_agents.exam_agent import generate_exam, evaluate_answer,ExamRequest,ExamGenerateRequest

# Endpoint para generar un examen
from fastapi import FastAPI, HTTPException, status, Form,Depends
from database.supa import supabase_user
from uuid import uuid4
from datetime import datetime

#
@app.post("/exam/generate")
async def generate_exam_endpoint(exam_request: ExamGenerateRequest):
    try:
        # Extraer datos del modelo
        prompt = exam_request.prompt
        max_items = exam_request.max_items
        memberid = exam_request.memberid
        # Generar preguntas
        questions = generate_exam(prompt, max_items)
        
        # Generar un UUID único para el examen
        exam_id = str(uuid4())
        
        # Preparar los datos para insertar en la tabla `exams_tb`
        exam_data = {
            "id": exam_id,  # ID único del examen
            "type": "diagnostic",  # Puedes cambiar a 'final' si es necesario
            "memberid": memberid,  # Asigna el ID del miembro, debe ser dinámico
            "questions": questions,  # Las preguntas generadas en formato JSONB
            "created_at": datetime.utcnow().isoformat(),  # Marca de tiempo actual
            "status": "ready",  # Estado inicial del examen
            "finished_at": None,  # Inicialmente, no ha sido terminado
            "time_elapsed": None,  # Inicialmente, no hay tiempo transcurrido
            "feedback": None,  # Sin feedback inicialmente
            "score": None,  # Sin score inicialmente
            "courseid":exam_request.course        }

        # Insertar los datos en la tabla `exams_tb`
        response = supabase_user.table("exams_tb").insert(exam_data).execute()
        print(response)

        # Guardar cada pregunta en la tabla `exam_questions_tb`
        for idx, question in enumerate(questions, start=1):
            question_data = {
                "id": str(uuid4()),  # Generar un UUID único para cada pregunta
                "question": question,  # La pregunta generada
                "order": idx,  # El orden de la pregunta en el examen
                "examid": exam_id,  # El ID del examen generado anteriormente
                "courseid":exam_request.courseid,
            }

            # Insertar cada pregunta en la tabla `exam_questions_tb`
            question_response = supabase_user.table("exams_questions_tb").insert(question_data).execute()
            print(question_response)

        print(f"\033[92m[INFO] Examen y preguntas generados y guardados en la base de datos.\033[0m")
        return {"examid": exam_id}

    except Exception as e:
        print(f"\033[91m[ERROR] Error generating exam: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")
from uuid import uuid4
from datetime import datetime

from datetime import datetime, timezone
from uuid import uuid4

# Endpoint para recibir y evaluar un examen completo
@app.post("/exam/evaluate")
async def receive_exam(exam: ExamRequest):
    try:
        evaluations = []
        
        # Obtener los detalles del examen de la tabla `exams_tb`
        exam_details = supabase_user.table("exams_tb").select("*").eq("id", exam.exam_id).single().execute()

        if not exam_details.data:
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        # Obtener el timestamp de cuando se creó el examen
        created_at_str = exam_details.data["created_at"]
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

        # Calcular el tiempo actual y el tiempo transcurrido
        finished_at = datetime.now(timezone.utc)
        time_elapsed = finished_at - created_at

        for idx, answer in enumerate(exam.answers, start=1):
            # Evaluar cada respuesta
            evaluation = evaluate_answer(answer.question, answer.answer)
            evaluations.append(evaluation)

            # Preparar los datos para insertar en la tabla `exams_answers_tb`
            answer_data = {
                "id": str(uuid4()),  # Generar un UUID único para la respuesta
                "answer": answer.answer,
                "questionid": answer.question_id,  # Usar el `question_id` proporcionado en el modelo
                "examid": exam.exam_id,  # ID del examen al que pertenece
                "score": evaluation["score"],  # Calificación obtenida
                "feedback": evaluation["feedback"],  # Feedback obtenido
                "created_at": datetime.utcnow().isoformat()  # Marca de tiempo actual
            }


            # Insertar los datos en la tabla `exams_answers_tb`
            response = supabase_user.table("exams_answers_tb").insert(answer_data).execute()
            print(f"\033[94m[INFO] Respuesta insertada con ID: {response.data[0]['id']}\033[0m")

            # Actualizar el estado a "completed"
            update = supabase_user.table("exams_tb").update({"status": "completed"}).eq("id", response.data[0]["id"]).execute()

        # Actualizar la tabla `exams_tb` con `finished_at`, `time_elapsed`, y `status` a `done`
        exam_update_data = {
            "status": "done",
            "finished_at": finished_at.isoformat(),
            "time_elapsed": str(time_elapsed)  # Guardar el tiempo transcurrido en formato 'HH:MM:SS'
        }

        # Actualizar el examen en la tabla `exams_tb`
        supabase_user.table("exams_tb").update(exam_update_data).eq("id", exam.exam_id).execute()

        print(f"\033[92m[INFO] Examen actualizado con `finished_at`, `time_elapsed`, y `status` a 'done'.\033[0m")
        return {"status": "success", "evaluations": evaluations}

    except Exception as e:
        print(f"\033[91m[ERROR] Error evaluating exam: {str(e)}\033[0m")
        raise HTTPException(status_code=500, detail="Internal Server Error")
