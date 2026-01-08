import os
from dotenv import load_dotenv

# Load environment variables once when module is imported
load_dotenv()

def get_env_path(env_var, default=None):
    """
    Get a path from an environment variable, expanding user home directory (~).
    """
    path = os.getenv(env_var, default)
    if path:
        return os.path.expanduser(path)
    return None

# Configuration Getters

def get_main_file():
    return get_env_path("BEANCOUNT_MAIN_FILE", "main.bean")

def get_accounts_file():
    return get_env_path("BEANCOUNT_ACCOUNTS_FILE", "accounts.bean")

def get_rules_file():
    return get_env_path("BEANCOUNT_RULES_FILE", "user_rules.yaml")

def get_imports_dir():
    return get_env_path("BEANCOUNT_IMPORTS_DIR", "imports")

def get_ledger_dir():
    return get_env_path("BEANCOUNT_LEDGER_DIR", "ledgers")

def get_archive_dir():
    return get_env_path("BEANCOUNT_ARCHIVE_DIR", "archive")

def get_staging_file():
    return get_env_path("BEANCOUNT_STAGING_FILE", "staging/import.bean")
