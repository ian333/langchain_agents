import os
import re
from decouple import config
from supabase import create_client, Client
import requests

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

bucket_name = "CoursesFiles"
import httpx
from database.supa import supabase_admin,supabase_user

class VideosQA:
    def __init__(self, courseid, id=None, first_response=None, thread_id=None):
        self.courseid = courseid
        self.id = id
        self.first_response = first_response
        self.thread_id = thread_id

    async def query(self, query_text):
        try:
            # Realizar la solicitud al nuevo servidor de bases de datos vectorizadas
            api_url = "https://34.46.119.67/query"  # Añadir http://127.0.0.1:8000/
            api_url = "http://127.0.0.1:8000/query"  # Añadir http://127.0.0.1:8000/
            payload = {
                "courseid": self.courseid,
                "query_text": query_text,
                "type": "VIDEO"  # O "PDF" según corresponda
            }
            print(f"Sending request to {api_url} with payload: {payload}")
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()
                result = response.json()
            print(f"Received response: {result}")

            videos = []
            for i, doc in enumerate(result.get("source_documents", []), start=1):
                video_id_match = re.search(r"v=([a-zA-Z0-9_-]+)", doc['metadata'].get('source', ''))
                url = doc['metadata'].get('source', '')
                if video_id_match:
                    video_id = video_id_match.group(1)
                    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                    start = int(doc['metadata'].get('start', ''))
                    videos.append({
                        "url": url + f"&t={start}ms",
                        "title": doc['metadata'].get("title", "Sin título"),
                        "thumbnailUrl": thumbnail_url,
                        "time": (start / 1000),
                        "fragment_text": doc['page_content']
                    })

            data = {"videos": videos}
            return data
            print(f"Videos data to be updated in Supabase for course ID {self.courseid}: {data}")

            try:

                supabase_user.table("threads_tb").update({"thread_img": videos[0]}).eq("id", self.thread_id).execute()
                supabase_user.table("responses_tb").update({"videos": data}).eq("id", self.id).execute()
                print(f"Supabase updated with videos for course ID {self.courseid}")
            except Exception as e:
                print(f"Error al actualizar la base de datos: {e}")

            return result if videos else {"error": "No se encontraron documentos."}
        except Exception as e:
            print(f"Error during query: {e}")
            return {"error": "No se pudo conectar a la base de datos esta vacia"}
