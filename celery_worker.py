from celery import Celery
from utils.email_utils import send_email
from utils.email_utils import Learning_process

from celery.schedules import crontab


from supabase import create_client
from decouple import config

supabase = create_client(config("SUPABASE_URL"), config("SUPABASE_KEY"))


# Configurar Celery con el broker Redis
celery = Celery('reminder_app', broker="redis://localhost:6379/0")

# celery.conf.beat_schedule = {
#     'send-reminders-every-morning': {
#         'task': 'celery_worker.send_reminder_email',
#         'schedule': crontab(minute='*/2')
#     },
# }

celery.conf.beat_schedule = {
    'send-reminders-every-morning': {
        'task': 'celery_worker.send_learning_progress_checkin',
        'schedule': crontab(minute='*/2')
    },
}

@celery.task
def send_reminder_email():

    send_email(to="sebastian@skills.tech",subject="test",content="Template corre de testing")
    # Esta función se encargará de enviar el correo electrónico
    # Asumiendo que 'reminder_id' es el ID del recordatorio en la base de datos
    print("Se envio el correo")
    return "Se envio el correo"


@celery.task
def send_learning_progress_checkin():
    recordatorios = supabase.table("reminders_tb").select("*").eq("reminder_type", "Learning Progress Check-In").eq("status", "pending").execute().data

    for recordatorio in recordatorios:
        print(recordatorio)
        send_email(recordatorio["user_email"], "Learning Progress Check-In", Learning_process)

        # Actualizar el estado del recordatorio en la base de datos
        supabase.table("reminders_tb").update({"status": "sent"}).eq("id", recordatorio["id"]).execute()
        print("Se mando email a ")
    
