"""
Sidebar component for Streamlit DSA Agent
"""

from typing import Any, Dict

import streamlit as st
from utils.config import (
    DEFAULT_DEBUG_MODE,
    DEFAULT_MODEL,
    DEFAULT_SHOW_EVENTS,
    MODEL_OPTIONS,
    USAGE_INSTRUCTIONS,
)
from utils.session import clear_execution_status, get_session_statistics, reset_session


def setup_sidebar() -> Dict[str, Any]:
    """Setup the sidebar with configuration options"""
    st.sidebar.title("⚙️ Configuration")

    # Model selection
    selected_model = st.sidebar.selectbox(
        "Select Model",
        MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(DEFAULT_MODEL),
        help="Choose the AI model to use for the agent",
    )

    # Debug mode toggle
    debug_mode = st.sidebar.checkbox(
        "Debug Mode",
        value=DEFAULT_DEBUG_MODE,
        help="Enable debug mode for detailed logging and event information",
    )

    # Event monitoring toggle
    show_events = st.sidebar.checkbox(
        "Show Event Details",
        value=DEFAULT_SHOW_EVENTS,
        help="Display detailed event information during agent execution",
    )

    # MCP Configuration
    st.sidebar.subheader("🔗 MCP Configuration")
    
    # LeetCode configuration
    lc_site = st.sidebar.selectbox(
        "LeetCode Site",
        ["global", "cn"],
        index=0,
        help="Select LeetCode site region",
    )
    
    lc_session = st.sidebar.text_input(
        "LeetCode Session",
        type="password",
        help="Enter your LeetCode session token",
        placeholder="LEETCODE_SESSION value from cookies",
    )
    
    # GitHub configuration
    gh_token = st.sidebar.text_input(
        "GitHub Token",
        type="password",
        help="Enter your GitHub personal access token",
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
    )
    
    # Show warnings if credentials are missing
    if not lc_session:
        st.sidebar.warning("⚠️ LeetCode session token is required for LeetCode MCP tools")
    
    if not gh_token:
        st.sidebar.warning("⚠️ GitHub token is required for GitHub MCP tools")

    # Session management
    _setup_session_management()

    # Session info
    _setup_session_info()

    # Instructions
    _setup_instructions()

    return {
        "model": selected_model,
        "debug_mode": debug_mode,
        "show_events": show_events,
        "lc_site": lc_site,
        "lc_session": lc_session,
        "gh_token": gh_token,
    }


def _setup_session_management():
    """Setup session management buttons"""
    st.sidebar.subheader("🔧 Session Management")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 New Session", help="Start a new conversation session"):
            reset_session()
            st.rerun()

    with col2:
        if st.button(
            "🧹 Clear Status", help="Clear execution status from all messages"
        ):
            clear_execution_status()
            st.rerun()


def _setup_session_info():
    """Display current session information"""
    with st.sidebar.expander("📋 Session Info"):
        st.text(f"User ID: {st.session_state.user_id[:8]}...")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")

        # Show session statistics
        stats = get_session_statistics()
        if stats:
            st.text(f"Messages: {stats['total_messages']}")
            st.text(f"Responses: {stats['total_responses']}")

            if stats["total_tools"] > 0:
                st.text(f"Total Tools Used: {stats['total_tools']}")
            if stats["total_events"] > 0:
                st.text(f"Total Events: {stats['total_events']}")
            if stats["avg_execution_time"] > 0:
                st.text(f"Avg Execution Time: {stats['avg_execution_time']:.2f}s")


def _setup_instructions():
    """Display usage instructions"""
    st.sidebar.subheader("📚 How to Use")
    st.sidebar.markdown(USAGE_INSTRUCTIONS)
