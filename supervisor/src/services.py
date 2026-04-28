import logging
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
from operator import add

from a2a.client import create_client
from a2a.helpers import new_text_message, get_message_text
from a2a.types import Role

from src.agents import classifique_intencao_do_usuario

logger = logging.getLogger(__name__)

AGENTS = {
    "cartao_credito": "http://cartao_credito_agent:8000",
    "abrir_conta": "http://abrir_conta_agent:8000"
}

CLIENT_CACHE = {}

class State(TypedDict):
    query: str
    responses: Annotated[list[str], add]

async def request_agent(message: str, agent_url: str) -> str:
    if agent_url not in CLIENT_CACHE:
        logger.info(f"Criando cliente para agente em {agent_url}")
        
        # v1.0: create_client é async e retorna diretamente o cliente
        CLIENT_CACHE[agent_url] = await create_client(agent_url)
        logger.info(f"Cliente criado com sucesso")

    client = CLIENT_CACHE[agent_url]

    # v1.0: Criar mensagem
    msg = new_text_message(text=message, role=Role.ROLE_USER)

    logger.info(f"Enviando mensagem para agente: {message}")

    # v1.0: send_message aceita Message diretamente - o cliente cria o request internamente
    async for chunk in client.send_message(msg):
        # Verificar se o chunk contém uma mensagem
        if chunk.HasField('message'):
            # Usar helper get_message_text para extrair texto
            response_text = get_message_text(chunk.message)
            if response_text:
                return response_text
                
    return "Sem resposta do agente."


async def no_de_roteamento(state: State):
    
    query = state.get("query", "")
    
    classifications = classifique_intencao_do_usuario(query)
    
    logger.info(f"Classificação: {classifications}")
    
    return [
        Send(c["agent"], {"query": c["query"]}) 
        for c in classifications
        ]


async def cartao_credito_node(state: State):
    
    query = state.get("query", "")
    
    logger.info("Executando agente CARTAO_CREDITO")
    
    resposta = await request_agent(
        query, 
        AGENTS["cartao_credito"]
        )
    
    return {"responses": [resposta]}


async def abrir_conta_node(state: State):
    
    query = state.get("query", "")
    
    logger.info("Executando agente ABRIR_CONTA")
    
    resposta = await request_agent(
        query, 
        AGENTS["abrir_conta"]
        )
    
    return {"responses": [resposta]}


# -----------------------------
# CONSTRUÇÃO DO GRAFO
# -----------------------------

# 1. Inicializar o grafo
builder = StateGraph(State)

# 2. Adicionar os nós (agentes especializados)
builder.add_node("abrir_conta", abrir_conta_node)
builder.add_node("cartao_credito", cartao_credito_node)

# 3. Adicionar aresta condicional do START (roteamento)
builder.add_conditional_edges(START, no_de_roteamento)

# 4. Adicionar arestas dos agentes para o END
builder.add_edge("abrir_conta", END)
builder.add_edge("cartao_credito", END)

# 5. Compilar o grafo
graph = builder.compile()

# -----------------------------
# EXECUTOR DO SUPERVISOR (NORMAL)
# -----------------------------


async def executar_supervisor(texto_usuario: str):
    
    input_state: State = {"query": texto_usuario, "responses": []}
    
    result = await graph.ainvoke(input_state)
    
    return "\n\n".join(result["responses"])
