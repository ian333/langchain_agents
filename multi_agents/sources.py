import os
import re
from decouple import config
from supabase import create_client
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake
from langchain_fireworks import Fireworks

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")





bucket_name = "CoursesFiles"

class SourcesQA:

    def __init__(self, courseid, id,orgid=None):
        self.orgid=orgid
        self.courseid = courseid
        self.id = id
        self.dataset_path = f"hub://skillstech/PDF-{self.courseid}"
        self.vectorstore_initialized = False

        url_admin = config("SUPABASE_ADMIN_URL")
        key_admin = config("SUPABASE_ADMIN_KEY")
        print("------------------------------------------")
        print("SOURCES 😁")
        print(key_admin)
        self.supabase_admin = create_client(supabase_url=url_admin, supabase_key=key_admin)
        print(self.supabase_admin)
        data_course=self.supabase_admin.table("courses_tb").select("*").eq("id",self.courseid).execute().data

        self.companyid = data_course[0]['companyid']
        



    async def initialize_vectorstore(self):

        try:
            llm = Fireworks(
                    model="accounts/fireworks/models/mixtral-8x7b-instruct", # see models: https://fireworks.ai/models
                    temperature=0.6,
                    max_tokens=100,
                    top_p=1.0,
                    top_k=40,
                )
            vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,#ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.vectorstore_initialized = True
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    async def query(self, query_text):
        
        try:
            if self.vectorstore_initialized == False:
                await self.initialize_vectorstore()
                # print("Base de datos vacía o vectorstore no inicializado correctamente.")
                # return {"error": "Base de datos vacía o vectorstore no inicializado correctamente."}

            result = self.qa(query_text)
            sources = []
            i = 1
            print(result)




            for results in result.get("source_documents", []):
                source = results.metadata.get('source')
                nombre_libro_regex = re.search(r'/([^/]*)$', source).group(1) if re.search(r'/([^/]*)$', source) else "Nombre no disponible"
                print(nombre_libro_regex)
                page = int(results.metadata.get('page', 0))
                url = self.supabase_admin.storage.from_(bucket_name).get_public_url(f'{self.orgid}/{self.carpeta}/{nombre_libro_regex}')
                # url = public_url_response.get('publicURL', 'URL no disponible')
                sources.append({
                    "url": f"{url}#page={page + 1}",
                    "title": results.page_content[:100],  # Primeros 100 caracteres como título
                    "sourceNumber": i
                })
                i += 1

            data = {"sources": sources}
            print(data)
            try:
                        # Inicialización de clientes Supabase
                url_user = config("SUPABASE_USER_URL")
                key_user = config("SUPABASE_USER_KEY")
                self.supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)
                thread_exists = self.supabase_user.table("responses_tb").update({"sources": data}).eq("id", self.id).execute()
            except Exception as e:
                print(f"Error al actualizar la base de datos: {e}")
                pass
        

            return result if sources else {"error": "No se encontraron documentos."}
        except Exception as e:
            print(e)

            return "No se pudo conectar a la base de datos esta vacia"
