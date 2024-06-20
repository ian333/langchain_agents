
import os
from langchain_community.retrievers import TavilySearchAPIRetriever

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from decouple import config
from supabase import create_client

# provide api keys
os.environ["TAVILY_API_KEY"] = config("TAVILY_API_KEY")
os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")




class WebSearch:
    def __init__(self, courseid, id,orgid=None):
        url_user = config("SUPABASE_USER_URL")
        key_user = config("SUPABASE_USER_KEY")
        self.orgid=orgid
        self.courseid = courseid
        self.id = id
        self.retriever = TavilySearchAPIRetriever(k=3)
        self.supabase_user = create_client(supabase_url=url_user, supabase_key=key_user)


    async def query(self,query):
            
        result=self.retriever.invoke(query)

        # prompt = ChatPromptTemplate.from_template(
        #     """Answer the question based only on the context provided.

        # Context: {context}

        # Question: {question}"""
        # )
        # chain = (
        #     RunnablePassthrough.assign(context=(lambda x: x["question"]) | retriever)
        #     | prompt
        #     | ChatOpenAI(model="gpt-4-1106-preview")
        #     | StrOutputParser()
        # )

        # chain.invoke({'question':'Who is the president of France?'})
        print(result)
# Crear una lista para almacenar las fuentes
        sources = []

        # Iterar sobre cada documento en el resultado
        for i, doc in enumerate(result, start=1):
            source = doc.metadata.get('source')
            title = doc.metadata.get('title', 'Title not available')
            url = source
            sources.append({
                "url": url,
                "title": title,
                "sourceNumber": i
            })

        data = {"sources": sources}
        print(data)

        try:
                            # Inicialización de clientes Supabase
            thread_exists = self.supabase_user.table("responses_tb").update({"sources": data}).eq("id", self.id).execute()
        except Exception as e:
            print(f"Error al actualizar la base de datos: {e}")
            pass