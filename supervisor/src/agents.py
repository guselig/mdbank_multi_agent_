import logging
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

load_dotenv()

__llm = init_chat_model(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

class RouterOutput(BaseModel):
    agents: List[str] = Field(
        description="Lista de agentes disponíveis para roteamento"
    )
    
parser = JsonOutputParser(pydantic_object=RouterOutput)

def classifique_intencao_do_usuario(query: str) -> List[str]:
    prompt = (
        f"""Você é um roteador de agentes de um banco.
        Agentes disponíveis: 
         
        cartao_credito,
        abrir_conta,
        
        Uma pergunta pode exigir mais de um agente.
        
        Responda apenas em JSON.
        
        Pergunta: {query}
        
        {parser.get_format_instructions()}
        """
    )
    
    resposta = __llm.invoke(prompt)
    
    resultado = parser.parse(resposta.content)
    
    agentes = resultado["agents"]
    
    logger.info(f"Agentes classificados para a pergunta '{query}': {agentes}")
    
    return [ 
        {
            "query": query,
            "agent": agente
        } for agente in agentes
    ]
