import asyncio
import os
import sys
import time
import uuid
from typing import Any, Dict

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dsa_agent"))

from dsa_agent.agent import DSAAgent


class StreamlitDSAAgent:
    """Streamlit interface for the DSA Agent"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        if "agent" not in st.session_state:
            st.session_state.agent = None

    def setup_sidebar(self) -> Dict[str, Any]:
        """Setup the sidebar with configuration options"""
        st.sidebar.title("⚙️ Configuration")

        # Model selection
        model_options = ["gemini-2.5-flash"]
        selected_model = st.sidebar.selectbox(
            "Select Model",
            model_options,
            index=0,
            help="Choose the AI model to use for the agent",
        )

        # Debug mode toggle
        debug_mode = st.sidebar.checkbox(
            "Debug Mode",
            value=True,
            help="Enable debug mode for detailed logging and event information",
        )

        # Event monitoring toggle
        show_events = st.sidebar.checkbox(
            "Show Event Details",
            value=False,
            help="Display detailed event information during agent execution",
        )

        # Session management
        st.sidebar.subheader("🔧 Session Management")

        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("🔄 New Session", help="Start a new conversation session"):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.session_state.agent = None
                st.rerun()

        with col2:
            if st.button(
                "🧹 Clear Status", help="Clear execution status from all messages"
            ):
                for message in st.session_state.messages:
                    if "execution_status" in message:
                        del message["execution_status"]
                st.rerun()

        # Display current session info
        with st.sidebar.expander("📋 Session Info"):
            st.text(f"User ID: {st.session_state.user_id[:8]}...")
            st.text(f"Session ID: {st.session_state.session_id[:8]}...")

            # Show session statistics
            assistant_messages = [
                msg for msg in st.session_state.messages if msg["role"] == "assistant"
            ]
            if assistant_messages:
                st.text(f"Messages: {len(st.session_state.messages)}")
                st.text(f"Responses: {len(assistant_messages)}")

                # Calculate statistics from execution statuses
                total_tools = 0
                total_events = 0
                avg_execution_time = 0

                valid_executions = []
                for msg in assistant_messages:
                    if "execution_status" in msg:
                        exec_status = msg["execution_status"]
                        details = exec_status.get("details", {})

                        total_tools += len(exec_status.get("tools_used", []))
                        total_events += details.get("total_events", 0)

                        exec_time = details.get("execution_time", 0)
                        if exec_time > 0:
                            valid_executions.append(exec_time)

                if valid_executions:
                    avg_execution_time = sum(valid_executions) / len(valid_executions)

                if total_tools > 0:
                    st.text(f"Total Tools Used: {total_tools}")
                if total_events > 0:
                    st.text(f"Total Events: {total_events}")
                if avg_execution_time > 0:
                    st.text(f"Avg Execution Time: {avg_execution_time:.2f}s")

        # Instructions
        st.sidebar.subheader("📚 How to Use")
        st.sidebar.markdown("""
        1. **Problem Solved**: Mention when you've solved a coding problem
        2. **Platform**: Specify the platform (e.g., LeetCode, HackerRank)
        3. **Problem Details**: Share problem number or name
        4. **Notes Creation**: The agent will help create organized notes
        
        **Example Messages:**
        - "I solved LeetCode problem #1 Two Sum"
        - "Help me create notes for the binary search problem I just solved"
        - "I completed problem 206 on LeetCode about reversing a linked list"
        """)

        return {
            "model": selected_model,
            "debug_mode": debug_mode,
            "show_events": show_events,
        }

    def get_agent(self, model: str, debug_mode: bool) -> DSAAgent:
        """Get or create DSA Agent instance"""
        if (
            st.session_state.agent is None
            or st.session_state.get("current_model") != model
            or st.session_state.get("current_debug") != debug_mode
        ):
            st.session_state.agent = DSAAgent(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                model_id=model,
                debug_mode=debug_mode,
            )
            st.session_state.current_model = model
            st.session_state.current_debug = debug_mode

        return st.session_state.agent

    def display_chat_messages(self):
        """Display existing chat messages with persistent status information"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Display the main content
                st.markdown(message["content"])

                # Display persistent execution status for assistant messages
                if message["role"] == "assistant" and "execution_status" in message:
                    execution_status = message["execution_status"]

                    # Show event log if available
                    if "event_log" in execution_status:
                        with st.expander("🔄 Processing Steps", expanded=False):
                            event_steps = execution_status["event_log"]
                            for step in event_steps:
                                status_icon = "✅" if step["completed"] else "🔄"
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"{status_icon} **{step['title']}**")
                                    if step.get("details"):
                                        st.caption(step["details"])
                                with col2:
                                    if step.get("duration") and step["completed"]:
                                        st.caption(f"{step['duration']:.2f}s")

                    st.divider()

                    # Create compact status display in columns
                    status_cols = st.columns([2, 2, 2, 2])

                    with status_cols[0]:
                        run_info = execution_status.get("run_status")
                        if run_info:
                            if run_info["type"] == "success":
                                st.success(run_info["message"], icon="✅")
                            elif run_info["type"] == "error":
                                st.error(run_info["message"], icon="❌")
                            elif run_info["type"] == "warning":
                                st.warning(run_info["message"], icon="⚠️")
                            else:
                                st.info(run_info["message"], icon="ℹ️")

                    with status_cols[1]:
                        reasoning_info = execution_status.get("reasoning_status")
                        if reasoning_info:
                            if reasoning_info["type"] == "success":
                                st.success(reasoning_info["message"], icon="🧠")
                            else:
                                st.info(reasoning_info["message"], icon="🧠")

                    with status_cols[2]:
                        tools_info = execution_status.get("tools_used", [])
                        if tools_info:
                            st.success(f"{len(tools_info)} tool(s)", icon="🔧")
                        else:
                            st.caption("No tools used")

                    with status_cols[3]:
                        memory_info = execution_status.get("memory_status")
                        if memory_info:
                            if memory_info["type"] == "success":
                                st.success(memory_info["message"], icon="💾")
                            else:
                                st.info(memory_info["message"], icon="💾")

                    # Show execution details in a compact format
                    execution_details = execution_status.get("details", {})
                    if execution_details:
                        detail_cols = st.columns([1, 1, 1, 1])

                        with detail_cols[0]:
                            if execution_details.get("total_events"):
                                st.metric(
                                    "Events",
                                    execution_details["total_events"],
                                    label_visibility="collapsed",
                                )

                        with detail_cols[1]:
                            if execution_details.get("execution_time"):
                                st.metric(
                                    "Time (s)",
                                    f"{execution_details['execution_time']:.2f}",
                                    label_visibility="collapsed",
                                )

                        with detail_cols[2]:
                            if execution_details.get("reasoning_steps"):
                                st.metric(
                                    "Reasoning",
                                    execution_details["reasoning_steps"],
                                    label_visibility="collapsed",
                                )

                        with detail_cols[3]:
                            if execution_details.get("model_used"):
                                st.caption(f"Model: {execution_details['model_used']}")

                        # Show additional details in expandable sections if available
                        expandable_sections = []

                        if tools_info:
                            expandable_sections.append("tools")
                        if execution_details.get("thinking_content"):
                            expandable_sections.append("thinking")

                        if expandable_sections:
                            expand_cols = st.columns(len(expandable_sections))

                            col_idx = 0
                            if "tools" in expandable_sections:
                                with expand_cols[col_idx]:
                                    with st.expander(
                                        "🔧 Tools Details", expanded=False
                                    ):
                                        for tool_info in tools_info:
                                            st.write(f"**{tool_info['name']}**")
                                            if tool_info.get("result_preview"):
                                                st.caption(
                                                    f"Result: {tool_info['result_preview']}"
                                                )
                                col_idx += 1

                            if "thinking" in expandable_sections:
                                with expand_cols[col_idx]:
                                    with st.expander("💭 Thinking", expanded=False):
                                        st.text_area(
                                            "",
                                            execution_details["thinking_content"],
                                            height=100,
                                            key=f"thinking_{id(message)}",
                                        )

    async def stream_response(
        self, agent: DSAAgent, user_message: str, show_events: bool = False
    ):
        """Stream agent response and update UI with detailed event handling"""
        start_time = time.time()

        # Initialize execution tracking
        execution_status = {
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

        with st.chat_message("assistant"):
            # Create event log container at the top
            event_log_container = st.container()

            # Main content container
            content_container = st.container()

            # Event log display
            with event_log_container:
                st.markdown("**🔄 Processing Steps:**")
                event_log = st.empty()
                event_steps = []  # Keep track of all events

            # Main content area
            with content_container:
                message_placeholder = st.empty()

            full_response = ""
            active_tools = []
            current_tool = None

            def update_event_log():
                """Update the event log display"""
                if event_steps:
                    log_html = "<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; color: #262730;'>"
                    for i, step in enumerate(event_steps):
                        status_icon = "✅" if step["completed"] else "🔄"
                        log_html += f"<div style='padding: 2px 0; color: #262730;'>{status_icon} <strong style='color: #262730;'>{step['title']}</strong>"
                        if step.get("details"):
                            log_html += f" - <span style='color: #6c757d;'>{step['details']}</span>"
                        if step.get("duration") and step["completed"]:
                            log_html += f" <em style='color: #28a745;'>({step['duration']:.2f}s)</em>"
                        log_html += "</div>"
                    log_html += "</div>"
                    event_log.markdown(log_html, unsafe_allow_html=True)

            try:
                async for event_data in agent.astream_agent(user_message):
                    if not event_data:
                        continue

                    execution_status["details"]["total_events"] += 1
                    event_type = event_data.get("event", "unknown")
                    data = event_data.get("data", {})
                    current_time = time.time()

                    # Show event details in debug mode
                    if show_events:
                        with st.expander(f"🐛 Event: {event_type}", expanded=False):
                            st.json(data)

                    # Handle different event types and update event log
                    if event_type == "run_started":
                        model_name = data.get("model", "Unknown Model")
                        event_steps.append(
                            {
                                "title": f"Starting execution with {model_name}",
                                "details": "Initializing agent and tools",
                                "completed": True,
                                "start_time": current_time,
                                "duration": 0,
                            }
                        )
                        execution_status["run_status"] = {
                            "type": "info",
                            "message": f"Started with {model_name}",
                        }
                        execution_status["details"]["model_used"] = model_name
                        update_event_log()

                    elif event_type == "content":
                        content = data.get("content", "")
                        if content and isinstance(content, str):
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")

                        # Handle thinking content
                        thinking = data.get("thinking")
                        if thinking:
                            execution_status["details"]["thinking_content"] = thinking

                    elif event_type == "run_completed":
                        # Mark the last step as completed
                        if event_steps and not event_steps[-1]["completed"]:
                            event_steps[-1]["completed"] = True
                            event_steps[-1]["duration"] = (
                                current_time - event_steps[-1]["start_time"]
                            )

                        event_steps.append(
                            {
                                "title": "Execution completed successfully",
                                "details": "Response generation finished",
                                "completed": True,
                                "start_time": current_time,
                                "duration": 0,
                            }
                        )

                        execution_status["run_status"] = {
                            "type": "success",
                            "message": "Execution Completed",
                        }
                        content = data.get("content", "")
                        if content and isinstance(content, str):
                            full_response += content

                        # Show final reasoning if available
                        reasoning = data.get("reasoning_content")
                        if reasoning:
                            if not execution_status["details"]["thinking_content"]:
                                execution_status["details"]["thinking_content"] = (
                                    reasoning
                                )

                        update_event_log()

                    elif event_type == "run_error":
                        error_msg = data.get("error_message", "Unknown error")
                        event_steps.append(
                            {
                                "title": "❌ Error occurred",
                                "details": error_msg,
                                "completed": True,
                                "start_time": current_time,
                                "duration": 0,
                            }
                        )
                        execution_status["run_status"] = {
                            "type": "error",
                            "message": f"Error: {error_msg}",
                        }
                        full_response = f"**Error**: {error_msg}"
                        update_event_log()

                    elif event_type == "run_cancelled":
                        reason = data.get("reason", "No reason provided")
                        event_steps.append(
                            {
                                "title": "⏹️ Execution cancelled",
                                "details": reason,
                                "completed": True,
                                "start_time": current_time,
                                "duration": 0,
                            }
                        )
                        execution_status["run_status"] = {
                            "type": "warning",
                            "message": f"Cancelled: {reason}",
                        }
                        update_event_log()

                    elif event_type == "run_paused":
                        tools = data.get("tools", [])
                        event_steps.append(
                            {
                                "title": "⏸️ Execution paused",
                                "details": f"{len(tools)} tools need confirmation",
                                "completed": False,
                                "start_time": current_time,
                            }
                        )
                        execution_status["run_status"] = {
                            "type": "warning",
                            "message": f"Paused ({len(tools)} tools need confirmation)",
                        }
                        update_event_log()

                    elif event_type == "run_continued":
                        if event_steps and not event_steps[-1]["completed"]:
                            event_steps[-1]["completed"] = True
                            event_steps[-1]["duration"] = (
                                current_time - event_steps[-1]["start_time"]
                            )
                        event_steps.append(
                            {
                                "title": "▶️ Execution resumed",
                                "details": "Continuing with approved actions",
                                "completed": True,
                                "start_time": current_time,
                                "duration": 0,
                            }
                        )
                        update_event_log()

                    elif event_type == "reasoning_started":
                        event_steps.append(
                            {
                                "title": "🧠 Starting reasoning process",
                                "details": "Analyzing and planning response",
                                "completed": False,
                                "start_time": current_time,
                            }
                        )
                        execution_status["reasoning_status"] = {
                            "type": "info",
                            "message": "Reasoning Active",
                        }
                        update_event_log()

                    elif event_type == "reasoning_step":
                        execution_status["details"]["reasoning_steps"] += 1
                        content = data.get("content", "")

                        # Update current reasoning step
                        if (
                            event_steps
                            and "reasoning" in event_steps[-1]["title"].lower()
                        ):
                            event_steps[-1]["details"] = (
                                f"Step {execution_status['details']['reasoning_steps']}: Processing..."
                            )
                        else:
                            event_steps.append(
                                {
                                    "title": f"🧠 Reasoning step {execution_status['details']['reasoning_steps']}",
                                    "details": "Processing logical connections",
                                    "completed": False,
                                    "start_time": current_time,
                                }
                            )

                        if content and isinstance(content, str):
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")

                        update_event_log()

                    elif event_type == "reasoning_completed":
                        # Mark reasoning as completed
                        for step in reversed(event_steps):
                            if (
                                "reasoning" in step["title"].lower()
                                and not step["completed"]
                            ):
                                step["completed"] = True
                                step["duration"] = current_time - step["start_time"]
                                step["details"] = (
                                    f"Completed {execution_status['details']['reasoning_steps']} reasoning steps"
                                )
                                break

                        execution_status["reasoning_status"] = {
                            "type": "success",
                            "message": f"Reasoning Complete ({execution_status['details']['reasoning_steps']} steps)",
                        }
                        update_event_log()

                    elif event_type == "tool_call_started":
                        tool = data.get("tool")
                        if tool and isinstance(tool, dict):
                            tool_name = tool.get("name", "Unknown Tool")
                            current_tool = {
                                "name": tool_name,
                                "started_at": current_time,
                                "result_preview": None,
                            }
                            active_tools.append(tool_name)

                            event_steps.append(
                                {
                                    "title": f"🔧 Using tool: {tool_name}",
                                    "details": "Executing tool function",
                                    "completed": False,
                                    "start_time": current_time,
                                }
                            )
                            update_event_log()

                    elif event_type == "tool_call_completed":
                        tool = data.get("tool")
                        result = data.get("result")
                        if tool and isinstance(tool, dict) and current_tool:
                            tool_name = tool.get("name", "Unknown Tool")
                            if tool_name in active_tools:
                                active_tools.remove(tool_name)

                            # Store tool information
                            current_tool["result_preview"] = (
                                result[:100] + "..."
                                if result and len(result) > 100
                                else result
                            )
                            execution_status["tools_used"].append(current_tool)

                            # Mark tool as completed
                            for step in reversed(event_steps):
                                if (
                                    f"tool: {tool_name}" in step["title"].lower()
                                    and not step["completed"]
                                ):
                                    step["completed"] = True
                                    step["duration"] = current_time - step["start_time"]
                                    step["details"] = (
                                        "Tool execution completed successfully"
                                    )
                                    break

                            current_tool = None
                            update_event_log()

                    elif event_type == "memory_update_started":
                        event_steps.append(
                            {
                                "title": "💾 Updating memory",
                                "details": "Storing conversation context",
                                "completed": False,
                                "start_time": current_time,
                            }
                        )
                        execution_status["memory_status"] = {
                            "type": "info",
                            "message": "Memory Update Active",
                        }
                        update_event_log()

                    elif event_type == "memory_update_completed":
                        # Mark memory update as completed
                        for step in reversed(event_steps):
                            if (
                                "memory" in step["title"].lower()
                                and not step["completed"]
                            ):
                                step["completed"] = True
                                step["duration"] = current_time - step["start_time"]
                                step["details"] = "Memory updated successfully"
                                break

                        execution_status["memory_status"] = {
                            "type": "success",
                            "message": "Memory Updated",
                        }
                        update_event_log()

                    elif event_type == "unknown":
                        # Handle unknown events gracefully
                        raw_content = data.get("raw_content")
                        if raw_content and isinstance(raw_content, str):
                            full_response += raw_content
                            message_placeholder.markdown(full_response + "▌")

                # Calculate final execution time
                execution_status["details"]["execution_time"] = time.time() - start_time

                # Store event log in execution status for persistence
                execution_status["event_log"] = event_steps

                # Final event log update with completion time
                if event_steps:
                    # Mark any remaining incomplete steps as completed
                    for step in event_steps:
                        if not step["completed"]:
                            step["completed"] = True
                            step["duration"] = time.time() - step["start_time"]

                    # Add final summary
                    event_steps.append(
                        {
                            "title": "🎉 All processing completed",
                            "details": f"Total execution time: {execution_status['details']['execution_time']:.2f}s",
                            "completed": True,
                            "start_time": time.time(),
                            "duration": 0,
                        }
                    )
                    update_event_log()

            except Exception as e:
                error_msg = f"**Streaming Error**: {str(e)}"
                message_placeholder.markdown(error_msg)

                event_steps.append(
                    {
                        "title": "❌ Processing failed",
                        "details": str(e),
                        "completed": True,
                        "start_time": time.time(),
                        "duration": 0,
                    }
                )

                execution_status["run_status"] = {
                    "type": "error",
                    "message": f"Stream Failed: {str(e)}",
                }
                execution_status["details"]["execution_time"] = time.time() - start_time
                execution_status["event_log"] = event_steps
                full_response = error_msg
                update_event_log()

            return full_response, execution_status

    def run_app(self):
        """Main application loop"""
        # Page configuration
        st.set_page_config(
            page_title="DSA Notes Agent",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Main title and description
        st.title("🧠 DSA Notes Agent")
        st.markdown("""
        **Your personal assistant for creating organized Data Structures & Algorithms notes!**
        
        This agent helps you create comprehensive notes for coding problems you solve on platforms like LeetCode, HackerRank, and more.
        """)

        # Setup sidebar and get configuration
        config = self.setup_sidebar()

        # Display existing messages
        self.display_chat_messages()

        # Chat input
        if user_message := st.chat_input(
            "Tell me about a problem you solved or need help with..."
        ):
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": user_message})

            # Display user message
            with st.chat_message("user"):
                st.markdown(user_message)

            # Get agent and generate response
            agent = self.get_agent(config["model"], config["debug_mode"])

            # Stream the response
            full_response, execution_status = asyncio.run(
                self.stream_response(agent, user_message, config["show_events"])
            )

            # Add assistant response to session state with execution status
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "execution_status": execution_status,
                }
            )


def main():
    """Main function to run the Streamlit app"""
    try:
        app = StreamlitDSAAgent()
        app.run_app()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.markdown("Please check the console for detailed error information.")


if __name__ == "__main__":
    main()
