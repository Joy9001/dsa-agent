import hashlib
from typing import Any


def generate_user_id(config: dict[str, Any]) -> str:
    """Generate a unique user ID based on user configurations"""
    # Create a string from the configuration values
    config_string = f"{config.get('lc_session', '')}-{config.get('gh_token', '')}"

    # Create a hash of the configuration
    config_hash = hashlib.md5(config_string.encode()).hexdigest()[:12]

    # Return a user-friendly ID
    return f"user-{config_hash}"
