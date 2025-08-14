# DSA Agent

A powerful AI-powered agent specialized in creating structured, educational notes for Data Structures and Algorithms (DSA) problems. The agent automatically detects when you've solved coding problems and helps generate organized markdown notes that are perfect for review and learning.

## 🌟 Key Features

- **Intelligent Problem Detection**: Automatically identifies coding problems from platforms like LeetCode, HackerRank, and Codeforces
- **Structured Note Generation**: Creates comprehensive, review-friendly markdown notes following a consistent template
- **GitHub Integration**: Automatically organizes and stores notes in GitHub repositories
- **Multi-Platform Support**: Works with various coding platforms
- **Memory & Session Management**: Maintains conversation history and learns from interactions
- **Real-time Streaming**: Provides streaming responses for immediate feedback
- **FastAPI REST API**: Complete HTTP API for integration with other tools
- **Comprehensive Logging**: Detailed monitoring and performance tracking

## 🏗️ Architecture

The DSA Agent is built on a modern, scalable architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API    │    │  Direct Python │
│                 │    │                  │    │   Integration   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      DSA Agent          │
                    │   (Agno Framework)      │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────▼─────┐        ┌──────▼──────┐        ┌─────▼─────┐
    │    MCP    │        │   Memory    │        │  Storage  │
    │   Tools   │        │ (Postgres)  │        │(Postgres) │
    └───────────┘        └─────────────┘        └───────────┘
          │
    ┌─────▼─────┐
    │ LeetCode  │
    │  GitHub   │
    └───────────┘
```

### Core Components

- **[Agno Framework](https://github.com/phidatahq/phidata)**: Modern AI agent framework providing the foundation
- **Google Gemini**: Primary language model (gemini-2.5-flash)
- **MCP (Model Context Protocol)**: Tool integration for LeetCode and GitHub APIs
- **PostgreSQL**: Persistent storage for memory and session data
- **FastAPI**: REST API interface
- **Rich Logging**: Advanced logging and monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Google Gemini API key
- GitHub Personal Access Token
- LeetCode session (for LeetCode integration)
- Smithery API access (for MCP tools)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd dsa-agent
   ```

2. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using uv (recommended)
   uv sync
   
   # Or install as editable package
   pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env  # Create this file based on config requirements
   ```

   Required environment variables:
   ```bash
   # Database
   PG_CONN_STR=postgresql://user:password@localhost:5432/dsa_agent
   
   # AI Model
   GEMINI_API_KEY=your_gemini_api_key
   
   # MCP Tools (Smithery.ai)
   SMITHERY_API_KEY=your_smithery_api_key
   SMITHERY_PROFILE=your_profile
   
   # LeetCode Integration
   LC_SESSION=your_leetcode_session_cookie
   LC_SITE=global  # or 'cn' for leetcode.cn
   LC_MCP_BASE_URL=https://server.smithery.ai/@jinzcdev/leetcode-mcp-server/mcp
   
   # GitHub Integration  
   GH_TOKEN=your_github_personal_access_token
   GH_MCP_BASE_URL=https://server.smithery.ai/@smithery-ai/github/mcp
   
   # Logging
   LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
   ```

4. **Set up the database:**
   ```bash
   # Ensure PostgreSQL is running and create the database
   createdb dsa_agent
   ```

5. **Run the API server:**
   ```bash
   # From the project root
   cd dsa_agent
   
   # Make sure uvicorn is available (should be installed with FastAPI)
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using Python module syntax
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Interactive UI: See the `streamlit_ui` directory

## 📁 Project Structure

```
dsa_agent/
├── agent/                    # Core agent implementation
│   ├── dsa_agent.py         # Main DSAAgent class
│   ├── prompt.py            # Agent instructions and behavior
│   ├── memory.py            # Memory and storage configuration
│   └── mcp_url.py           # MCP tool URL configuration
├── api/                     # FastAPI web interface
│   ├── main.py              # FastAPI application
│   ├── settings.py          # API configuration
│   └── routes/              # API route definitions
│       ├── v1_router.py     # Version 1 API router
│       └── agent.py         # Agent interaction endpoints
├── db/                      # Database utilities
│   └── get_db.py            # Database connection helper
├── config.py                # Environment configuration
├── logger.py                # Rich logging setup
└── monitor.py               # Performance monitoring
```

## 🤖 Core Components Deep Dive

### DSAAgent Class (`agent/dsa_agent.py`)

The heart of the system, the `DSAAgent` class provides:

```python
# From within the dsa_agent directory
from agent.dsa_agent import DSAAgent

# Initialize the agent
agent = DSAAgent(
    user_id="your_user_id",
    session_id="session_123", 
    model_id="gemini-2.5-flash",
    debug_mode=True
)

# Streaming interaction
async for event in agent.astream_agent("I solved LeetCode problem #1 Two Sum"):
    print(event)

# Non-streaming interaction  
response = await agent.arun_agent("Create notes for problem #206 Reverse Linked List")
```

**Key Features:**
- Async streaming and non-streaming modes
- Memory persistence across sessions
- Tool integration (LeetCode, GitHub)
- Comprehensive event handling
- Performance monitoring

### Agent Prompt System (`agent/prompt.py`)

Defines the agent's behavior and instructions:

```python
AGENT_DESCRIPTION = """
You are a DSA Notes Agent that helps users create and manage 
organized notes for Data Structures and Algorithms problems 
they solve on coding platforms like LeetCode.
"""

AGENT_INSTRUCTION = """
**Your Workflow:**
1. Detect Problem Context: Identify problem details
2. Repository Check: Verify GitHub repo exists  
3. Repo Initialization: Create template if needed
4. Note Generation: Create comprehensive markdown notes
5. Organize and Upload: Push to appropriate folder
"""
```

