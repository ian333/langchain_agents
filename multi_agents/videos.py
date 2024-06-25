import os
import re
from decouple import config
from supabase import create_client,Client
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake
from langchain_fireworks import Fireworks

# Configuración de variables de entorno
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")
from langchain_google_genai import ChatGoogleGenerativeAI
### Gemini
import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] =config("GOOGLE_API_KEY")



bucket_name = "CoursesFiles"

class VideosQA:
    def __init__(self, courseid, id,first_response,thread_id):
        self.courseid = courseid
        self.id = id
        self.first_response=first_response
        self.thread_id=thread_id

    
    async def query(self, query_text):
        try:
            # Intenta configurar DeepLake y la cadena de QA
            # llm = Fireworks(
            #         model="accounts/fireworks/models/mixtral-8x7b-instruct", # see models: https://fireworks.ai/models
            #         temperature=0.6,
            #         max_tokens=100,
            #         top_p=1.0,
            #         top_k=40,
            #     )
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            dataset_path = f"hub://skillstech/VIDEO-{self.courseid}"
            vectorstore = DeepLake(dataset_path=dataset_path, embedding=OpenAIEmbeddings(), read_only=True)
            self.qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,#ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                verbose=True,
            )
            self.initialized = True
        except Exception as e:
            print(f"Error al inicializar VideosQA: {e}")
            self.initialized = False
        try:
            if not self.initialized:
                return {"error": "VideosQA no inicializado correctamente."}

            result = self.qa(query_text)
            videos = []
            print(result)


            for document in result.get("source_documents"):
                print("Estos son los diocumentos",document)
                video_id_match = re.search(r"v=([a-zA-Z0-9_-]+)", document.metadata.get('source', ''))
                url=document.metadata.get('source', '')
                print("video_id_match",video_id_match)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                    print("esta es la url del thumbnail",thumbnail_url)
                    start=int(document.metadata.get('start',''))
                    videos.append({
                        "url": url+f"&t={start}ms",
                        "title": document.metadata.get("title", "Sin título"),
                        "thumbnailUrl": thumbnail_url,
                        "time":(start/1000),
                        "fragment_text":document.page_content

                    })
                    print("Esta es la lista de vidoes",videos)
            
            

            data = {"videos": videos}
            print("Este es data",data)

            try:
                
                # Inicialización de clientes Supabase
                url_user = config("SUPABASE_USER_URL")
                key_user = config("SUPABASE_USER_KEY")
                supabase_user:ClientEEE = create_client(supabase_url=url_user, supabase_key=key_user)
                supabase_user.table("threads_tb").update({"thread_img": videos[0]}).eq("id", self.thread_id).execute()
                supabase_user.table("responses_tb").update({"videos": data}).eq("id", self.id).execute()
            except Exception as e:
                print(f"Error al actualizar la base de datos: {e}")

            return result if videos else {"error": "No se encontraron documentos."}
        except Exception as e:
            print(e)
            return "No se pudo conectar a la base de datos esta vacia"

