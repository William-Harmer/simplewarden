import os
from dotenv import dotenv_values, load_dotenv

_env_initialized = False


def load_and_validate_env() -> None:
    global _env_initialized

    load_dotenv()
    values = dotenv_values()

    if not values:
        raise RuntimeError(".env file not found or is empty.")

    missing = [k for k, v in values.items() if not v]
    if missing:
        raise RuntimeError(
            "The following .env variables are missing values: "
            + ", ".join(missing)
        )

    _env_initialized = True


def get_sl_api_key() -> str:
    if not _env_initialized:
        raise RuntimeError(
            "Environment not initialized. "
            "Call load_and_validate_env() first."
        )

    value = os.getenv("SL_APIKEY")
    if not value:
        raise RuntimeError("SL_APIKEY not available after validation")

    return value.strip()