### Memory & Storage (`agent/memory.py`)

Persistent conversation and session management:

```python
# Memory for learning from conversations
agent_memory = Memory(
    model=Gemini(id="gemini-2.5-flash", api_key=GEMINI_API_KEY),
    db=PostgresMemoryDb(table_name="user_memories", db_url=db_url)
)

# Storage for session history
agent_storage = PostgresStorage(table_name="agent_sessions", db_url=db_url)
```

### MCP Tool Integration (`agent/mcp_url.py`)

Model Context Protocol tools for external API access:

- **LeetCode MCP**: Fetches problem details, submissions, user stats
- **GitHub MCP**: Creates repos, manages files, organizes folders

## 🔌 API Usage

### REST API Endpoints

**Start Agent Interaction:**
```bash
POST /v1/agents/{agent_id}/runs
Content-Type: application/json

{
  "message": "I solved problem #1 Two Sum on LeetCode",
  "stream": true,
  "model": "gemini-2.5-flash", 
  "user_id": "user123",
  "session_id": "session456"
}
```

**Streaming Response:**
```bash
# Returns Server-Sent Events stream
curl -X POST "http://localhost:8000/v1/agents/dsa/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me create notes for Binary Search problem",
    "stream": true,
    "user_id": "demo_user",
    "session_id": "demo_session"
  }'
```

**Non-Streaming Response:**
```bash
curl -X POST "http://localhost:8000/v1/agents/dsa/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help organizing my LeetCode solutions",
    "stream": false,
    "user_id": "demo_user",
    "session_id": "demo_session"
  }'
```

### Python SDK Usage

**Option 1: Direct Import (from dsa_agent directory)**
```python
import asyncio
import os

# Change to the dsa_agent directory
os.chdir('dsa_agent')  # or navigate to the dsa_agent directory

from agent.dsa_agent import DSAAgent

async def main():
    agent = DSAAgent(
        user_id="your_user_id",
        session_id="session_id"
    )
    
    # For study session notes
    response = await agent.arun_agent(
        "I just solved LeetCode #206 Reverse Linked List using iterative approach"
    )
    print(response)
    
    # For streaming interaction
    async for event in agent.astream_agent(
        "Create notes for Binary Tree problems I solved today"
    ):
        if event.get("event") == "content":
            print(event["data"]["content"])

asyncio.run(main())
```

**Option 2: Package Installation (if installed with `pip install -e .`)**
```python
import asyncio
from dsa_agent.agent.dsa_agent import DSAAgent

async def main():
    agent = DSAAgent(
        user_id="your_user_id",
        session_id="session_id"
    )
    
    # Your agent interactions here...

asyncio.run(main())
```

## 🛠️ Development

### Adding New Features

1. **Custom Prompts**: Modify `agent/prompt.py` to change agent behavior
2. **New Tools**: Extend MCP configuration in `agent/mcp_url.py`
3. **API Endpoints**: Add routes in `api/routes/`
4. **Memory**: Customize storage in `agent/memory.py`

### Performance Monitoring

The agent includes built-in performance monitoring:

```python
# From within the dsa_agent directory
from monitor import time_component

@time_component("database")
def my_database_function():
    # Function will be automatically timed
    pass
```

### Logging Configuration

Rich logging is pre-configured:

```python
# From within the dsa_agent directory
from logger import logger

logger.info("Agent started")
logger.debug("Detailed debug info") 
logger.error("Error occurred")
```

Log levels can be controlled via the `LOG_LEVEL` environment variable.

## 📊 Event Handling

The agent provides comprehensive event streaming for real-time monitoring:

- **Run Events**: `run_started`, `run_completed`, `run_error`
- **Content Events**: `content_delta`, `content_done`  
- **Reasoning Events**: `reasoning_started`, `reasoning_step`, `reasoning_completed`
- **Tool Events**: `tool_call_started`, `tool_call_completed`
- **Memory Events**: `memory_created`, `memory_updated`

See `docs/EVENT_HANDLING.md` for detailed documentation.

## 🎯 Example Use Cases

### 1. Problem Note Creation
```
User: "I solved LeetCode #1 Two Sum"
Agent: Creates structured note with:
- Problem description and constraints
- Solution approach and complexity analysis  
- Code implementation with comments
- Key insights and patterns
- Related problems and follow-ups
```

### 2. Study Session Organization
```
User: "I completed 5 binary tree problems today"
Agent: 
- Fetches all problem details
- Creates individual notes for each
- Organizes in GitHub repo structure
- Updates progress tracking
```

### 3. Interview Preparation
```
User: "Help me review all my graph problems"
Agent:
- Analyzes existing notes
- Identifies knowledge gaps
- Suggests practice problems
- Creates study schedule
```

## 🖥️ User Interface

A Streamlit-based web interface is available in the `streamlit_ui/` directory for easy interaction with the agent. The UI provides a chat interface, session management, and real-time streaming responses.

To run the UI:
```bash
cd streamlit_ui
streamlit run app.py
```

See `streamlit_ui/README.md` for detailed UI documentation.

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Errors:**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify connection string
echo $PG_CONN_STR
```

**2. API Key Issues:**
```bash
# Verify Gemini API key
echo $GEMINI_API_KEY

# Test API access
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

**3. MCP Tool Errors:**
- Verify Smithery API key and profile
- Check LeetCode session cookie validity
- Ensure GitHub token has required permissions

**4. Import Errors:**
```bash
# Ensure you're in the correct directory
cd dsa_agent
python -c "from agent.dsa_agent import DSAAgent; print('Import successful')"
```

### Debug Mode

Enable detailed logging:
```python
agent = DSAAgent(debug_mode=True)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support information here]

---

**Built with ❤️ using [Agno](https://github.com/phidatahq/phidata) framework**