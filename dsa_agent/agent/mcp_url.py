import base64
import json


def get_smithery_url(base_url: str, config: dict, api_key: str, profile: str):
    config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
    url = f"{base_url}?config={config_b64}&api_key={api_key}&profile={profile}"
    return url


