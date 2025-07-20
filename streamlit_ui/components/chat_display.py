"""
Chat display component for Streamlit DSA Agent
"""

import streamlit as st


def display_chat_messages():
    """Display existing chat messages with persistent status information"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Display persistent execution status for assistant messages
            if message["role"] == "assistant" and "execution_status" in message:
                # Show event log if available
                if "event_log" in message["execution_status"]:
                    _display_event_log(message["execution_status"]["event_log"])

                # Show message content
                st.markdown(message["content"])
                
                st.divider()
                
                _display_execution_status(message["execution_status"], message)
            else:
                # Display user messages normally
                st.markdown(message["content"])


def _display_execution_status(execution_status: dict, message: dict):
    """Display execution status information for a message"""



    # Create compact status display in columns
    _display_status_columns(execution_status)

    # Show execution details
    _display_execution_details(execution_status, message)


def _display_event_log(event_steps: list):
    """Display event log steps"""
    with st.expander("🔄 Processing Steps", expanded=False):
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


def _display_status_columns(execution_status: dict):
    """Display status information in columns"""
    status_cols = st.columns([2, 2, 2, 2])

    with status_cols[0]:
        _display_run_status(execution_status.get("run_status"))

    with status_cols[1]:
        _display_reasoning_status(execution_status.get("reasoning_status"))

    with status_cols[2]:
        _display_tools_status(execution_status.get("tools_used", []))

    with status_cols[3]:
        _display_memory_status(execution_status.get("memory_status"))


def _display_run_status(run_info: dict):
    """Display run status"""
    if run_info:
        if run_info["type"] == "success":
            st.success(run_info["message"], icon="✅")
        elif run_info["type"] == "error":
            st.error(run_info["message"], icon="❌")
        elif run_info["type"] == "warning":
            st.warning(run_info["message"], icon="⚠️")
        else:
            st.info(run_info["message"], icon="ℹ️")


def _display_reasoning_status(reasoning_info: dict):
    """Display reasoning status"""
    if reasoning_info:
        if reasoning_info["type"] == "success":
            st.success(reasoning_info["message"], icon="🧠")
        else:
            st.info(reasoning_info["message"], icon="🧠")


def _display_tools_status(tools_info: list):
    """Display tools status"""
    if tools_info:
        st.success(f"{len(tools_info)} tool(s)", icon="🔧")
    else:
        st.caption("No tools used")


def _display_memory_status(memory_info: dict):
    """Display memory status"""
    if memory_info:
        if memory_info["type"] == "success":
            st.success(memory_info["message"], icon="💾")
        else:
            st.info(memory_info["message"], icon="💾")


def _display_execution_details(execution_status: dict, message: dict):
    """Display detailed execution information"""
    execution_details = execution_status.get("details", {})
    if not execution_details:
        return

    detail_cols = st.columns([1, 1, 1, 1])

    with detail_cols[0]:
        if execution_details.get("total_events"):
            st.metric(
                "Events",
                execution_details["total_events"],
                label_visibility="visible",
            )

    with detail_cols[1]:
        if execution_details.get("execution_time"):
            st.metric(
                "Time (s)",
                f"{execution_details['execution_time']:.2f}",
                label_visibility="visible",
            )

    with detail_cols[2]:
        if execution_details.get("reasoning_steps"):
            st.metric(
                "Reasoning",
                execution_details["reasoning_steps"],
                label_visibility="visible",
            )

    with detail_cols[3]:
        if execution_details.get("model_used"):
            st.caption(f"Model: {execution_details['model_used']}")

    # Show additional details in expandable sections
    _display_expandable_details(execution_status, execution_details, message)


def _display_expandable_details(
    execution_status: dict, execution_details: dict, message: dict
):
    """Display expandable detail sections"""
    tools_info = execution_status.get("tools_used", [])
    expandable_sections = []

    if tools_info:
        expandable_sections.append("tools")
    if execution_details.get("thinking_content"):
        expandable_sections.append("thinking")

    if not expandable_sections:
        return

    expand_cols = st.columns(len(expandable_sections))
    col_idx = 0

    if "tools" in expandable_sections:
        with expand_cols[col_idx]:
            with st.expander("🔧 Tools Details", expanded=False):
                for tool_info in tools_info:
                    st.write(f"**{tool_info['name']}**")
                    if tool_info.get("result_preview"):
                        st.caption(f"Result: {tool_info['result_preview']}")
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
