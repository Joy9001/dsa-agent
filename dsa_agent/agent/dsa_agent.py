from typing import AsyncGenerator

import config as cfg
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import MultiMCPTools
from agno.tools.thinking import ThinkingTools

from agent.mcp_url import get_gh_url, get_lc_url

from .memory import agent_memory, agent_storage
from .prompt import AGENT_DESCRIPTION


class DSAAgent:
    def __init__(
        self,
        user_id: str,
        session_id: str,
        model_id: str = "gemini-2.5-flash",
        debug_mode: bool = True,
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.model_id = model_id
        self.debug_mode = debug_mode
        self.mcp_tools = self._get_mcp_tools()

    def _get_mcp_tools(self) -> MultiMCPTools:
        lc_mcp_url = get_lc_url()
        gh_mcp_url = get_gh_url()
        return MultiMCPTools(
            urls=[lc_mcp_url, gh_mcp_url],
            urls_transports=["streamable-http", "streamable-http"],
        )

    def _get_agent(
        self,
        user_id: str,
        session_id: str,
        model_id: str,
        tools: list | None = None,
        debug_mode: bool = False,
    ) -> Agent:
        if tools is None:
            tools = []

        return Agent(
            name="DSA Agent",
            model=Gemini(id=model_id, api_key=cfg.GEMINI_API_KEY),
            description=AGENT_DESCRIPTION,
            user_id=user_id,
            session_id=session_id,
            tools=[ThinkingTools(think=True, add_instructions=True), *tools],
            # Store memories in a database
            memory=agent_memory,
            # Give the Agent the ability to update memories
            enable_agentic_memory=True,
            # OR - Run the MemoryManager after each response
            enable_user_memories=True,
            # Store the chat history in the database
            storage=agent_storage,
            # Add the chat history to the messages
            add_history_to_messages=True,
            # Number of history runs
            num_history_runs=10,
            markdown=True,
            add_datetime_to_instructions=True,
            debug_mode=debug_mode,
        )

    async def astream_agent(self, msg: str) -> AsyncGenerator | str:
        async with self.mcp_tools as mcp_tools:
            agent = self._get_agent(
                self.user_id,
                self.session_id,
                self.model_id,
                tools=[mcp_tools],
                debug_mode=self.debug_mode,
            )

            run_response = await agent.arun(msg, stream=True)

            async for chunk in run_response:
                yield chunk.content

    async def arun_agent(self, msg: str) -> str:
        async with self.mcp_tools as mcp_tools:
            agent = self._get_agent(
                self.user_id,
                self.session_id,
                self.model_id,
                tools=[mcp_tools],
                debug_mode=self.debug_mode,
            )

            run_response = await agent.arun(msg, stream=False)
            return run_response.content
