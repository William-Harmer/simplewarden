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
        self._sl_emails: Counter[str] | None = None

    def get_status(self) -> str:
        try:
            _result = subprocess.run([BW_CLI, "status"], text=True, capture_output=True, check=True)
            return json.loads(_result.stdout)["status"]
        except subprocess.CalledProcessError as e:
            print(f"Error getting status: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing status JSON: {e}")
            raise
        except Exception as e:
            print(f"Error getting status: {e}")
            raise
    
    def logout(self) -> None:
        if self.get_status() == "unauthenticated":
            print("Already logged out")
        else:
            try:
                subprocess.run([BW_CLI, "logout"], capture_output=True, check=True)
                print("Logged out successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error logging out: {e}")
                raise
            except Exception as e:
                print(f"Error logging out: {e}")
                raise

    def login(self) -> None:
        if self.get_status() == "unauthenticated":
            try:
                subprocess.run([BW_CLI, "login", "--apikey"], capture_output=True, check=True)
                print("Logged in successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error logging in: {e}")
                raise
            except Exception as e:
                print(f"Error logging in: {e}")
                raise
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

        try:
            _result = subprocess.run(
                [BW_CLI, "unlock", "--raw"],
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )

            session_key = _result.stdout.strip()
            os.environ["BW_SESSION"] = session_key
            print("Vault unlocked.")
        except subprocess.CalledProcessError as e:
            print(f"Error unlocking vault: {e}")
            raise
        except Exception as e:
            print(f"Error unlocking vault: {e}")
            raise
    
    
    def lock(self) -> None:
        _status = self.get_status()
        if _status == "unauthenticated":
            print("You are not logged in and so you cannot lock your vault.")
        elif _status == "locked":
            print("Your vault is already locked.")
        else:
            try:
                subprocess.run([BW_CLI, "lock"], capture_output=True, check=True)
                print("Vault locked successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error locking vault: {e}")
                raise
            except Exception as e:
                print(f"Error locking vault: {e}")
                raise

    def sync(self) -> None:
        _status = self.get_status()
        if _status == "unauthenticated":
            print("You are not logged in and so you cannot sync your vault.")
            return
        
        try:
            subprocess.run([BW_CLI, "sync"], capture_output=True, check=True)
            print("Vault synced successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error syncing vault: {e}")
            raise
        except Exception as e:
            print(f"Error syncing vault: {e}")
            raise

    def create_usernames(self) -> None:
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

        self._usernames = usernames

    def clear_usernames(self) -> None:
        self._usernames = None

    def create_sl_emails(self) -> None:
        if self._usernames is None:
            raise RuntimeError(
                "Usernames not loaded. Call create_usernames() first."
            )
        
        sl_emails: Counter[str] = Counter()
        
        for username in self._usernames:
            if username.endswith("@simplelogin.com"):
                sl_emails[username] = self._usernames[username]
        
        self._sl_emails = sl_emails

    def clear_sl_emails(self) -> None:
        self._sl_emails = None

    @property
    def usernames(self) -> Counter[str]:
        if self._usernames is None:
            raise RuntimeError(
                "Usernames not loaded. Call create_usernames() first."
            )
        return self._usernames

    @property
    def sl_emails(self) -> Counter[str]:
        if self._sl_emails is None:
            raise RuntimeError(
                "SLEmails not loaded. Call create_sl_emails() first."
            )
        return self._sl_emails