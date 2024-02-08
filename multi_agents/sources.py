# Import libraries

# langchain
#from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake # For DeepLake
from decouple import config

# OpenAI
import os
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

# DeepLake
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")

from decouple import config
from supabase import create_client
url_user: str = config("SUPABASE_USER_URL")
key_user: str = config("SUPABASE_USER_KEY")

supabase_user = create_client(supabase_url=url_user,supabase_key= key_user)

class SourcesQA():
    def __init__(self,courseid,id):
        self.courseid=courseid
        self.id=id
        # Define las variables de entorno aquí o asegúrate de que ya están definidas en el entorno

        # Configura DeepLake y la cadena de QA
        dataset_path = f"hub://skillstech/PDF-{self.courseid}"
        vectorstore = DeepLake(dataset_path=dataset_path, embedding=OpenAIEmbeddings(),read_only=True)

        self.qa = RetrievalQAWithSourcesChain.from_chain_type(
            llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0),
            retriever = vectorstore.as_retriever(),
            return_source_documents = True,
            verbose = True,
        )
    
    def query(self, query_text):
        result = self.qa(query_text)
        for document in result['source_documents']:
    # Get the source title and URL from the metadata of each document
            source_title = document.metadata.get('page', 'No title available.')
            page_content=document.page_content
            Titulo = document.metadata.get('source', 'No url available.')
            print("Page Content",page_content,"Pagina",source_title,' - ',"Titulo",Titulo)

        response_data = { "sources":[{
                "url":"www.google.com",
                "title":result['answer']
                }
                ],
            }

        thread_exists = supabase_user.table("responses_tb").update({"sources":response_data}).eq("id", self.id).execute()


        return result
