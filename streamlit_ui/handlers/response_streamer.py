import time
from typing import Any, Dict, Tuple
import html
import streamlit as st


class ResponseStreamer:
    """Handles streaming of agent responses with event tracking"""

    def __init__(self):
        self.start_time = None
        self.event_steps = []
        self.full_response = ""
        self.active_tools = []
        self.current_tool = None
        self.event_log = None
        self.message_placeholder = None
        self.reasoning_steps = 0

    async def stream_response(
        self, agent, user_message: str, show_events: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """Stream agent response and update UI with detailed event handling"""
        self.start_time = time.time()
        self._initialize_execution_tracking()

        with st.chat_message("assistant"):
            self._setup_ui_containers()

            try:
                await self._process_stream(agent, user_message, show_events)
                self._finalize_execution()
            except Exception as e:
                self._handle_stream_error(e)

            return self.full_response, {"event_log": self.event_steps}

    def _initialize_execution_tracking(self):
        """Initialize execution status tracking"""
        self.event_steps = []
        self.full_response = ""
        self.active_tools = []
        self.current_tool = None
        self.reasoning_steps = 0

    def _setup_ui_containers(self):
        """Setup UI containers for event log and content"""
        event_log_container = st.container()
        content_container = st.container()

        with event_log_container:
            st.markdown("**🔄 Processing Steps:**")
            self.event_log = st.empty()

        with content_container:
            self.message_placeholder = st.empty()

    async def _process_stream(self, agent, user_message: str, show_events: bool):
        """Process the event stream from the agent"""
        async for event_data in agent.astream_agent(user_message):
            if not event_data:
                continue

            event_type = event_data.get("event", "unknown")
            data = event_data.get("data", {})
            current_time = time.time()

            if show_events:
                with st.expander(f"🐛 Event: {event_type}", expanded=False):
                    st.json(data)

            await self._handle_event(event_type, data, current_time)

    async def _handle_event(self, event_type: str, data: dict, current_time: float):
        """Handle individual event based on type"""
        event_handlers = {
            "run_started": self._handle_run_started,
            "content": self._handle_content,
            "run_completed": self._handle_run_completed,
            "run_error": self._handle_run_error,
            "run_cancelled": self._handle_run_cancelled,
            "run_paused": self._handle_run_paused,
            "run_continued": self._handle_run_continued,
            "reasoning_started": self._handle_reasoning_started,
            "reasoning_step": self._handle_reasoning_step,
            "reasoning_completed": self._handle_reasoning_completed,
            "tool_call_started": self._handle_tool_call_started,
            "tool_call_completed": self._handle_tool_call_completed,
            "memory_update_started": self._handle_memory_update_started,
            "memory_update_completed": self._handle_memory_update_completed,
            "unknown": self._handle_unknown_event,
        }

        handler = event_handlers.get(event_type, self._handle_unknown_event)
        handler(data, current_time)
        self._update_event_log()

    def _handle_run_started(self, data: dict, current_time: float):
        model_name = data.get("model", "Unknown Model")
        self.event_steps.append(
            {
                "title": f"🚀 Starting execution with {model_name}",
                "details": "Initializing agent and tools",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_content(self, data: dict, current_time: float):
        content = data.get("content", "")
        if content and isinstance(content, str):
            self.full_response += content
            self.message_placeholder.markdown(self.full_response + "▌")

    def _handle_run_completed(self, data: dict, current_time: float):
        self.event_steps.append(
            {
                "title": "✅ Execution completed successfully",
                "details": "Response generation finished",
                "completed": True,
                "start_time": current_time,
                "duration": time.time() - self.start_time,
            }
        )

    def _handle_run_error(self, data: dict, current_time: float):
        error_msg = data.get("error_message", "Unknown error")
        self.event_steps.append(
            {
                "title": "❌ Error occurred",
                "details": error_msg,
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )
        self.full_response = f"**Error**: {error_msg}"

    def _handle_run_cancelled(self, data: dict, current_time: float):
        reason = data.get("reason", "No reason provided")
        self.event_steps.append(
            {
                "title": "⏹️ Execution cancelled",
                "details": reason,
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_run_paused(self, data: dict, current_time: float):
        tools = data.get("tools", [])
        self.event_steps.append(
            {
                "title": "⏸️ Execution paused",
                "details": f"{len(tools)} tools need confirmation",
                "completed": False,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_run_continued(self, data: dict, current_time: float):
        self.event_steps.append(
            {
                "title": "▶️ Execution resumed",
                "details": "Continuing with approved actions",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_reasoning_started(self, data: dict, current_time: float):
        self.reasoning_steps = 0
        self.event_steps.append(
            {
                "title": "🧠 Starting reasoning process",
                "details": "Analyzing and planning response",
                "completed": False,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_reasoning_step(self, data: dict, current_time: float):
        self.reasoning_steps += 1
        self.event_steps.append(
            {
                "title": f"🧠 Reasoning step {self.reasoning_steps}",
                "details": "Processing logical connections",
                "completed": False,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_reasoning_completed(self, data: dict, current_time: float):
        self.event_steps.append(
            {
                "title": "🧠 Reasoning completed",
                "details": f"Completed {self.reasoning_steps} reasoning steps",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_tool_call_started(self, data: dict, current_time: float):
        tool = data.get("tool")
        if tool and isinstance(tool, dict):
            tool_name = tool.get("name", "Unknown Tool")
            tool_args = tool.get("args", "No Args")
            self.current_tool = {"name": tool_name, "args": tool_args}
            self.active_tools.append(tool_name)
            self.event_steps.append(
                {
                    "title": f"🔧 Using tool: {tool_name}",
                    "details": f"Executing with args: {tool_args}",
                    "completed": False,
                    "start_time": current_time,
                    "duration": 0,
                }
            )

    def _handle_tool_call_completed(self, data: dict, current_time: float):
        tool = data.get("tool")
        result = data.get("result")
        if tool and isinstance(tool, dict) and self.current_tool:
            tool_name = tool.get("name", "Unknown Tool")
            tool_args = self.current_tool.get("args", "No Args")
            if tool_name in self.active_tools:
                self.active_tools.remove(tool_name)

            self.event_steps.append(
                {
                    "title": f"🔧 Tool: {tool_name} completed",
                    "details": f"Tool execution completed successfully with args: {tool_args} and result: {result}",
                    "completed": True,
                    "start_time": current_time,
                    "duration": 0,
                }
            )
            self.current_tool = None

    def _handle_memory_update_started(self, data: dict, current_time: float):
        self.event_steps.append(
            {
                "title": "💾 Updating memory",
                "details": "Storing conversation context",
                "completed": False,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_memory_update_completed(self, data: dict, current_time: float):
        self.event_steps.append(
            {
                "title": "💾 Memory updated",
                "details": "Memory updated successfully",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

    def _handle_unknown_event(self, data: dict, current_time: float):
        raw_content = data.get("raw_content")
        if raw_content and isinstance(raw_content, str):
            self.full_response += raw_content
            self.message_placeholder.markdown(self.full_response + "▌")

    def _update_event_log(self):
        if not self.event_steps:
            return

        log_html = "<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; color: #262730;'>"
        for step in self.event_steps:
            title = html.escape(step["title"])
            log_html += f"<div style='padding: 2px 0; color: #262730;'> <strong style='color: #262730;'>{title}</strong>"
            if step.get("details"):
                details = html.escape(step["details"])
                log_html += f" - <span style='color: #6c757d;'>{details}</span>"
            if step.get("duration") is not None:
                log_html += (
                    f" <em style='color: #28a745;'>({step['duration']:.2f}s)</em>"
                )
            log_html += "</div>"
        log_html += "</div>"

        # Optional: debug output
        # print(log_html.encode("unicode_escape").decode())

        self.event_log.markdown(log_html, unsafe_allow_html=True)

    def _finalize_execution(self):
        execution_time = time.time() - self.start_time
        self.event_steps.append(
            {
                "title": "🎉 All processing completed",
                "details": f"Total execution time: {execution_time:.2f}s",
                "completed": True,
                "start_time": time.time(),
                "duration": 0,
            }
        )
        self._update_event_log()

    def _handle_stream_error(self, error: Exception):
        error_msg = f"**Streaming Error**: {str(error)}"
        self.message_placeholder.markdown(error_msg)
        self.event_steps.append(
            {
                "title": "❌ Processing failed",
                "details": str(error),
                "completed": True,
                "start_time": time.time(),
                "duration": 0,
            }
        )
        self.full_response = error_msg
        self._update_event_log()
