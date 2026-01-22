import json
import os
import subprocess
from config import BW_CLI
from dotenv import load_dotenv

def get_status():
    result = subprocess.run([BW_CLI, "status"], text = True, capture_output=True, check=True)

    # print(result.stdout) will be {"serverUrl":null,"lastSync":null,"status":"unauthenticated"}

    # "unauthenticated" or "locked" or "unlocked"
    return json.loads(result.stdout)["status"]

def logout():
    # Add the option for when locked in with locked or unlocked vault
    if get_status() == "unauthenticated":
        print("Already logged out")
    else:
        subprocess.run([BW_CLI, "logout"], check=True)

def login():
    if get_status() == "unauthenticated":
        subprocess.run([BW_CLI, "login", "--apikey"], check=True)


def interactive_console():
    print("Interactive mode started.")
    print("Type 'logout' to log out and exit.")

    while True:
        try:
            user_input = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input == "logout":
            logout()
            break
        elif user_input == "":
            continue
        else:
            print(f"Unknown command: {user_input}")
        
def main():
    # Check that the .env variables have been loaded
    # Need to write a proper error check for these
    load_dotenv()
    print("BW_CLIENTID set:", bool(os.getenv("BW_CLIENTID")))
    print("BW_CLIENTSECRET set:", bool(os.getenv("BW_CLIENTSECRET")))

    login()
    interactive_console()

if __name__ == "__main__":
    main()