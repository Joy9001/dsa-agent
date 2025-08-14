import base64
import json

import dsa_agent.config as cfg


def get_smithery_url(base_url: str, config: dict, api_key: str, profile: str):
    config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
    url = f"{base_url}?config={config_b64}&api_key={api_key}&profile={profile}"
    return url


LC_MCP_URL = get_smithery_url(
    base_url=cfg.LC_MCP_BASE_URL,
    config={
        "site": cfg.LC_SITE,
        "session": cfg.LC_SESSION,
    },
    api_key=cfg.SMITHERY_API_KEY,
    profile=cfg.SMITHERY_PROFILE,
)
GH_MCP_URL = get_smithery_url(
    base_url=cfg.GH_MCP_BASE_URL,
    config={"githubPersonalAccessToken": cfg.GH_TOKEN},
    api_key=cfg.SMITHERY_API_KEY,
    profile=cfg.SMITHERY_PROFILE,
)
