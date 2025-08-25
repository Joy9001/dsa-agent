"""
Session management utilities for Streamlit DSA Agent
"""

import uuid
from typing import Any, Dict

import streamlit as st

from utils.gen_userid import generate_user_id


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_id" not in st.session_state:
        st.session_state.user_id = None  # Will be set when config is available

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "agent" not in st.session_state:
        st.session_state.agent = None


def update_user_id(config: Dict[str, Any]):
    """Update user ID based on current configuration"""
    new_user_id = generate_user_id(config)

    if st.session_state.user_id != new_user_id:
        st.session_state.user_id = new_user_id


def reset_session():
    """Reset session state for a new conversation"""
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.agent = None


def clear_execution_status():
    """Clear execution status from all messages"""
    for message in st.session_state.messages:
        if "execution_status" in message:
            del message["execution_status"]


def get_session_statistics() -> Dict[str, Any]:
    """Calculate and return session statistics"""
    assistant_messages = [
        msg for msg in st.session_state.messages if msg["role"] == "assistant"
    ]

    if not assistant_messages:
        return {}

    total_tools = 0
    total_events = 0
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

    avg_execution_time = (
        sum(valid_executions) / len(valid_executions) if valid_executions else 0
    )

    return {
        "total_messages": len(st.session_state.messages),
        "total_responses": len(assistant_messages),
        "total_tools": total_tools,
        "total_events": total_events,
        "avg_execution_time": avg_execution_time,
    }
