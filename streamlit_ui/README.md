# DSA Notes Agent - Streamlit UI

A beautiful and interactive web interface for the DSA Notes Agent, built with Streamlit.

## 🌟 Features

- **Interactive Chat Interface**: Chat with your DSA Notes Agent in real-time
- **Streaming Responses**: See responses as they're generated
- **Session Management**: Start new sessions, maintain conversation history
- **Model Configuration**: Choose different AI models and settings
- **Problem Note Creation**: Automatically create organized notes for coding problems
- **Multi-platform Support**: Works with LeetCode, HackerRank, and other coding platforms

## 🚀 Quick Start

### Prerequisites

Make sure you have the main DSA Agent project dependencies installed:

```bash
cd .. && pip install -r requirements.txt
```

### Installation & Running

1. **Navigate to the UI directory:**

   ```bash
   cd streamlit_ui
   ```

2. **Install Streamlit dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 🎯 How to Use

### Basic Usage

1. **Start a Conversation**: Type your message in the chat input at the bottom
2. **Problem Solving**: Tell the agent about problems you've solved
3. **Note Creation**: The agent will help create organized notes for your problems

### Example Messages

- "I solved LeetCode problem #1 Two Sum"
- "Help me create notes for the binary search problem I just solved"
- "I completed problem 206 on LeetCode about reversing a linked list"
- "Create notes for HackerRank's Array Manipulation problem"

### Sidebar Features

- **Model Selection**: Choose between available AI models
- **Debug Mode**: Toggle debug mode for detailed logging
- **New Session**: Start a fresh conversation
- **Session Info**: View current user and session IDs

## 🛠️ Configuration

### Environment Variables

Make sure these are set in your main project (the agent uses them):

- `GEMINI_API_KEY`: Your Google Gemini API key
- `PG_CONN_STR`: Your PostgreSQL connection string
- `LC_SESSION`: Your LeetCode session cookie
- `SMITHERY_API_KEY`: Your Smithery API key
- `SMITHERY_PROFILE`: Your Smithery profile ID
- `GH_TOKEN`: Your GitHub token

### Streamlit Configuration

The UI comes with a pre-configured `.streamlit/config.toml` file with:

- Dark theme
- Optimized server settings
- Custom styling

## 📁 Project Structure

```bash
streamlit_ui/
├── components/            # UI components
├── core/                  # Core App
├── handlers/              # Event Response Handlers
├── utils/                 # Utility functions
├── app.py                 # Main Streamlit application
├── README.md             
├── .streamlit/
│   └── config.toml        # Streamlit configuration
```

## 🔧 Architecture

### Direct Agent Integration

The UI directly imports and uses the `DSAAgent` class from the main project, providing:

- **Better Performance**: No HTTP overhead
- **Real-time Streaming**: Direct access to async generators
- **Session Persistence**: Maintains agent state across interactions
- **Error Handling**: Direct exception handling

### Key Components

1. **StreamlitDSAAgent**: Main application class managing UI state
2. **Session Management**: Handles user sessions and conversation history  
3. **Agent Integration**: Direct interface with the DSA Agent
4. **Streaming Interface**: Real-time response streaming

## 🎨 UI Features

### Chat Interface

- Clean, modern chat interface
- Message history persistence
- Real-time streaming responses
- Error handling and display

### Sidebar Configuration

- Model selection dropdown
- Debug mode toggle
- Session management controls
- Usage instructions and tips

### Visual Elements

- Dark theme optimized for coding
- Syntax highlighting for code blocks
- Responsive design
- Loading indicators

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:

   ```bash
   ImportError: No module named 'agent.agent'
   ```

   **Solution**: Make sure you're running from the `streamlit_ui` directory and the main project dependencies are installed.

2. **Streamlit Not Found**:

   ```bash
   ModuleNotFoundError: No module named 'streamlit'
   ```

   **Solution**: Install UI dependencies: `pip install -r requirements.txt`

3. **API Key Errors**:

   ```bash
   Error: GEMINI_API_KEY not found
   ```

   **Solution**: Set your Gemini API key in the main project's configuration.

### Debug Mode

Enable debug mode in the sidebar to see:

- Detailed agent logging
- Request/response information
- Error stack traces

## 🚀 Development

### Adding New Features

1. **Custom Styling**: Modify `.streamlit/config.toml`
2. **New UI Components**: Add to the `StreamlitDSAAgent` class
3. **Agent Features**: Extend the main DSA Agent and they'll be available here

### Performance Optimization

- The UI reuses agent instances when configuration doesn't change
- Session state is efficiently managed
- Streaming reduces perceived latency

## 📝 Notes

- The UI maintains separate session state from the FastAPI app
- All agent features (memory, storage, MCP tools) are fully available
- The interface is optimized for the DSA note-taking workflow

## 🤝 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure all dependencies are correctly installed
3. Verify your environment variables are set
4. Check the main project documentation

---

**Happy Coding! 🧠✨**
