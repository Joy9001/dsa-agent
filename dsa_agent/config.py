from decouple import config

DB_DRIVER = config("DB_DRIVER", default="postgresql+psycopg")
DB_USER = config("DB_USER", default="postgres")
DB_PASS = config("DB_PASS")
DB_HOST = config("DB_HOST", default="localhost")
DB_PORT = config("DB_PORT", default="5432")
DB_DATABASE = config("DB_DATABASE", default="dsa_agent")

GEMINI_API_KEY = config("GEMINI_API_KEY")

LC_SITE = config("LC_SITE", default="global")
LC_SESSION = config("LC_SESSION")
SMITHERY_API_KEY = config("SMITHERY_API_KEY")
SMITHERY_PROFILE = config("SMITHERY_PROFILE")
GH_TOKEN = config("GH_TOKEN")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
