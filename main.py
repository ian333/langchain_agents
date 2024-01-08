from fastapi import FastAPI
from datetime import datetime

# Importar funciones de utilidades
from utils.db_utils import save_reminder
from utils.email_utils import email_template_user

from decouple import config

# Configuración de FastAPI
app = FastAPI()

@app.post("/create-reminder/")
async def create_reminder(reminder_data: dict):
    """
    Crear un recordatorio y programar el envío del correo.
    """
    # Guardar recordatorio en la base de datos
    saved_reminder = save_reminder(reminder_data)

    # Programar tarea de Celery para enviar recordatorio
    send_reminder.apply_async((saved_reminder["id"],), eta=saved_reminder["time_to_send"])
    return {"message": "Recordatorio creado y programado correctamente"}





