"""
Response streaming handler for Streamlit DSA Agent
"""

import time
from typing import Any, Dict, Tuple

import streamlit as st


class ResponseStreamer:
    """Handles streaming of agent responses with event tracking"""

    def __init__(self):
        self.start_time = None
        self.execution_status = None
        self.event_steps = []
        self.full_response = ""
        self.active_tools = []
        self.current_tool = None
        self.event_log = None
        self.message_placeholder = None

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

            return self.full_response, self.execution_status

    def _initialize_execution_tracking(self):
        """Initialize execution status tracking"""
        self.execution_status = {
            "run_status": None,
            "reasoning_status": None,
            "tools_used": [],
            "memory_status": None,
            "details": {
                "total_events": 0,
                "execution_time": 0,
                "model_used": None,
                "reasoning_steps": 0,
                "thinking_content": None,
            },
        }
        self.event_steps = []
        self.full_response = ""
        self.active_tools = []
        self.current_tool = None

    def _setup_ui_containers(self):
        """Setup UI containers for event log and content"""
        # Create event log container at the top
        event_log_container = st.container()

        # Main content container
        content_container = st.container()

        # Event log display
        with event_log_container:
            st.markdown("**🔄 Processing Steps:**")
            self.event_log = st.empty()

        # Main content area
        with content_container:
            self.message_placeholder = st.empty()

    async def _process_stream(self, agent, user_message: str, show_events: bool):
        """Process the event stream from the agent"""
        async for event_data in agent.astream_agent(user_message):
            if not event_data:
                continue

            self.execution_status["details"]["total_events"] += 1
            event_type = event_data.get("event", "unknown")
            data = event_data.get("data", {})
            current_time = time.time()

            # Show event details in debug mode
            if show_events:
                with st.expander(f"🐛 Event: {event_type}", expanded=False):
                    st.json(data)

            # Handle the event
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
        """Handle run started event"""
        model_name = data.get("model", "Unknown Model")
        self.event_steps.append(
            {
                "title": f"Starting execution with {model_name}",
                "details": "Initializing agent and tools",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )
        self.execution_status["run_status"] = {
            "type": "info",
            "message": f"Started with {model_name}",
        }
        self.execution_status["details"]["model_used"] = model_name

    def _handle_content(self, data: dict, current_time: float):
        """Handle content event"""
        content = data.get("content", "")
        if content and isinstance(content, str):
            self.full_response += content
            self.message_placeholder.markdown(self.full_response + "▌")

        # Handle thinking content
        thinking = data.get("thinking")
        if thinking:
            self.execution_status["details"]["thinking_content"] = thinking

    def _handle_run_completed(self, data: dict, current_time: float):
        """Handle run completed event"""
        # Mark the last step as completed
        if self.event_steps and not self.event_steps[-1]["completed"]:
            self.event_steps[-1]["completed"] = True
            self.event_steps[-1]["duration"] = (
                current_time - self.event_steps[-1]["start_time"]
            )

        self.event_steps.append(
            {
                "title": "Execution completed successfully",
                "details": "Response generation finished",
                "completed": True,
                "start_time": current_time,
                "duration": 0,
            }
        )

        self.execution_status["run_status"] = {
            "type": "success",
            "message": "Execution Completed",
        }

        #! THIS DUPLICATES THE CONTENT
        # content = data.get("content", "")
        # if content and isinstance(content, str):
        #     self.full_response += content

        # Show final reasoning if available
        reasoning = data.get("reasoning_content")
        if reasoning and not self.execution_status["details"]["thinking_content"]:
            self.execution_status["details"]["thinking_content"] = reasoning

    def _handle_run_error(self, data: dict, current_time: float):
        """Handle run error event"""
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
        self.execution_status["run_status"] = {
            "type": "error",
            "message": f"Error: {error_msg}",
        }
        self.full_response = f"**Error**: {error_msg}"

    def _handle_run_cancelled(self, data: dict, current_time: float):
        """Handle run cancelled event"""
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
        self.execution_status["run_status"] = {
            "type": "warning",
            "message": f"Cancelled: {reason}",
        }

    def _handle_run_paused(self, data: dict, current_time: float):
        """Handle run paused event"""
        tools = data.get("tools", [])
        self.event_steps.append(
            {
                "title": "⏸️ Execution paused",
                "details": f"{len(tools)} tools need confirmation",
                "completed": False,
                "start_time": current_time,
            }
        )
        self.execution_status["run_status"] = {
            "type": "warning",
            "message": f"Paused ({len(tools)} tools need confirmation)",
        }

    def _handle_run_continued(self, data: dict, current_time: float):
        """Handle run continued event"""
        if self.event_steps and not self.event_steps[-1]["completed"]:
            self.event_steps[-1]["completed"] = True
            self.event_steps[-1]["duration"] = (
                current_time - self.event_steps[-1]["start_time"]
            )

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
        """Handle reasoning started event"""
        self.event_steps.append(
            {
                "title": "🧠 Starting reasoning process",
                "details": "Analyzing and planning response",
                "completed": False,
                "start_time": current_time,
            }
        )
        self.execution_status["reasoning_status"] = {
            "type": "info",
            "message": "Reasoning Active",
        }

    def _handle_reasoning_step(self, data: dict, current_time: float):
        """Handle reasoning step event"""
        self.execution_status["details"]["reasoning_steps"] += 1
        content = data.get("content", "")

        # Update current reasoning step
        if self.event_steps and "reasoning" in self.event_steps[-1]["title"].lower():
            self.event_steps[-1]["details"] = (
                f"Step {self.execution_status['details']['reasoning_steps']}: Processing..."
            )
        else:
            self.event_steps.append(
                {
                    "title": f"🧠 Reasoning step {self.execution_status['details']['reasoning_steps']}",
                    "details": "Processing logical connections",
                    "completed": False,
                    "start_time": current_time,
                }
            )

        if content and isinstance(content, str):
            self.full_response += content
            self.message_placeholder.markdown(self.full_response + "▌")

    def _handle_reasoning_completed(self, data: dict, current_time: float):
        """Handle reasoning completed event"""
        # Mark reasoning as completed
        for step in reversed(self.event_steps):
            if "reasoning" in step["title"].lower() and not step["completed"]:
                step["completed"] = True
                step["duration"] = current_time - step["start_time"]
                step["details"] = (
                    f"Completed {self.execution_status['details']['reasoning_steps']} reasoning steps"
                )
                break

        self.execution_status["reasoning_status"] = {
            "type": "success",
            "message": f"Reasoning Complete ({self.execution_status['details']['reasoning_steps']} steps)",
        }

    def _handle_tool_call_started(self, data: dict, current_time: float):
        """Handle tool call started event"""
        tool = data.get("tool")
        if tool and isinstance(tool, dict):
            print(f"Tool call started: {tool}")
            tool_name = tool.get("name", "Unknown Tool")
            tool_args = tool.get("args", "No Args")
            self.current_tool = {
                "name": tool_name,
                "args": tool_args,
                "started_at": current_time,
                "result_preview": None,
            }
            self.active_tools.append(tool_name)

            self.event_steps.append(
                {
                    "title": f"🔧 Using tool: {tool_name}",
                    "details": f"Executing tool function with args: {tool_args}",
                    "completed": False,
                    "start_time": current_time,
                }
            )

    def _handle_tool_call_completed(self, data: dict, current_time: float):
        """Handle tool call completed event"""
        tool = data.get("tool")
        result = data.get("result")
        if tool and isinstance(tool, dict) and self.current_tool:
            tool_name = tool.get("name", "Unknown Tool")
            tool_args = tool.get("args", "No Args")
            if tool_name in self.active_tools:
                self.active_tools.remove(tool_name)

            # Store tool information
            self.current_tool["result_preview"] = result if result else "No Result"
            self.execution_status["tools_used"].append(self.current_tool)

            # Mark tool as completed
            for step in reversed(self.event_steps):
                if (
                    f"tool: {tool_name}" in step["title"].lower()
                    and not step["completed"]
                ):
                    step["completed"] = True
                    step["duration"] = current_time - step["start_time"]
                    step["details"] = (
                        f"Tool execution completed successfully with args: {tool_args} and result: \n{result}"
                    )
                    break

            self.current_tool = None

    def _handle_memory_update_started(self, data: dict, current_time: float):
        """Handle memory update started event"""
        self.event_steps.append(
            {
                "title": "💾 Updating memory",
                "details": "Storing conversation context",
                "completed": False,
                "start_time": current_time,
            }
        )
        self.execution_status["memory_status"] = {
            "type": "info",
            "message": "Memory Update Active",
        }

    def _handle_memory_update_completed(self, data: dict, current_time: float):
        """Handle memory update completed event"""
        # Mark memory update as completed
        for step in reversed(self.event_steps):
            if "memory" in step["title"].lower() and not step["completed"]:
                step["completed"] = True
                step["duration"] = current_time - step["start_time"]
                step["details"] = "Memory updated successfully"
                break

        self.execution_status["memory_status"] = {
            "type": "success",
            "message": "Memory Updated",
        }

    def _handle_unknown_event(self, data: dict, current_time: float):
        """Handle unknown event"""
        raw_content = data.get("raw_content")
        if raw_content and isinstance(raw_content, str):
            self.full_response += raw_content
            self.message_placeholder.markdown(self.full_response + "▌")

    def _update_event_log(self):
        """Update the event log display"""
        if not self.event_steps:
            return

        log_html = "<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; color: #262730;'>"
        for step in self.event_steps:
            status_icon = "✅" if step["completed"] else "🔄"
            log_html += f"<div style='padding: 2px 0; color: #262730;'>{status_icon} <strong style='color: #262730;'>{step['title']}</strong>"
            if step.get("details"):
                log_html += f" - <span style='color: #6c757d;'>{step['details']}</span>"
            if step.get("duration") and step["completed"]:
                log_html += (
                    f" <em style='color: #28a745;'>({step['duration']:.2f}s)</em>"
                )
            log_html += "</div>"
        log_html += "</div>"
        self.event_log.markdown(log_html, unsafe_allow_html=True)

    def _finalize_execution(self):
        """Finalize execution tracking"""
        # Calculate final execution time
        self.execution_status["details"]["execution_time"] = (
            time.time() - self.start_time
        )

        # Store event log in execution status for persistence
        self.execution_status["event_log"] = self.event_steps

        # Final event log update with completion time
        if self.event_steps:
            # Mark any remaining incomplete steps as completed
            for step in self.event_steps:
                if not step["completed"]:
                    step["completed"] = True
                    step["duration"] = time.time() - step["start_time"]

            # Add final summary
            self.event_steps.append(
                {
                    "title": "🎉 All processing completed",
                    "details": f"Total execution time: {self.execution_status['details']['execution_time']:.2f}s",
                    "completed": True,
                    "start_time": time.time(),
                    "duration": 0,
                }
            )
            self._update_event_log()

    def _handle_stream_error(self, error: Exception):
        """Handle streaming error"""
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

        self.execution_status["run_status"] = {
            "type": "error",
            "message": f"Stream Failed: {str(error)}",
        }
        self.execution_status["details"]["execution_time"] = (
            time.time() - self.start_time
        )
        self.execution_status["event_log"] = self.event_steps
        self.full_response = error_msg
        self._update_event_log()
