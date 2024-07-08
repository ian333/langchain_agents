import os
import re
from decouple import config
from supabase import create_client, Client
import requests
import httpx

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

bucket_name = "CoursesFiles"

class SourcesQA:
    def __init__(self, courseid, id=None, orgid=None):
        self.orgid = orgid
        self.courseid = courseid
        self.id = id
        self.dataset_path = f"./skillstech/PDF-{self.courseid}"
        self.vectorstore_initialized = False

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")

        self.supabase_admin = create_client(supabase_url=url_admin, supabase_key=key_admin)
        data_course = self.supabase_admin.table("courses_tb").select("*").eq("id", self.courseid).execute().data
        self.companyid = data_course[0]['companyid']

    async def query(self, query_text):
        try:
            # Realizar la solicitud al nuevo servidor de bases de datos vectorizadas
            api_url = "https://34.46.119.67/query"
            api_url = "http://127.0.0.1:8000/query"

            payload = {
                "courseid": self.courseid,
                "query_text": query_text,
                "type": "PDF"  # O "VIDEO" según corresponda
            }
            print(f"Sending request to {api_url} with payload: {payload}")
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()
                result = response.json()
            print(f"Received response: {result}")
            
            sources = []
            for i, doc in enumerate(result, start=1):
                source = doc['metadata'].get('source')
                nombre_libro_regex = re.search(r'/([^/]*)$', source).group(1) if re.search(r'/([^/]*)$', source) else "Nombre no disponible"
                page = int(doc['metadata'].get('page', 0))
                url = self.supabase_admin.storage.from_(bucket_name).get_public_url(f'{self.orgid}/{self.courseid}/{nombre_libro_regex}')
                sources.append({
                    "url": f"{url}#page={page + 1}",
                    "title": doc['page_content'][:100],  # Primeros 100 caracteres como título
                    "sourceNumber": i
                })

            data = {"sources": sources}
            return data
        except Exception as e:
            print(f"Error during query: {e}")
            return {"error": "No se pudo conectar a la base de datos esta vacia"}
