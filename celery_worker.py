from celery import Celery
from utils.email_utils import send_email,send_html_email
from utils.email_utils import Learning_process

from celery.schedules import crontab


from supabase import create_client
from decouple import config
import datetime


# supabase = create_client(config("SUPABASE_URL"), config("SUPABASE_KEY"))


# Configurar Celery con el broker Redis
app = Celery('tasks', broker="redis://localhost:6379/0")


app.conf.beat_schedule = {
    # 'send-reminders-every-morning': {
    #     'task': 'celery_worker.send_learning_progress_checkin',
    #     'schedule': crontab(minute='*/2')
    # },    
    # 'check-new-users-every-two-minutes': {
    #     'task': 'celery_worker.check_and_register_new_users',
    #     'schedule': crontab(minute='*/2')  # Cada 2 minutos para pruebas
    # },
    #     'manage-learning-progress-checkin': {
    #     'task': 'celery_worker.manage_learning_progress_checkin',
    #     'schedule': crontab(minute='*/2')  # Cada 2 minutos para pruebas
    # },
        
        'process_courses': {
        'task': 'process_all_courses',
        'schedule': crontab(minute='*/10')  # Cada 2 minutos para pruebas
    }
}


import pytz  # Asegúrate de tener instalado pytz
current_date = datetime.datetime.now(datetime.timezone.utc)


from celery_functions.PDF_dl_processer import CourseProcessor
from celery_functions.VIDEO_dl_processer import CourseVideoProcessor

@app.task
def process_all_courses():
    processor = CourseProcessor()
    processor.process_courses()
    processor = CourseVideoProcessor()
    processor.process_all_courses()


@app.task
def send_reminder_email():

    send_email(to="sebastian@skills.tech",subject="test",content="Template corre de testing")
    # Esta función se encargará de enviar el correo electrónico
    # Asumiendo que 'reminder_id' es el ID del recordatorio en la base de datos
    print("Se envio el correo")
    return "Se envio el correo"


@app.task
def send_learning_progress_checkin():
    recordatorios = supabase.table("reminders_tb").select("*").eq("reminder_type", "Learning Progress Check-In").eq("status", "pending").execute().data

    for recordatorio in recordatorios:
        print(recordatorio)
        send_email(recordatorio["user_email"], "Learning Progress Check-In", Learning_process)

        # Actualizar el estado del recordatorio en la base de datos
        supabase.table("reminders_tb").update({"status": "sent"}).eq("id", recordatorio["id"]).execute()
        print("Se mando email a ")
    

@app.task
def check_and_register_new_users():
    # Obtener todos los usuarios de members_tb
    members = supabase.table("members_tb").select("*").execute().data
    for member in members:
        user_email = member["email"]
        user_name = member["name"]  # Obtener el nombre del usuario


        # Verificar si el usuario ya tiene un recordatorio en reminders_tb
        existing_reminder = supabase.table("reminders_tb").select("*").eq("user_email", user_email).eq("reminder_type", "Welcome").execute().data

        if not existing_reminder:
            # Enviar correo de bienvenida
            with open("email_templates/Learning_check_in.html", "r") as file:
                html_content = file.read()

                html_content = html_content.replace("[Nombre del Usuario]", user_name)
                send_html_email("sebastian@skills.tech", "Bienvenido a SkillsAI", html_content)

            # Crear un registro de recordatorio para el nuevo usuario
            new_reminder = {
                "user_email": user_email,
                "user_name":user_name,
                "reminder_type": "Welcome",
                "status": "sent",
                "scheduled_date": None,  # No aplica para correos de bienvenida
                "content": "Bienvenido a nuestra plataforma.",
                "sent_date": current_date.isoformat()
            }
            supabase.table("reminders_tb").insert(new_reminder).execute()

            print(f"Correo de bienvenida enviado a {user_email} y recordatorio creado.")






@app.task
def manage_learning_progress_checkin():
    current_date = datetime.datetime.now(datetime.timezone.utc)

    users = supabase.table("members_tb").select("*").execute().data

    for user in users:
        user_email = user["email"]
        user_name = user["name"]
        # Buscar el recordatorio de bienvenida
        welcome_reminder = supabase.table("reminders_tb").select("*").eq("user_email", user_email).eq("reminder_type", "Welcome").execute().data

        if welcome_reminder:
            welcome_date = welcome_reminder[0]["sent_date"]
            if welcome_date:
                welcome_date = datetime.datetime.fromisoformat(welcome_date)
                if not welcome_date.tzinfo:
                    welcome_date = pytz.utc.localize(welcome_date)

                scheduled_date = welcome_date + datetime.timedelta(days=7)

                # Buscar el recordatorio "Learning Progress Check-In"
                progress_checkin = supabase.table("reminders_tb").select("*").eq("user_email", user_email).eq("reminder_type", "Learning Progress Check-In").execute().data
                print(progress_checkin,current_date >= scheduled_date)
                if not progress_checkin:
                    # Crear un registro para el nuevo recordatorio programado
                    new_recordatorio = {
                        "user_email": user_email,
                        "user_name":user_name,
                        "reminder_type": "Learning Progress Check-In",
                        "status": "pending",
                        "scheduled_date": scheduled_date.isoformat(),
                        "content": "Learning Progress Check-In",
                        "sent_date": None
                    }
                    supabase.table("reminders_tb").insert(new_recordatorio).execute()
                    print(f"Se programó email 'Learning Progress Check-In' para {user_email}")

                elif progress_checkin[0]["status"] == "pending" and current_date >= scheduled_date:
                    # Enviar correo "Learning Progress Check-In"
                    with open("email_templates/Learning_check_in.html", "r") as file:
                        html_content = file.read()

                        html_content = html_content.replace("[Nombre del Usuario]", user_name)
                        send_html_email(user_email, "Learning Progress Check-In", html_content)
                    # Actualizar el estado del recordatorio
                    supabase.table("reminders_tb").update({"status": "sent", "sent_date": current_date.isoformat()}).eq("id", progress_checkin[0]["id"]).execute()
                    print(f"Se mando email 'Learning Progress Check-In' a {user_email}")

