from decouple import config

PG_CONN_STR = config("PG_CONN_STR")

GEMINI_API_KEY = config("GEMINI_API_KEY")

LC_MCP_BASE_URL=config("LC_MCP_BASE_URL", default="https://server.smithery.ai/@jinzcdev/leetcode-mcp-server/mcp")
LC_SITE = config("LC_SITE", default="global")
LC_SESSION = config("LC_SESSION")
SMITHERY_API_KEY = config("SMITHERY_API_KEY")
SMITHERY_PROFILE = config("SMITHERY_PROFILE")
GH_MCP_BASE_URL=config("GH_MCP_BASE_URL", default="https://server.smithery.ai/@smithery-ai/github/mcp")
GH_TOKEN = config("GH_TOKEN")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
