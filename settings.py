import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, 'config.env')

load_dotenv(dotenv_path=env_path)


# Only these variables are allowed to be exposed
ALLOWED_KEYS = {
    "HOST",
    "CARDAPP_PORT",
    "CUSTINFO_PORT",
    "CREDITSCAN_PORT",
    "FRAUDRISK_PORT",
    "APPID_PORT",
    "SIGNIN_PORT",
    "CREDITSCAN_KEY",
    "FRAUDRISK_KEY",
    "CUSTINFO_KEY",
    "APPID_KEY",
    "SIGNIN_KEY",
}


def _cast(value):
    if value is None:
        return None
    if isinstance(value, str) and value.isdigit():
        return int(value)
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


# Build a clean config namespace
CONFIG = {}

for key in ALLOWED_KEYS:
    if key in os.environ:
        CONFIG[key] = _cast(os.environ[key])