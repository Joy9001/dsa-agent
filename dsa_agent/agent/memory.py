from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage

from dsa_agent.db.get_db import get_db_url

db_url = get_db_url()


def initialize_agent_memory(api_key: str, model_id: str = "gemini-2.5-flash"):
    """Initialize agent memory with user-provided API key or fallback to config"""

    agent_memory = Memory(
        model=Gemini(id=model_id, api_key=api_key),
        db=PostgresMemoryDb(table_name="user_memories", db_url=db_url),
    )

    return agent_memory


def initialize_agent_storage():
    agent_storage = PostgresStorage(table_name="agent_sessions", db_url=db_url)
    return agent_storage
