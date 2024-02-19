import os
import re
from decouple import config
from supabase import create_client
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

# Inicialización de clientes Supabase
url_user = config("SUPABASE_USER_URL")
key_user = config("SUPABASE_USER_KEY")
supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)

url_admin = config("SUPABASE_ADMIN_URL")
key_admin = config("SUPABASE_ADMIN_KEY")
supabase_admin = create_client(supabase_url=url_admin, supabase_key=key_admin)

bucket_name = "CoursesFiles"

class VideosQA:
    def __init__(self, courseid, id):
        self.courseid = courseid
        self.id = id
        try:
            # Intenta configurar DeepLake y la cadena de QA
            dataset_path = f"hub://skillstech/VIDEO-{self.courseid}"
            vectorstore = DeepLake(dataset_path=dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.initialized = True
        except Exception as e:
            print(f"Error al inicializar VideosQA: {e}")
            self.initialized = False
    
    def query(self, query_text):
        if not self.initialized:
            return {"error": "VideosQA no inicializado correctamente."}

        result = self.qa(query_text)
        videos = []

        for document in result.get("source_documents", []):
            video_id_match = re.search(r"v=([a-zA-Z0-9_-]+)", document.metadata.get('source', ''))
            if video_id_match:
                video_id = video_id_match.group(1)
                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                videos.append({
                    "url": document.metadata.get('source', ''),
                    "title": document.metadata.get("title", "Sin título"),
                    "thumbnailUrl": thumbnail_url
                })

        data = videos

        try:
            supabase_user.table("responses_tb").update({"videos": data}).eq("id", self.id).execute()
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")

        return result if videos else {"error": "No se encontraron documentos."}
