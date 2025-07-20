"""
Main entry point for the Streamlit DSA Agent application.

This is the simplified main application file that imports and runs the modular components.
"""

import streamlit as st
from core.app import StreamlitDSAAgent


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
