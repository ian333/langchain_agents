# Import libraries

# langchain
#from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake # For DeepLake
from decouple import config
import os 
# OpenAI
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

# DeepLake
os.environ["ACTIVELOOP_TOKEN"] = config("ACTIVELOOP_TOKEN")


class VideosQA():
    def __init__(self,courseid):
        self.courseid=courseid
        # Define las variables de entorno aquí o asegúrate de que ya están definidas en el entorno

        # Configura DeepLake y la cadena de QA
        dataset_path = f"hub://VIDEOS/{self.courseid}"
        vectorstore = DeepLake(dataset_path=dataset_path, embedding=OpenAIEmbeddings())

        self.qa = RetrievalQAWithSourcesChain.from_chain_type(
            llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0),
            retriever = vectorstore.as_retriever(),
            return_source_documents = True,
            verbose = True,
        )
    
    def query(self, query_text):
        result = self.qa(query_text)
        return result
