import logging
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.helpers import new_text_message
from a2a.types import Role
from agent.abrir_conta import run_agent

logger = logging.getLogger("a2a.abrir_conta.executor")

class AbrirContaExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        logger.info("agent.execute.abrir_conta")

        user_text = context.get_user_input()

        response_balance_agent = await run_agent(mensagem=user_text)

        await event_queue.enqueue_event(
            new_text_message(text=str(response_balance_agent), role=Role.ROLE_AGENT)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        logger.info("agent.cancel.balance")