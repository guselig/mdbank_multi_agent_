from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette
from executer import CartaoDeCreditoExecutor

# -----------------------
# Definição do skill
# -----------------------
skill = AgentSkill(
    id="cartao_credito",
    name="Cartões de Crédito MDBank",
    description="Ajuda clientes com dúvidas, solicitação e limites de cartões de crédito.",
    tags=["cartão", "credito", "limite",
          "platinum", "gold", "silver", "mdzao"],
    examples=[
        "quais cartões vocês têm?",
        "quero solicitar um cartão platinum",
        "qual é o limite do meu cartão?",
        "posso aumentar meu limite?",
        "quero um cartão mdzao"
    ],
)

# -----------------------
# Agent Card
# -----------------------
agent_card = AgentCard(
    name="Agente de Cartões MDBank",
    description="Especialista em cartões de crédito do MDBank.",
    supported_interfaces=[
        AgentInterface(
            protocol_binding='JSONRPC',
            url='http://cartao_credito_agent:8000/api/v1/jsonrpc/',
        ),
    ],
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[skill],
    version="1.0.0",
    capabilities=AgentCapabilities(),
)
# -----------------------
# Request Handler
# -----------------------
handler = DefaultRequestHandler(
    agent_executor=CartaoDeCreditoExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

# -----------------------
# Define routes for transports
# -----------------------
routes = []
# A2A Agent Card routes
routes.extend(create_agent_card_routes(agent_card))
# JSON-RPC routes
routes.extend(create_jsonrpc_routes(handler, rpc_url='/api/v1/jsonrpc/'))

# -----------------------
# Create application using routes
# -----------------------
app = Starlette(routes=routes)