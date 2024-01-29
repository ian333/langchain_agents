from supabase import create_client
from decouple import config
# Configuración de Supabase
url_supabase = config("SUPABASE_ADMIN_URL")
key_supabase = config("SUPABASE_ADMIN_KEY")
supabase = create_client(url_supabase, key_supabase)

def save_reminder(reminder_data):
    """
    Guarda un recordatorio en Supabase.
    """
    response = supabase.table('reminders').insert(reminder_data).execute()
    if response.error:
        raise Exception("Error al guardar el recordatorio")
    return response.data
