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
**Quick Setup:**
1. Add your Gemini API key
2. Add your LeetCode session token
3. Add your GitHub personal access token

**How to Use:**
Just tell me about any LeetCode problem you've solved! I'll automatically:
- Create organized notes in markdown format
- Set up a GitHub repository if needed
- Save everything with proper naming and structure

**Examples:**
- "I solved LeetCode #1 Two Sum"
- "Help me create notes for problem 206 Reverse Linked List"
- "Just completed Binary Search problem #704"

That's it! 🚀
"""

# UI Messages
MAIN_DESCRIPTION = """
**Your personal assistant for creating organized Data Structures & Algorithms notes!**

This agent helps you create comprehensive notes for coding problems you solve on platforms like LeetCode, HackerRank, and more.
"""
