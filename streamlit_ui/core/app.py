"""
Core application class for Streamlit DSA Agent
"""

import asyncio
from typing import Any, Dict

import streamlit as st
from components.chat_display import display_chat_messages
from components.sidebar import setup_sidebar
from handlers.response_streamer import ResponseStreamer
from utils.config import (
    CHAT_INPUT_PLACEHOLDER,
    LAYOUT,
    MAIN_DESCRIPTION,
    PAGE_ICON,
    PAGE_TITLE,
    SIDEBAR_STATE,
)
from utils.session import initialize_session_state

from dsa_agent.agent import DSAAgent


class StreamlitDSAAgent:
    """Main Streamlit interface for the DSA Agent"""

    def __init__(self):
        self.response_streamer = ResponseStreamer()
        initialize_session_state()

    def get_agent(self, config: Dict[str, Any]) -> DSAAgent:
        """Get or create DSA Agent instance"""
        model = config["model"]
        debug_mode = config["debug_mode"]
        gemini_api_key = config["gemini_api_key"]
        lc_site = config["lc_site"]
        lc_session = config["lc_session"]
        gh_token = config["gh_token"]

        # Create a unique key for the agent configuration
        agent_key = (
            f"{model}_{debug_mode}_{lc_site}_{bool(lc_session)}_{bool(gh_token)}"
        )

        if (
            st.session_state.agent is None
            or st.session_state.get("current_agent_key") != agent_key
        ):
            st.session_state.agent = DSAAgent(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                model_id=model,
                debug_mode=debug_mode,
                lc_site=lc_site,
                lc_session=lc_session,
                gh_token=gh_token,
                gemini_api_key=gemini_api_key,
            )
            st.session_state.current_agent_key = agent_key

        return st.session_state.agent

    def run_app(self):
        """Main application loop"""
        self._setup_page_config()
        self._setup_main_header()

        # Setup sidebar and get configuration
        config = setup_sidebar()

        # Show configuration status in main area
        if not config.get("config_valid", False):
            st.info(
                "👈 **Please complete the configuration in the sidebar before starting.**\n\n"
                "Required configurations:\n"
                "- **Gemini API Key**: Your Google Gemini API key\n"
                "- **LeetCode Session**: Your LeetCode session token from browser cookies\n"
                "- **GitHub Token**: Your GitHub personal access token\n\n"
                "Once all configurations are provided, you can start chatting with the DSA Agent!"
            )

        # Display existing messages
        display_chat_messages()

        # Handle chat input
        self._handle_chat_input(config)

    def _setup_page_config(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title=PAGE_TITLE,
            page_icon=PAGE_ICON,
            layout=LAYOUT,
            initial_sidebar_state=SIDEBAR_STATE,
        )

    def _setup_main_header(self):
        """Setup main page header and description"""
        st.title(f"{PAGE_ICON} {PAGE_TITLE}")
        st.markdown(MAIN_DESCRIPTION)

    def _handle_chat_input(self, config: Dict[str, Any]):
        """Handle user chat input and agent response"""
        # Check if all required configurations are provided
        if not config.get("config_valid", False):
            # Display disabled chat input with helpful message
            st.chat_input(
                "Please provide all required configurations in the sidebar to start chatting...",
                disabled=True,
            )
            return

        if user_message := st.chat_input(CHAT_INPUT_PLACEHOLDER):
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": user_message})

            # Display user message
            with st.chat_message("user"):
                st.markdown(user_message)

            # Get agent and generate response
            agent = self.get_agent(config)

            # Stream the response
            full_response, execution_status = asyncio.run(
                self.response_streamer.stream_response(
                    agent, user_message, config["show_events"]
                )
            )

            # Add assistant response to session state with execution status
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "execution_status": execution_status,
                }
            )
