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
    else:
        print("You are already logged in.")


# Need to understand what is happening here
def unlock():
    status = get_status()
    
    if status == "unauthenticated":
        print("You are not logged in and so you cannot unlock your vault.")

    elif status == "unlocked":
        print("Your vault is already unlocked.")

    elif status == "locked":

        result = subprocess.run(
            [BW_CLI, "unlock", "--raw"], # --raw allows only the session key to be outputted to console
            text=True, # treat the subprocess input/output as text (strings), not bytes.

            # Do not print the output to the console (Which is the raw session key), instead store the console output in result.stdout
            # We can't use capture_output here because otherwise it also captures stderr whihc is where bitwarden prints its password prompt to stderr
            stdout=subprocess.PIPE,


            check=True
        ) 
        session = result.stdout
        os.environ["BW_SESSION"] = session
        print("Vault unlocked (session stored).")


def lock():
    status = get_status()
    if status == "unauthenticated":
        print("You are not logged in and so you cannot lock your vault.")
    elif status == "locked":
        print("Your vault is already locked.")
    elif status == "unlocked":
        subprocess.run([BW_CLI, "lock"], check=True)



def interactive_console():
    print("\n\n")
    print(get_status())
    login()
    print("\n\n")
    print(get_status())
    unlock()
    print("\n\n")
    print(get_status())

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
        elif user_input == "":
            continue
        else:
            print(f"Unknown command: {user_input}")
    
    # lock()
    # logout()
        
def main():
    # Check that the .env variables have been loaded
    # Need to write a proper error check for these
    load_dotenv()
    print("BW_CLIENTID set:", bool(os.getenv("BW_CLIENTID")))
    print("BW_CLIENTSECRET set:", bool(os.getenv("BW_CLIENTSECRET")))


    interactive_console()

if __name__ == "__main__":
    main()