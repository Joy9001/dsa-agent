import config as cfg


def get_db_url() -> str:
    db_driver = cfg.DB_DRIVER
    db_user = cfg.DB_USER
    db_pass = cfg.DB_PASS
    db_host = cfg.DB_HOST
    db_port = cfg.DB_PORT
    db_database = cfg.DB_DATABASE
    return "{}://{}{}@{}:{}/{}".format(
        db_driver,
        db_user,
        f":{db_pass}" if db_pass else "",
        db_host,
        db_port,
        db_database,
    )
