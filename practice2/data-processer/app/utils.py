import logging
import os

def pass_or_die(env: str) -> str:
    if os.getenv(env, None) is None:
        logging.fatal(f"Environment {env} is not provided!")
        exit(1)
    return os.environ[env]