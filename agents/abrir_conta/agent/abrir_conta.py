from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import os
import uuid

load_dotenv()

_llm = init_chat_model(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

agente_abertura_conta = create_agent(
    _llm,
    tools=[],
    system_prompt=(
        "Você é um especialista em abertura de contas do banco MDBank. "
        "Ajude o cliente a abrir uma conta e explique os tipos disponíveis que são conta simples e conta completa."
    ),
)

async def run_agent(mensagem: str, thread_id: str = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    resultado = await agente_abertura_conta.ainvoke(
        {"messages": [HumanMessage(content=mensagem)]},
        {"configurable": {"thread_id": thread_id}}
    )

    return resultado["messages"][-1].content