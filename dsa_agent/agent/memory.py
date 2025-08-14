from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from dsa_agent.db.get_db import get_db_url

import dsa_agent.config as cfg

db_url = get_db_url()

# Initialize memory.v2
agent_memory = Memory(
    # Use any model for creating memories
    model=Gemini(id="gemini-2.5-flash", api_key=cfg.GEMINI_API_KEY),
    db=PostgresMemoryDb(table_name="user_memories", db_url=db_url),
)

# Initialize storage
agent_storage = PostgresStorage(table_name="agent_sessions", db_url=db_url)
