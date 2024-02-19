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

class SourcesQA:
    def __init__(self, courseid, id):
        self.courseid = courseid
        self.id = id
        self.dataset_path = f"hub://skillstech/PDF-{self.courseid}"
        self.vectorstore_initialized = False
        self.initialize_vectorstore()

    def initialize_vectorstore(self):
        try:
            vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.vectorstore_initialized = True
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    def query(self, query_text):
        if not self.vectorstore_initialized:
            print("Base de datos vacía o vectorstore no inicializado correctamente.")
            return {"error": "Base de datos vacía o vectorstore no inicializado correctamente."}

        result = self.qa(query_text)
        sources = []
        i = 1
        carpeta = self.courseid

        for results in result.get("source_documents", []):
            source = results.metadata.get('source')
            nombre_libro_regex = re.search(r'/([^/]*)$', source).group(1) if re.search(r'/([^/]*)$', source) else "Nombre no disponible"
            page = int(results.metadata.get('page', 0))
            public_url_response = supabase_admin.storage.from_(bucket_name).get_public_url(f'{carpeta}/{nombre_libro_regex}')
            url = public_url_response.get('publicURL', 'URL no disponible')

            sources.append({
                "url": f"{url}#page={page + 1}",
                "title": results.page_content[:100],  # Primeros 100 caracteres como título
                "sourceNumber": i
            })
            i += 1

        data = {"sources": sources}
        try:
            thread_exists = supabase_user.table("responses_tb").update({"sources": data}).eq("id", self.id).execute()
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")
            pass

        return result if sources else {"error": "No se encontraron documentos."}
