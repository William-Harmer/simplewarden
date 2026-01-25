import json
import os
import subprocess
from collections import Counter
from config import BW_CLI
from env import load_and_validate_env


class BWClient:

    def __init__(self):
        load_and_validate_env()
        self._usernames: Counter[str] | None = None
        self._slemails: Counter[str] | None = None

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

        # Strip actually needed
        session_key = _result.stdout.strip()
        os.environ["BW_SESSION"] = session_key
        print("Vault unlocked.")
    
    
    def lock(self) -> None:
        _status = self.get_status()
        if _status == "unauthenticated":
            print("You are not logged in and so you cannot lock your vault.")
        elif _status == "locked":
            print("Your vault is already locked.")
        else:
            subprocess.run([BW_CLI, "lock"], check=True)

    def create_counter_of_usernames(self) -> None:
        status = self.get_status()
        
        if status != "unlocked":
            self.unlock()
            status = self.get_status()
            if status != "unlocked":
                raise RuntimeError(f"Cannot proceed: vault is not unlocked (status: {status})")
        
        try:
            _result = subprocess.run(
                [BW_CLI, "list", "items"],
                text=True,
                capture_output=True,
                check=True,
                timeout=30
            )
        except subprocess.TimeoutExpired:
            print("ERROR: Subprocess timed out after 30 seconds")
            raise
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Subprocess failed with return code {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error: {type(e).__name__}: {e}")
            raise

        items = json.loads(_result.stdout)

        usernames: Counter[str] = Counter()

        for item in items:
            login = item.get("login") or {}
            username = login.get("username")
            if username:
                usernames[username] += 1

        # Assign only after fully built
        self._usernames = usernames

    def clear_usernames(self) -> None:
        self._usernames = None

    def create_counter_of_slemails(self) -> None:
        if self._usernames is None:
            raise RuntimeError(
                "Usernames not loaded. Call create_counter_of_usernames() first."
            )
        
        slemails: Counter[str] = Counter()
        
        for username in self._usernames:
            if username.endswith("@simplelogin.com"):
                slemails[username] = self._usernames[username]
        
        self._slemails = slemails

    def clear_slemails(self) -> None:
        self._slemails = None

    @property
    def usernames(self) -> Counter[str]:
        if self._usernames is None:
            raise RuntimeError(
                "Usernames not loaded. Call create_counter_of_usernames() first."
            )
        return self._usernames

    @property
    def slemails(self) -> Counter[str]:
        if self._slemails is None:
            raise RuntimeError(
                "SLEmails not loaded. Call create_counter_of_slemails() first."
            )
        return self._slemails