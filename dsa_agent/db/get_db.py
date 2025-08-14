import dsa_agent.config as cfg


def get_db_url() -> str:
    return cfg.PG_CONN_STR
