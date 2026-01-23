# main.py
import json
import pprint
import subprocess
from dotenv import load_dotenv
from config import BW_CLI
from bw_auth import login, logout, unlock, lock  # <-- import from other file

def list_items():
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
    login()
    unlock()

    print("Interactive mode started.")
    print("Type 'logout' to log out and exit.")

    while True:
        try:
            user_input = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input == "logout":
            break
        elif user_input == "list":
            list_items()
        elif user_input == "":
            continue
        else:
            print(f"Unknown command: {user_input}")

    lock()
    logout()

def main():
    load_dotenv()
    interactive_console()

if __name__ == "__main__":
    main()
