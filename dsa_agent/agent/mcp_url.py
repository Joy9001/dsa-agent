import base64
import json

import config as cfg


def get_lc_url():
    lc_mcp_base_url = "https://server.smithery.ai/@jinzcdev/leetcode-mcp-server/mcp"
    config = {
        "site": cfg.LC_SITE,
        "session": cfg.LC_SESSION,
    }
    config_b64 = base64.b64encode(json.dumps(config).encode()).decode()

    url = f"{lc_mcp_base_url}?config={config_b64}&api_key={cfg.SMITHERY_API_KEY}&profile={cfg.SMITHERY_PROFILE}"
    return url


def get_gh_url():
    gh_mcp_base_url = "https://server.smithery.ai/@smithery-ai/github/mcp"
    config = {"githubPersonalAccessToken": cfg.GH_TOKEN}
    config_b64 = base64.b64encode(json.dumps(config).encode()).decode()

    url = f"{gh_mcp_base_url}?config={config_b64}&api_key={cfg.SMITHERY_API_KEY}&profile={cfg.SMITHERY_PROFILE}"
    return url

LC_MCP_URL = get_lc_url()
GH_MCP_URL = get_gh_url()