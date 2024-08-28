import os
import re
import time
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

    def initialize_vectorstore(self):
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            self.vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)

            self.vectorstore_initialized = True
            print(f"Vector store initialized for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    async def query(self, query_text):
        if not self.vectorstore_initialized:
            self.initialize_vectorstore()
        start_time = time.time()
        result = self.vectorstore.similarity_search(query_text)
        end_time = time.time()
        response_time = end_time - start_time
        print(f"PDFQA Query Time: {response_time:.4f} seconds")
        # print("Esto es vector DATABASE imprime de pdfqa", result)

        return result 


class VideoQA:
    def __init__(self, courseid):
        self.courseid = courseid
        self.dataset_path = f"./skillstech/VIDEO-{self.courseid}"
        self.vectorstore_initialized = False
        self.initialize_vectorstore()

    def initialize_vectorstore(self):
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            self.vectorstore = DeepLake(dataset_path=self.dataset_path, embedding=OpenAIEmbeddings(), read_only=True)

            self.vectorstore_initialized = True
            print(f"Vector store initialized for course ID {self.courseid}")
        except Exception as e:
            print(f"Error al inicializar vectorstore: {e}")
            self.vectorstore_initialized = False

    async def query(self, query_text):
        if not self.vectorstore_initialized:
            self.initialize_vectorstore()
        start_time = time.time()
        result = self.vectorstore.similarity_search(query_text)
        end_time = time.time()
        response_time = end_time - start_time
        print(f"VideoQA Query Time: {response_time:.4f} seconds")
        # print("Esto es vector DATABASE imprime de videoqa", result)
        
        return result
import os
import re
import time

class VectorDatabaseManager:
    def __init__(self):
        self.instances = {}
        self.initialize_all_instances()

    def initialize_all_instances(self):
        try:
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
                try:
                    if prefix == "PDF":
                        self.instances[f"PDF-{courseid}"] = PDFQA(courseid)
                    elif prefix == "VIDEO":
                        self.instances[f"VIDEO-{courseid}"] = VideoQA(courseid)
                except Exception as e:
                    print(f"Error initializing instance for {prefix}-{courseid}: {str(e)}")
            print(f"Initialized instances: {self.instances}")
        except Exception as e:
            print(f"Error initializing instances: {str(e)}")

    async def query_instance(self, courseid: str, query_text: str, type: str):
        try:
            instance_key = f"{type}-{courseid}"
            print(f"Querying instance with key: {instance_key}")
            if instance_key in self.instances:
                print(f"Found instance for key: {instance_key}")
                start_time = time.time()
                instance = self.instances[instance_key]
                result = await instance.query(query_text)
                end_time = time.time()
                response_time = end_time - start_time
                print(f"Total Query Time for {instance_key}: {response_time:.4f} seconds")
                return result
            else:
                print(f"No instance found for key: {instance_key}")
                return {"error": f"No instance found for {type}-{courseid}"}
        except Exception as e:
            print(f"Error during query for {type}-{courseid}: {str(e)}")
            return {"error": f"Failed to query instance {type}-{courseid}: {str(e)}"}
