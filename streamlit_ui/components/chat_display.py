"""
Chat display component for Streamlit DSA Agent
"""

import streamlit as st


def display_chat_messages():
    """Display existing chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Show event log if available
                if "execution_status" in message and "event_log" in message["execution_status"]:
                    _display_event_log(message["execution_status"]["event_log"])

                # Show message content
                st.markdown(message["content"])
            else:
                # Display user messages normally
                st.markdown(message["content"])


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
