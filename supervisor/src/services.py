import logging
import httpx
from pydantic import BaseModel
import requests

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
from operator import add

from src.agents import classifique_intencao_do_usuario

logger = logging.getLogger(__name__)

class State(TypedDict):
    query: str
    responses: Annotated[list[str], add]



async def request_agent(message: str, agent_url: str) -> str:

    url = f"http://{agent_url}:8000/send"
    payload = {"message": message}
    
    try:
        logger.info(f"Enviando requisição para agente em {url} com payload: {payload}") 
        
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx ou 5xx
        
        data = response.json()
        logger.info(f"Resposta recebida do agente: {data}")
        
        return data.get("resposta", "Sem resposta do agente.")
    
    except Exception as e:
        logger.error(f"Erro ao enviar requisição para agente: {e}")
        return "Sem resposta do agente."


async def no_de_roteamento(state: State):
    query = state.get("query", "")
    classifications = classifique_intencao_do_usuario(query)
    logger.info(f"Classificação: {classifications}")
    return [Send(c["agent"], {"query": c["query"]}) for c in classifications]


async def cartao_credito_node(state: State):
    query = state.get("query", "")
    logger.info("Executando agente CARTAO_CREDITO")
    resposta = await request_agent(query, "cartao_credito_agent")
    return {"responses": [resposta]}


async def abrir_conta_node(state: State):
    query = state.get("query", "")
    logger.info("Executando agente ABRIR_CONTA")
    resposta = await request_agent(query, "abrir_conta_agent")
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
