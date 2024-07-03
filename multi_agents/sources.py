import os
import re
from decouple import config
from supabase import create_client,Client
import requests

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

bucket_name = "CoursesFiles"

import httpx

class SourcesQA:
    def __init__(self, courseid, id, orgid=None):
        self.orgid = orgid
        self.courseid = courseid
        self.id = id
        self.dataset_path = f"hub://skillstech/PDF-{self.courseid}"
        self.vectorstore_initialized = False

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")

        self.supabase_admin = create_client(supabase_url=url_admin, supabase_key=key_admin)
        data_course = self.supabase_admin.table("courses_tb").select("*").eq("id", self.courseid).execute().data
        self.companyid = data_course[0]['companyid']

    async def query(self, query_text):
        try:
            # Realizar la solicitud al nuevo servidor de bases de datos vectorizadas
            api_url = "http://localhost:8000/query"  # Añadir http://
            payload = {
                "courseid": self.courseid,
                "query_text": query_text,
                "type": "PDF"  # O "VIDEO" según corresponda
            }
            print(f"Sending request to {api_url} with payload: {payload}")
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"Received response: {result}")
            
            sources = []
            for i, doc in enumerate(result.get("source_documents", []), start=1):
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
            print(f"Sources data to be updated in Supabase for course ID {self.courseid}: {data}")

            try:
                url_user = config("SUPABASE_USER_URL")
                key_user = config("SUPABASE_USER_KEY")
                self.supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)
                self.supabase_user.table("responses_tb").update({"sources": data}).eq("id", self.id).execute()
                print(f"Supabase updated with sources for course ID {self.courseid}")
            except Exception as e:
                print(f"Error al actualizar la base de datos: {e}")
            
            return result if sources else {"error": "No se encontraron documentos."}
        except Exception as e:
            print(f"Error during query: {e}")
            return {"error": "No se pudo conectar a la base de datos esta vacia"}
