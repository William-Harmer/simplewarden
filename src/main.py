import json
import pprint
import subprocess
import requests
from SLCient import SLClient
from bw_auth import bw_get_status, bw_lock, bw_login, bw_logout, bw_unlock
from config import BW_CLI
from env import get_sl_api_key, load_and_validate_env


def create_list_of_logins():
    result = subprocess.run(
        [BW_CLI, "list", "items"],
        text=True,
        capture_output=True,
        check=True
    )

    items = json.loads(result.stdout)

    results = []

    for item in items:
        login = item.get("login") or {}

        results.append({
            "username": login.get("username"),
            "uris": login.get("uris"),
            "password": login.get("password"),
        })

    return results

def interactive_console():
    bw_login()
    bw_unlock()
    sl_client = SLClient()

    print("Interactive mode started.")
    print("Type 'logout' to log out and exit.")

    while True:
        user_input = input("> ").strip().lower()

        if user_input == "logout":
            break
        elif user_input == "":
            continue
        elif user_input == "sllist":
            sl_client.create_list_of_alias_emails()
            for email in sl_client.emails:
                print(email)
            sl_client.clear_emails()
        elif user_input == "bwlist":
            logins = create_list_of_logins()
            for login in logins:
                print("-" * 40)
                for value in login.values():
                    print(value)
        else:
            print(f"Unknown command: {user_input}")

def main():
    load_and_validate_env()
    interactive_console()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        lock_err = None
        logout_err = None

        try:
            bw_lock()
        except Exception as e:
            lock_err = e

        try:
            bw_logout()
        except Exception as e:
            logout_err = e

        if lock_err:
            print(f"Cleanup: lock failed: {lock_err}")
        if logout_err:
            print(f"Cleanup: logout failed: {logout_err}")