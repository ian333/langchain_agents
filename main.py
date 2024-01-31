# main.py

# Importaciones de librerías estándar
from datetime import datetime
from typing import Optional

# Importaciones de FastAPI
from fastapi import FastAPI, HTTPException, Request, Body

# Importaciones de Langchain y herramientas relacionadas
from langchain_community.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatOpenAI

# Importaciones de utilidades y modelos propios
from utils.db_utils import save_reminder
from utils.email_utils import email_template_user
from models.chat_models import ChatRequest
from examples.chat_examples import chat_examples
from multi_agents.agent_executor import run_agent
from multi_agents.agent_utils import process_course_info  
from starlette.middleware.cors import CORSMiddleware


# Importaciones de configuración y utilidades adicionales
from decouple import config
import uuid
from supabase import create_client
from decouple import config
# Proyecto Admin
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


@app.post("/chat")
async def chat_endpoint(request_body: ChatRequest):
    """
    Endpoint para procesar solicitudes de chat, interactuar con un agente y guardar la información en la base de datos.

    Args:
    - request_body (ChatRequest): Datos de la solicitud de chat.

    Returns:
    - dict: Respuesta del agente y otros detalles relevantes.
    """
    # Desempaquetar los datos recibidos
    text = request_body.text
    courseid = request_body.courseid
    memberid = request_body.memberid
    prompt = request_body.prompt
    threadid = request_body.threadid  # Asume que ya viene generado si es necesario
    followup = request_body.followup
    email = request_body.email

    if not text:
        raise HTTPException(status_code=400, detail="Texto no proporcionado")

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
        "text": text,
        "followup": followup,
        "email": email,
        "timestamp": datetime.now().isoformat()
    }
    print(user_data)

    result = run_agent(query=text,courseid=courseid,member_id=memberid,custom_prompt=processed_info,prompt=prompt,thread_id=threadid,videos=reference_videos)
    # Insertar o actualizar en Supabase Usuario
    # response = supabase_user.table("user_table_name").insert(user_data).execute()

    # Devolver la respuesta
    return {"thread_id": threadid}
