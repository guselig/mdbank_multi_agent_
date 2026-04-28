from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.applications import Starlette
from executor import AbrirContaExecutor


# Definição do skill
skill = AgentSkill(
    id="abrir_conta",
    name="Abertura de Conta MDBank",
    description="Ajuda clientes a abrir uma conta bancária e explica os tipos de contas disponíveis.",
    tags=[
        "conta",
        "abrir conta",
        "abrir conta no banco",
        "conta corrente",
        "conta poupança",
        "abrir conta digital",
        "cadastro bancário",
    ],
    examples=[
        "quero abrir uma conta",
        "como faço para abrir uma conta?",
        "quais tipos de conta vocês oferecem?",
        "quero criar uma conta corrente",
        "posso abrir uma conta digital?",
    ],
)

# Agent Card
agent_card = AgentCard(
    name="Agente de Abertura de Conta MDBank",
    description="Especialista em abertura de contas bancárias do MDBank.",
    url="http://abrir_conta_agent:8000/",
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[skill],
    version="1.0.0",
    capabilities=AgentCapabilities(),
)

# Request Handler
handler = DefaultRequestHandler(
    agent_executor=AbrirContaExecutor(),
    task_store=InMemoryTaskStore(),
)

# Define routes for transports as defined in the AgentCard
routes = []
# A2A Agent Card routes
routes.extend(create_agent_card_routes(agent_card))
# JSON-RPC routes
routes.extend(create_jsonrpc_routes(handler, rpc_url='/api/v1/jsonrpc/'))

# Create application using routes
app = Starlette(routes=routes)