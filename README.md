# DSA Agent

A specialized AI agent built with the [Agno framework](https://github.com/agno-agi/agno) that helps users create structured, educational notes for Data Structures and Algorithms (DSA) problems solved on coding platforms like LeetCode.

## 🌟 Key Features

- **Problem Note Generation**: Creates comprehensive, review-friendly markdown notes following a consistent template structure
- **LeetCode Integration**: Connects to LeetCode via MCP (Model Context Protocol) to fetch problem details and submissions
- **GitHub Integration**: Automatically organizes and stores notes in GitHub repositories with proper folder structure
- **Memory & Session Management**: Maintains conversation history and learns from interactions using PostgreSQL storage
- **Streaming & Non-streaming Modes**: Supports both real-time streaming responses and standard request-response patterns
- **FastAPI REST API**: Complete HTTP API for integration with other applications
- **Streamlit Web Interface**: User-friendly web interface for interactive agent usage
- **Rich Logging & Monitoring**: Comprehensive logging with performance tracking and timing decorators

## 🏗️ Architecture

The DSA Agent is built on a modern, event-driven architecture:

```bash
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API    │    │  Direct Python │
│   (Web Client)  │    │   (REST API)     │    │   Integration   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      DSAAgent           │
                    │   (Agno Framework)      │
                    │   Google Gemini Model   │
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
    │ (via MCP) │
    └───────────┘
```

### Core Components

- **[Agno Framework](https://github.com/agno-agi/agno)**: AI agent framework providing the foundation
- **Google Gemini**: Language model (gemini-2.5-flash or gemini-2.5-pro)
- **MCP (Model Context Protocol)**: Tool integration for LeetCode and GitHub APIs via Smithery.ai
- **PostgreSQL**: Persistent storage for agent memory and conversation history
- **FastAPI**: REST API server with streaming support
- **Streamlit**: Interactive web interface
- **Rich Logging**: Performance monitoring with execution time tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Google Gemini API key
- GitHub Personal Access Token
- LeetCode session cookie (for LeetCode integration)
- Smithery.ai API access (for MCP tools)

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

   Create a `.env` file in the root directory with the following variables:

   ```bash
   # Database Connection
   PG_CONN_STR=postgresql://user:password@localhost:5432/dsa_agent
   
   # Logging Level
   LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
   
   # MCP Tools (Smithery.ai) - Required for LeetCode/GitHub integration
   SMITHERY_API_KEY=your_smithery_api_key
   SMITHERY_PROFILE=your_smithery_profile
   
   # Optional: Custom MCP URLs (defaults provided)
   LC_MCP_BASE_URL=https://server.smithery.ai/@jinzcdev/leetcode-mcp-server/mcp
   GH_MCP_BASE_URL=https://server.smithery.ai/@smithery-ai/github/mcp
   ```

4. **Set up the database:**

   ```bash
   # Ensure PostgreSQL is running and create the database
   createdb dsa_agent
   ```

### Running the Application

#### Option 1: FastAPI Server

```bash
# Navigate to the dsa_agent directory
cd dsa_agent

# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API:

- **API Documentation**: <http://localhost:8000/docs>
- **API Endpoint**: POST <http://localhost:8000/v1/agents/run>

#### Option 2: Streamlit Web Interface

```bash
streamlit run streamlit_ui/app.py
```

Access the web interface at: <http://localhost:8501>

## 🛠️ Development

### Performance Monitoring

The agent includes built-in performance monitoring using decorators:

```python
# From within the dsa_agent directory
from monitor import time_component

@time_component("database")
def my_database_function():
    # Function will be automatically timed
    pass

# For async functions
@time_component("api")
async def my_async_function():
    # Async function will be automatically timed
    pass
```

### Logging Configuration

Rich logging is pre-configured in `logger.py`:

```python
# From within the dsa_agent directory
from logger import logger

logger.info("Agent started")
logger.debug("Detailed debug info") 
logger.error("Error occurred")
```

Log levels can be controlled via the `LOG_LEVEL` environment variable (DEBUG, INFO, WARNING, ERROR).

### Configuration Management

Environment variables are managed in `config.py` using python-decouple:

```python
from decouple import config

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
PG_CONN_STR = config("PG_CONN_STR")
SMITHERY_API_KEY = config("SMITHERY_API_KEY")
SMITHERY_PROFILE = config("SMITHERY_PROFILE")
```

### Adding New Features

1. **Custom Prompts**: Modify `agent/prompt.py` to change agent behavior
2. **New MCP Tools**: Extend MCP configuration in `agent/mcp_url.py`
3. **API Endpoints**: Add routes in `api/routes/`
4. **Memory Customization**: Modify storage configuration in `agent/memory.py`
5. **UI Components**: Add Streamlit components in `streamlit_ui/components/`

## 📊 Event Handling

The agent provides comprehensive event streaming for real-time monitoring during execution:

### Event Categories

**Execution Events:**

- `run_started`: Agent execution begins with model and run metadata
- `run_completed`: Agent execution completes with final content
- `run_paused`: Agent execution paused (e.g., waiting for tool results)
- `run_continued`: Agent execution resumed
- `run_error`: Agent execution error with error details
- `run_cancelled`: Agent execution cancelled

**Content Events:**

- `content`: Incremental agent response content during generation

**Reasoning Events:**

- `reasoning_started`: Agent reasoning/thinking process begins
- `reasoning_step`: Individual reasoning step with partial content
- `reasoning_completed`: Reasoning process completes

**Tool Events:**

- `tool_call_started`: MCP tool execution begins
- `tool_call_completed`: MCP tool execution completes with results

**Memory Events:**

- `memory_update_started`: Memory update process begins
- `memory_update_completed`: Memory update process completes

### Event Structure

Each event contains:

```python
{
    "event": "event_type",
    "data": {
        "event_type": "run_started",
        "timestamp": "2025-01-01T00:00:00Z",
        "agent_id": "agent_uuid",
        "run_id": "run_uuid", 
        "session_id": "session_id",
        # Additional event-specific data
        "content": "response content",
        "tool": {"name": "tool_name", "args": "tool_args"},
        "result": "tool_result"
    }
}
```

See the `agent/agent.py` file for detailed event handling implementation.

## 🎯 Example Use Cases

### 1. Problem Note Creation

```bash
User: "I solved LeetCode #1 Two Sum using a hash map approach"

Agent Response:
- Fetches problem details from LeetCode
- Creates structured markdown note with:
  * Problem description and constraints
  * Solution approach and complexity analysis  
  * Code implementation with comments
  * Key insights and patterns
  * Related problems and follow-ups
- Uploads to organized GitHub repository
```

### 2. Interview Preparation

```bash
User: "Help me review my dynamic programming solutions"

Agent Response:
- Analyzes existing notes in the repository
- Identifies knowledge gaps and patterns
- Suggests related problems for practice
- Creates summary notes for quick review
```

### 3. Solution Analysis

```bash
User: "I solved problem #206 Reverse Linked List but want to document it properly"

Agent Response:
- Fetches problem details and user's submission
- Creates comprehensive note with multiple approaches
- Includes time/space complexity analysis
- Adds to appropriate data structure folder
```

## 📞 Support

[Email Me](mailto:joymridha939@gmail.com)

---

**Built with ❤️ using [Agno](https://github.com/agno-agi/agno) framework**
