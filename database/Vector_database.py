import os
import re
from decouple import config
from supabase import create_client
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

bucket_name = "CoursesFiles"

class PDFQA:
    def __init__(self, courseid, orgid=None):
        self.orgid = orgid
        self.courseid = courseid
        self.dataset_path = f"./skillstech/PDF-{self.courseid}"
        self.vectorstore_initialized = False
        self.supabase_admin = None
        self.companyid = None
        self.initialize_supabase()

    def initialize_supabase(self):
        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        print(f"Connecting to Supabase with URL: {url_admin} and Key: {key_admin[:5]}...")
        self.supabase_admin = create_client(supabase_url=url_admin, supabase_key=key_admin)
        print(f"Fetching data for course ID: {self.courseid}")
        data_course = self.supabase_admin.table("courses_tb").select("*").eq("id", self.courseid).execute().data
        print(f"Data fetched for course ID {self.courseid}: {data_course}")
        self.companyid = data_course[0]['companyid']

    def initialize_vectorstore(self):
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.vectorstore_initialized = True
            print(f"Vector store initialized for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    def query(self, query_text):
        if not self.vectorstore_initialized:
            self.initialize_vectorstore()
        result = self.qa(query_text)
        sources = []
        i = 1
        print(f"Query result for course ID {self.courseid}: {result}")

        for results in result.get("source_documents", []):
            source = results.metadata.get('source')
            nombre_libro_regex = re.search(r'/([^/]*)$', source).group(1) if re.search(r'/([^/]*)$', source) else "Nombre no disponible"
            page = int(results.metadata.get('page', 0))
            url = self.supabase_admin.storage.from_(bucket_name).get_public_url(f'{self.orgid}/{self.courseid}/{nombre_libro_regex}')
            sources.append({
                "url": f"{url}#page={page + 1}",
                "title": results.page_content[:100],  # Primeros 100 caracteres como título
                "sourceNumber": i
            })
            i += 1

        data = {"sources": sources}
        print(f"Sources data to be updated in Supabase for course ID {self.courseid}: {data}")
        try:
            url_user = config("SUPABASE_USER_URL")
            key_user = config("SUPABASE_USER_KEY")
            supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)
            supabase_user.table("responses_tb").update({"sources": data}).eq("id", self.courseid).execute()
            print(f"Supabase updated with sources for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")
        
        return result if sources else {"error": "No se encontraron documentos."}


class VideoQA:
    def __init__(self, courseid):
        self.courseid = courseid
        self.dataset_path = f"./skillstech/VIDEO-{self.courseid}"
        self.vectorstore_initialized = False
        self.initialize_vectorstore()

    def initialize_vectorstore(self):
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.vectorstore_initialized = True
            print(f"Vector store initialized for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    def query(self, query_text):
        if not self.vectorstore_initialized:
            self.initialize_vectorstore()
        result = self.qa(query_text)
        videos = []
        print(f"Query result for course ID {self.courseid}: {result}")

        for document in result.get("source_documents", []):
            video_id_match = re.search(r"v=([a-zA-Z0-9_-]+)", document.metadata.get('source', ''))
            url = document.metadata.get('source', '')
            if video_id_match:
                video_id = video_id_match.group(1)
                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                start = int(document.metadata.get('start', ''))
                videos.append({
                    "url": url + f"&t={start}ms",
                    "title": document.metadata.get("title", "Sin título"),
                    "thumbnailUrl": thumbnail_url,
                    "time": (start / 1000),
                    "fragment_text": document.page_content
                })

        data = {"videos": videos}
        print(f"Videos data to be updated in Supabase for course ID {self.courseid}: {data}")
        try:
            url_user = config("SUPABASE_USER_URL")
            key_user = config("SUPABASE_USER_KEY")
            supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)
            supabase_user.table("responses_tb").update({"videos": data}).eq("id", self.courseid).execute()
            print(f"Supabase updated with videos for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")

        return result if videos else {"error": "No se encontraron documentos."}


class VectorDatabaseManager:
    def __init__(self):
        self.instances = {}
        self.initialize_all_instances()

    def initialize_all_instances(self):
        path = "./skillstech"
        datasets = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        print(f"Datasets found: {datasets}")
        for dataset in datasets:
            print(f"Processing dataset: {dataset}")
            match = re.match(r'^(PDF|VIDEO)-(.+)$', dataset)
            if not match:
                print(f"Skipping invalid dataset name: {dataset}")
                continue
            prefix, courseid = match.groups()
            print(f"Extracted courseid: {courseid}")
            if prefix == "PDF":
                self.instances[courseid] = PDFQA(courseid)
            elif prefix == "VIDEO":
                self.instances[courseid] = VideoQA(courseid)

        print(f"Initialized instances: {self.instances}")

    def query_instance(self, courseid, query_text):
        if courseid in self.instances:
            return self.instances[courseid].query(query_text)
        else:
            return {"error": "No se encontró la instancia para el courseid proporcionado."}

# # Ejemplo de uso:
# vector_db_manager = VectorDatabaseManager()
# result = vector_db_manager.query_instance(courseid="0a8b1e63-c1ac-4faf-8ce8-2e8934ebf275", query_text="What is the main topic?")
# print(result)

# Ejemplo de uso: