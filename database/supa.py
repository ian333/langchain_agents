from supabase import create_client
from decouple import config
# Proyecto Admin

url_admin: str = config("SUPABASE_ADMIN_URL")
key_admin: str = config("SUPABASE_ADMIN_KEY")

supabase_admin = create_client(supabase_url=url_admin,supabase_key= key_admin)

# Proyecto Usuario
url_user: str = config("SUPABASE_USER_URL")
key_user: str = config("SUPABASE_USER_KEY")
supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)

