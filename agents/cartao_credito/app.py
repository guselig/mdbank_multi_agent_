from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import os

load_dotenv()

__llm = init_chat_model(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
)

app = FastAPI()

agente_cartao_credito = create_agent(
    __llm,
    tools=[],
    system_prompt=(
        "Você é um especialista em cartão de crédito do banco MDBank e sempre avise que você é um agente de IA no final da repsosta."
        "Os cartões que existem no MDBank são: [platinum, gold, silver, md_card e cartao_bronze]. "
        "Ajude o cliente com dúvidas, solicitação e limites."
    )
)
class CartaoCreditoRequest(BaseModel):
    message: str

@app.post("/send")
async def consultar(payload: CartaoCreditoRequest):
    message = payload.message
    if not message:
        raise HTTPException(status_code=400, detail="Campo 'message' é obrigatório")
    
    try:
        resultado = agente_cartao_credito.invoke(
            {"messages": [HumanMessage(content=message)]}
        )
        mensagem_ia = str(resultado["messages"][-1])
        return {"resposta": mensagem_ia}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def health():
    return {"message": "API de cartão de crédito do MDBank está funcionando!"}