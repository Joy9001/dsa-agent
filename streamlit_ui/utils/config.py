"""
Configuration settings for the Streamlit DSA Agent
"""

# Model options
MODEL_OPTIONS = ["gemini-2.5-flash", "gemini-2.5-pro"]
DEFAULT_MODEL = "gemini-2.5-flash"

# UI Configuration
PAGE_TITLE = "DSA Notes Agent"
PAGE_ICON = "🧠"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Default Settings
DEFAULT_DEBUG_MODE = True
DEFAULT_SHOW_EVENTS = False

# Chat Configuration
CHAT_INPUT_PLACEHOLDER = "Tell me about a problem you solved or need help with..."

# Instructions
USAGE_INSTRUCTIONS = """
1. **Problem Solved**: Mention when you've solved a coding problem
2. **Platform**: Specify the platform (e.g., LeetCode, HackerRank)
3. **Problem Details**: Share problem number or name
4. **Notes Creation**: The agent will help create organized notes

**Example Messages:**
- "I solved LeetCode problem #1 Two Sum"
- "Help me create notes for the binary search problem I just solved"
- "I completed problem 206 on LeetCode about reversing a linked list"
"""

# UI Messages
MAIN_DESCRIPTION = """
**Your personal assistant for creating organized Data Structures & Algorithms notes!**

This agent helps you create comprehensive notes for coding problems you solve on platforms like LeetCode, HackerRank, and more.
"""
