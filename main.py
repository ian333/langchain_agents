# main.py
from uuid import uuid4  # Importa esta biblioteca en la parte superior de tu archivo

# Importaciones de librerías estándar
from datetime import datetime

# Importaciones de FastAPI
from fastapi import FastAPI, HTTPException, Request,Security

# Importaciones de Langchain y herramientas relacionadas
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from fastapi import status

# Importaciones de utilidades y modelos propios
from utils.db_utils import save_reminder
from models.chat_models import ChatRequest
from examples.chat_examples import chat_examples
from multi_agents.agent_executor import run_agent
from multi_agents.agent_utils import process_course_info  
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks


# Importaciones de configuración y utilidades adicionales
from decouple import config
from supabase import create_client
from decouple import config
# Proyecto Admin

import os
from multi_agents.videos import VideosQA
from multi_agents.sources import SourcesQA

from concurrent.futures import ThreadPoolExecutor

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

url_admin: str = config("SUPABASE_ADMIN_URL")
key_admin: str = config("SUPABASE_ADMIN_KEY")

supabase_admin = create_client(supabase_url=url_admin,supabase_key= key_admin)


# Configuración de la aplicación FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origins
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

@app.post("/create-reminder/")
async def create_reminder(reminder_data: dict):
    """
    Endpoint para crear un recordatorio y programar su envío por correo.
    
    Args:
    - reminder_data (dict): Datos del recordatorio.
    
    Returns:
    - dict: Mensaje de confirmación de creación y programación del recordatorio.
    """
    # Guardar recordatorio en la base de datos
    saved_reminder = save_reminder(reminder_data)

    # Aquí se podría programar una tarea de Celery para enviar el recordatorio (comentado actualmente)
    # send_reminder.apply_async((saved_reminder["id"],), eta=saved_reminder["time_to_send"])
    return {"message": "Recordatorio creado y programado correctamente"}





def validate_api_key(request: Request= None):
    HEADER_NAME = "X-API-KEY"

    API_KEY: str = config("API_KEY")
    api_key = request.headers.get(HEADER_NAME)
    print(API_KEY)
    print(api_key)
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


@app.post("/chat",status_code=status.HTTP_200_OK)
async def chat_endpoint(request_body: ChatRequest,background_tasks: BackgroundTasks,api_key: str = Security(validate_api_key)):
    """
    Endpoint para procesar solicitudes de chat, interactuar con un agente y guardar la información en la base de datos.

    Args:
    - request_body (ChatRequest): Datos de la solicitud de chat.

    Returns:
    - dict: Respuesta del agente y otros detalles relevantes.
    """
    # Desempaquetar los datos recibidos
    # text = request_body.text
    courseid = request_body.courseid
    memberid = request_body.memberid
    prompt = request_body.prompt
    threadid = request_body.threadid  # Asume que ya viene generado si es necesario
    followup = request_body.followup
    email = request_body.email
    orgid=request_body.organizationid
    processed_info={}
    reference_videos={}

    if not threadid:
        threadid = str(uuid4())

    # Obtener instrucciones de la empresa desde la tabla de admin
    response = supabase_admin.table("courses_tb").select("*").eq("id", courseid).execute()

    # Verificar si la respuesta tiene datos
    if response.data:
        admin_data = response.data[0]
    
        print(admin_data)
        processed_info,reference_videos = process_course_info(admin_data)
        print(processed_info)
    # Aquí se manejaría la lógica para interactuar con el agente (comentado actualmente)
    # ...

    # Guardar o actualizar la información en la tabla de usuario
    user_data = {
        "courseid": courseid,
        "memberid": memberid,
        "prompt": prompt,
        "threadid": threadid,
        "followup": followup,
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "orgid":orgid

    }
    print(user_data)

    agent,id=run_agent(query=prompt,courseid=courseid,member_id=memberid,custom_prompt=processed_info,prompt=prompt,thread_id=threadid,videos=reference_videos)
    # background_tasks.add_task(run_agent,query=prompt,courseid=courseid,member_id=memberid,custom_prompt=processed_info,prompt=prompt,thread_id=threadid,videos=reference_videos)
    
    
    with ThreadPoolExecutor() as executor:
        videos = VideosQA(courseid=courseid, id=id)
        sources = SourcesQA(courseid=courseid, id=id)
        
        # Envía las tareas en segundo plano y continúa sin esperar a que finalicen
        executor.submit(videos.query, prompt)
        executor.submit(sources.query, prompt)

    # sources.query(query_text=prompt)
    # background_tasks.add_task(sources.query,query_text=prompt)

    # Insertar o actualizar en Supabase Usuario

    # Devolver la respuesta
    return {"thread_id": threadid}


