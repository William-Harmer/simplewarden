import json
import os
import subprocess
from config import BW_CLI
from env import load_and_validate_env


class BWClient:

    def __init__(self):
        load_and_validate_env()

    def get_status(self) -> str:
        _result = subprocess.run([BW_CLI, "status"], text=True, capture_output=True, check=True)
        return json.loads(_result.stdout)["status"]  # unauthenticated | locked | unlocked
    
    def logout(self) -> None:
        if self.get_status() == "unauthenticated":
            print("Already logged out")
        else:
            subprocess.run([BW_CLI, "logout"], check=True)

    def login(self) -> None:
        if self.get_status() == "unauthenticated":
            subprocess.run([BW_CLI, "login", "--apikey"], check=True)
        else:
            print("You are already logged in.")

    def unlock(self) -> None:
        _status = self.get_status()

        if _status == "unauthenticated":
            print("You are not logged in and so you cannot unlock your vault.")
            return

        if _status == "unlocked":
            print("Your vault is already unlocked.")
            return

        # status == "locked"
        _result = subprocess.run(
            [BW_CLI, "unlock", "--raw"],
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        os.environ["BW_SESSION"] = _result.stdout
        print("Vault unlocked.")
    
    
    def lock(self) -> None:
        _status = self.get_status()
        if _status == "unauthenticated":
            print("You are not logged in and so you cannot lock your vault.")
        elif _status == "locked":
            print("Your vault is already locked.")
        else:
            subprocess.run([BW_CLI, "lock"], check=True)

    def create_list_of_logins(self):
        _result = subprocess.run(
            [BW_CLI, "list", "items"],
            text=True,
            capture_output=True,
            check=True
        )

        items = json.loads(_result.stdout)

        _results = []

        for item in items:
            login = item.get("login") or {}

            _results.append({
                "username": login.get("username"),
                "uris": login.get("uris"),
                "password": login.get("password"),
            })

        return _results