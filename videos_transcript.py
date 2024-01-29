import os
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from decouple import config
from langchain_community.chat_models import ChatOpenAI

from langchain.agents import AgentType
from langchain.agents.initialize import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory

os.environ["OPENAI_API_KEY"] = "***REMOVED***PrbQpTkArdcDp4BItWXdT3BlbkFJN76nqGc4qtQzGYXxVDfO"

# Pinecone
import pinecone
pinecone.init(
    api_key="71d56197-0de5-45f2-ac9a-c58c3cfb761f", # find at app.pinecone.io | rag
    environment="us-west1-gcp-free" # next to api key in console
)

# create index
index_name = 'skillsgpt'
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        index_name,
        dimension=1536,
        metric='cosine',
    )



openai_api_key=config('OPEN_AI_KEY')

# connect to the index & vectorstore
pinecone_index = pinecone.Index(index_name)
vectorstore = Pinecone.from_existing_index(index_name, OpenAIEmbeddings())
llm = ChatOpenAI(verbose=True,model="gpt-4-1106-preview",openai_api_key=openai_api_key,temperature=0.5)


from langchain.agents import Tool

from langchain.chains import RetrievalQAWithSourcesChain
qa = RetrievalQAWithSourcesChain.from_chain_type(
llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0),
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'fetch_k': 3}),
return_source_documents=True,
verbose=True,
)
def transcript_videos(query):
    # query = "How can you become a partner at New York Life?"
    result = qa(query)
    # printAS(result)
    return result["answer"] +printAS(result)


tools = [

             Tool.from_function(
                 name='Transcript Videos',
                 func=transcript_videos,
                 description=(""" Usa esta herramienta , con esto tienes acceso al texto de videos transcritos acerca de NEw York Life , estas entrenando a sus agentes""" 
                 )
                 )
        ]



agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True),
            handle_parsing_errors=True
            
        )


agent.agent.llm_chain.prompt.messages[0].prompt.template="""SkillsGPT is an advanced AI tool designed to aid  agents. It functions as an intelligent chat interface, delivering essential information and resources efficiently. Your primary role is to provide agents with clear, precise responses and pertinent external links.

When you receive links or specific materials from your tools, organize this information to enhance clarity and visual appeal. Make sure your responses are not only informative but also well-structured and easy to understand.

As SkillsGPT, your aim is to be a dependable and insightful assistant, streamlining access to knowledge and resources for agents, while ensuring that the information presented is both coherent and visually engaging.

THE MOST IMPORTANT THING IT'S VITAL EVERYTHING DEPEND ON THIS:
--------------------------------------------------------------
YOU HAVE TOOLS , IF THE TOOLS RETURN A LINK OR INFORMATION , SHOW ALL THE INFORMACION RETURNED , JUST MAKE IT BETTER , DON'T CUT THE INFORMATION 

"""














def printAS(result):

  """
  Prints the 'answer' (A) and the sources (S) from the 'source_documents' list in the result dictionary.
  Adapted for RetrievalQAWithSourcesChain

  Parameters:
  result (dict): A dictionary containing keys 'answer' and 'source_documents'. The 'source_documents'
                 key should be a list of Document objects, each having a 'metadata' dictionary with
                 a 'source' key.

  Output:
  Prints the 'answer' followed by the phrase "To know more, check:" and then each source URL
  on a new line. If no source URL is found, it prints 'No source available.' for that entry.
  """
  answer="\nTo know more, check:"
  # Print the 'answer'
  print(result.get('answer', 'No answer available.'))
  answer=answer
  # Print the introductory phrase for sources
  print("\nTo know more, check:")

  # Check if 'source_documents' key exists in the result
  if 'source_documents' in result:
    for document in result['source_documents']:
      # Get the source title and URL from the metadata of each document
      source_title = document.metadata.get('title', 'No title available.')
      source_url = document.metadata.get('source', 'No url available.')
      print(source_title,' - ',source_url)
      answer=answer+source_title+' - '+source_url
  else:
    print("No source documents available.")
  return answer