import requests
from env import get_sl_api_key, load_and_validate_env

class SLClient:
    _initialized = False
    SL_APIKEY: str

    def __init__(self):
        if not SLClient._initialized:
            load_and_validate_env()
            SLClient.SL_APIKEY = get_sl_api_key()
            SLClient._initialized = True

        self._emails: list[str] | None = None

    def create_list_of_alias_emails(self) -> None:
        emails: list[str] = []
        page = 0

        while True:
            resp = requests.get(
                "https://app.simplelogin.io/api/v2/aliases",
                headers={"Authentication": SLClient.SL_APIKEY},
                params={"page_id": page},
                timeout=30,
            )
            resp.raise_for_status()

            aliases = resp.json()["aliases"]
            if not aliases:
                break

            for alias in aliases:
                emails.append(alias["email"])

            page += 1

        # Assign only after fully built
        self._emails = emails

    def clear_emails(self):
        self._emails = None

    @property
    def emails(self) -> list[str]:
        if self._emails is None:
            raise RuntimeError(
                "Emails not loaded. Call create_list_of_alias_emails() first."
            )
        return self._emails
