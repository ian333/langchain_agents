import os
from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from decouple import config


llm = ChatOpenAI(
    openai_api_key=config("OPENAI_API_KEY"),
    temperature=0.0,
    model_name="gpt-3.5-turbo",
    streaming=True,  # ! important
    callbacks=[StreamingStdOutCallbackHandler()]  # ! important
)


from langchain.schema import HumanMessage

# create messages to be passed to chat LLM
messages = [HumanMessage(content="tell me a long story")]

llm(messages)


from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import load_tools, AgentType, initialize_agent

# initialize conversational memory
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True,
    output_key="output"
)

# create a single tool to see how it impacts streaming
tools = load_tools(["llm-math"], llm=llm)

# initialize the agent
agent = initialize_agent(
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    memory=memory,
    verbose=True,
    max_iterations=3,
    early_stopping_method="generate",
    return_intermediate_steps=False
)