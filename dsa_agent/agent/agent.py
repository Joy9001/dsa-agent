from typing import AsyncGenerator

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import MultiMCPTools
from agno.tools.thinking import ThinkingTools

import dsa_agent.config as cfg
from dsa_agent.agent.memory import initialize_agent_memory, initialize_agent_storage
from dsa_agent.agent.prompt import AGENT_DESCRIPTION, AGENT_INSTRUCTION
from dsa_agent.logger import logger
from dsa_agent.monitor import time_component

from .mcp_url import get_smithery_url


class DSAAgent:
    def __init__(
        self,
        user_id: str,
        session_id: str,
        gemini_api_key: str,
        lc_session: str,
        gh_token: str,
        model_id: str = "gemini-2.5-flash",
        debug_mode: bool = True,
        lc_site: str = "global",
    ):
        logger.info(
            f"Initializing DSA Agent for user_id={user_id}, session_id={session_id}, model_id={model_id}, debug_mode={debug_mode}"
        )
        self.user_id = user_id
        self.session_id = session_id
        self.model_id = model_id
        self.debug_mode = debug_mode
        self.lc_site = lc_site
        self.lc_session = lc_session
        self.gh_token = gh_token
        self.gemini_api_key = gemini_api_key

        logger.debug("Setting up MCP tools for DSA Agent")
        self.mcp_tools = self._get_mcp_tools()
        logger.info(f"DSA Agent initialized successfully for user {user_id}")

    @time_component()
    def _safe_get_tool_info(self, tool) -> dict | None:
        """Safely extract tool information for serialization"""
        if tool is None:
            return None

        tool_info = {}
        try:
            tool_info["name"] = getattr(tool, "tool_name", "Unknown Tool")
            tool_info["args"] = getattr(tool, "tool_args", "Unknown Args")
        except Exception as e:
            logger.warning(f"Could not extract tool info: {e}")
            tool_info = {"name": "Tool Info Unavailable", "error": str(e)}

        return tool_info

    @time_component()
    def _get_mcp_tools(self) -> MultiMCPTools:
        logger.debug("Generating MCP URLs for LeetCode and GitHub")

        # Use provided values
        lc_site = self.lc_site
        lc_session = self.lc_session
        gh_token = self.gh_token

        # Generate LeetCode MCP URL
        lc_mcp_url = get_smithery_url(
            base_url=cfg.LC_MCP_BASE_URL,  # type: ignore
            config={
                "site": lc_site,
                "session": lc_session,
            },
            api_key=cfg.SMITHERY_API_KEY,  # type: ignore
            profile=cfg.SMITHERY_PROFILE,  # type: ignore
        )

        # Generate GitHub MCP URL
        gh_mcp_url = get_smithery_url(
            base_url=cfg.GH_MCP_BASE_URL,  # type: ignore
            config={"githubPersonalAccessToken": gh_token},
            api_key=cfg.SMITHERY_API_KEY,  # type: ignore
            profile=cfg.SMITHERY_PROFILE,  # type: ignore
        )

        logger.debug(f"LeetCode MCP URL: {lc_mcp_url}")
        logger.debug(f"GitHub MCP URL: {gh_mcp_url}")

        logger.info("Creating MultiMCPTools instance with streamable-http transport")
        mcp_tools = MultiMCPTools(
            urls=[lc_mcp_url, gh_mcp_url],
            urls_transports=["streamable-http", "streamable-http"],
        )
        logger.debug("MCP tools initialized successfully")
        return mcp_tools

    @time_component()
    def _get_agent(
        self,
        user_id: str,
        session_id: str,
        model_id: str,
        tools: list | None = None,
        debug_mode: bool = False,
    ) -> Agent:
        logger.debug(
            f"Creating agent instance with user_id={user_id}, session_id={session_id}, model_id={model_id}"
        )
        if tools is None:
            tools = []
            logger.debug("No tools provided, using empty tools list")
        else:
            logger.debug(f"Using {len(tools)} tools for agent creation")

        logger.info(f"Initializing Gemini model with ID: {model_id}")
        try:
            # Initialize memory and storage with the user-provided API key
            agent_memory = initialize_agent_memory(self.gemini_api_key, model_id)
            agent_storage = initialize_agent_storage()

            agent = Agent(
                name="DSA Agent",
                model=Gemini(id=model_id, api_key=self.gemini_api_key),
                description=AGENT_DESCRIPTION,
                instructions=[AGENT_INSTRUCTION],
                user_id=user_id,
                session_id=session_id,
                tools=[ThinkingTools(think=True, add_instructions=True), *tools],
                # Store memories in a database
                memory=agent_memory,
                # # Give the Agent the ability to update memories
                # enable_agentic_memory=True,
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
                store_events=True,
                stream_intermediate_steps=True,
                debug_mode=debug_mode,
            )
            logger.info(f"Agent created successfully for user {user_id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    async def astream_agent(self, msg: str) -> AsyncGenerator | str:
        logger.info(
            f"Starting streaming agent execution for user {self.user_id}, session {self.session_id}"
        )
        logger.debug(f"Message length: {len(msg)} characters")

        try:
            async with self.mcp_tools as mcp_tools:
                logger.debug("MCP tools context established")
                agent = self._get_agent(
                    self.user_id,
                    self.session_id,
                    self.model_id,
                    tools=[mcp_tools],
                    debug_mode=self.debug_mode,
                )

                logger.info("Executing agent.arun() in streaming mode")
                response_stream = await agent.arun(
                    msg, stream=True, stream_intermediate_steps=True
                )

                event_count = 0
                async for event in response_stream:
                    event_count += 1
                    logger.info(f"DSA Agent (streaming event #{event_count}): {event}")

                    # Handle different event types and yield structured content
                    content = None
                    event_data = {
                        "event_type": event.event,
                        "timestamp": getattr(event, "created_at", None),
                        "agent_id": getattr(event, "agent_id", None),
                        "run_id": getattr(event, "run_id", None),
                        "session_id": getattr(event, "session_id", None),
                    }

                    if event.event == "RunStarted":
                        event_data.update(
                            {
                                "model": getattr(event, "model", ""),
                                "model_provider": getattr(event, "model_provider", ""),
                            }
                        )
                        content = {"event": "run_started", "data": event_data}

                    elif event.event == "RunResponseContent":
                        event_data.update(
                            {
                                "content": getattr(event, "content", None),
                                "content_type": getattr(event, "content_type", "str"),
                                "thinking": getattr(event, "thinking", None),
                            }
                        )
                        content = {"event": "content", "data": event_data}

                    elif event.event == "RunCompleted":
                        event_data.update(
                            {
                                "content": getattr(event, "content", None),
                                "content_type": getattr(event, "content_type", "str"),
                                "reasoning_content": getattr(
                                    event, "reasoning_content", None
                                ),
                                "thinking": getattr(event, "thinking", None),
                            }
                        )
                        content = {"event": "run_completed", "data": event_data}

                    elif event.event == "RunPaused":
                        event_data.update(
                            {
                                "tools": getattr(event, "tools", None),
                            }
                        )
                        content = {"event": "run_paused", "data": event_data}

                    elif event.event == "RunContinued":
                        content = {"event": "run_continued", "data": event_data}

                    elif event.event == "RunError":
                        event_data.update(
                            {
                                "error_message": getattr(event, "content", None),
                            }
                        )
                        content = {"event": "run_error", "data": event_data}

                    elif event.event == "RunCancelled":
                        event_data.update(
                            {
                                "reason": getattr(event, "reason", None),
                            }
                        )
                        content = {"event": "run_cancelled", "data": event_data}

                    elif event.event == "ReasoningStarted":
                        content = {"event": "reasoning_started", "data": event_data}

                    elif event.event == "ReasoningStep":
                        event_data.update(
                            {
                                "content": getattr(event, "content", None),
                                "content_type": getattr(event, "content_type", "str"),
                                "reasoning_content": getattr(
                                    event, "reasoning_content", ""
                                ),
                            }
                        )
                        content = {"event": "reasoning_step", "data": event_data}

                    elif event.event == "ReasoningCompleted":
                        event_data.update(
                            {
                                "content": getattr(event, "content", None),
                                "content_type": getattr(event, "content_type", "str"),
                            }
                        )
                        content = {"event": "reasoning_completed", "data": event_data}

                    elif event.event == "ToolCallStarted":
                        event_data.update(
                            {
                                "tool": self._safe_get_tool_info(
                                    getattr(event, "tool", None)
                                ),
                            }
                        )
                        content = {"event": "tool_call_started", "data": event_data}

                    elif event.event == "ToolCallCompleted":
                        tool = getattr(event, "tool", None)
                        event_data.update(
                            {
                                "tool": self._safe_get_tool_info(tool),
                                "result": tool.result
                                if tool and hasattr(tool, "result")
                                else None,
                            }
                        )
                        content = {"event": "tool_call_completed", "data": event_data}

                    elif event.event == "MemoryUpdateStarted":
                        content = {"event": "memory_update_started", "data": event_data}

                    elif event.event == "MemoryUpdateCompleted":
                        content = {
                            "event": "memory_update_completed",
                            "data": event_data,
                        }

                    else:
                        # Handle unknown events
                        event_data.update(
                            {
                                "raw_content": getattr(event, "content", None),
                            }
                        )
                        content = {"event": "unknown", "data": event_data}

                    if content:
                        logger.info(f"Yielding content: {content}")
                        yield content

                logger.info(
                    f"Streaming execution completed. Total events: {event_count}"
                )
        except Exception as e:
            logger.error(f"Error in streaming agent execution: {e}")
            raise

    async def arun_agent(self, msg: str) -> str:
        logger.info(
            f"Starting non-streaming agent execution for user {self.user_id}, session {self.session_id}"
        )
        logger.debug(
            f"Message content: {msg[:100]}..."
            if len(msg) > 100
            else f"Message content: {msg}"
        )

        try:
            async with self.mcp_tools as mcp_tools:
                logger.debug(
                    "MCP tools context established for non-streaming execution"
                )
                agent = self._get_agent(
                    self.user_id,
                    self.session_id,
                    self.model_id,
                    tools=[mcp_tools],
                    debug_mode=self.debug_mode,
                )

                logger.info("Executing agent.arun() in non-streaming mode")
                run_response = await agent.arun(msg, stream=False)

                response_content = run_response.content
                logger.info(
                    f"Agent execution completed. Response length: {len(response_content)} characters"
                )
                logger.debug(
                    f"Response preview: {response_content[:200]}..."
                    if len(response_content) > 200
                    else f"Full response: {response_content}"
                )

                return response_content
        except Exception as e:
            logger.error(f"Error in non-streaming agent execution: {e}")
            raise
