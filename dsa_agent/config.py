from decouple import config

PG_CONN_STR = config("PG_CONN_STR")

GEMINI_API_KEY = config("GEMINI_API_KEY")

LC_SITE = config("LC_SITE", default="global")
LC_SESSION = config("LC_SESSION")
SMITHERY_API_KEY = config("SMITHERY_API_KEY")
SMITHERY_PROFILE = config("SMITHERY_PROFILE")
GH_TOKEN = config("GH_TOKEN")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
