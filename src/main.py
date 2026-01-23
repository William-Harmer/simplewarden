import json
import pprint
import subprocess

from bw_auth import bw_get_status, bw_lock, bw_login, bw_logout, bw_unlock
from config import BW_CLI
from env import get_sl_api_key, load_and_validate_env


def bw_list_items():
    result = subprocess.run(
        [BW_CLI, "list", "items"],
        text=True,
        capture_output=True,
        check=True
    )

    items = json.loads(result.stdout)

    print(f"Total items: {len(items)}")
    print("=" * 40)

    for i, item in enumerate(items, start=1):
        login_obj = item.get("login", {}) or {}

        output = {
            "index": i,
            "username": login_obj.get("username"),
            "uris": login_obj.get("uris"),
            "password": login_obj.get("password"),
        }

        pprint.pprint(output)
        print("-" * 40)

def interactive_console():
    bw_login()
    bw_unlock()

    print("Interactive mode started.")
    print("Type 'logout' to log out and exit.")

    while True:
        user_input = input("> ").strip().lower()

        if user_input == "logout":
            break
        elif user_input == "list":
            bw_list_items()
        elif user_input == "":
            continue
        else:
            print(f"Unknown command: {user_input}")

def main():
    load_and_validate_env()
    SL_API_KEY = get_sl_api_key()
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