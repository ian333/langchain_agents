# Import libraries

# langchain
#from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake # For DeepLake
from decouple import config
import re


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
url_admin: str = config("SUPABASE_ADMIN_URL")
key_admin: str = config("SUPABASE_ADMIN_KEY")

supabase_admin = create_client(supabase_url=url_admin,supabase_key= key_admin)
bucket_name = "CoursesFiles"

class SourcesQA():
    def __init__(self,courseid,id):
        self.courseid=courseid
        self.id=id
        # Define las variables de entorno aquí o asegúrate de que ya están definidas en el entorno

        # Configura DeepLake y la cadena de QA
        dataset_path = f"hub://skillstech/PDF-{self.courseid}"
        vectorstore = DeepLake(dataset_path=dataset_path, embedding=OpenAIEmbeddings(),read_only=True,reset=True)

        self.qa = RetrievalQAWithSourcesChain.from_chain_type(
            llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
            retriever = vectorstore.as_retriever(),
            return_source_documents = True,
            verbose = True,
        )
    
    def query(self, query_text):
        result = self.qa(query_text)
        sources=[]
        i=1
        carpeta=self.courseid

        print(result)


        for results in result["source_documents"]:
            print(results)

            source=results.metadata['source']
            nombre_libro_regex = re.search(r'/([^/]*)$', source).group(1)

            page=int(results.metadata['page'])
            print(page)
            url=supabase_admin.storage.from_(bucket_name).get_public_url(f'{carpeta}/{nombre_libro_regex}')
            print(url)
            print(f"{url}#page={page+1}")
            sources.append({
                "url":f"{url}#page={page+1}",
                "title":results.page_content,
                "sourceNumber": i}
                )
            i+=1
            
        data={"sources":sources}
        try:
            thread_exists = supabase_user.table("responses_tb").update({"sources":data}).eq("id", self.id).execute()
        except :
            pass

        


        return result
