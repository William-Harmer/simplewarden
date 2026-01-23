# bw_auth.py
import json
import os
import subprocess
from config import BW_CLI

def bw_get_status() -> str:
    result = subprocess.run([BW_CLI, "status"], text=True, capture_output=True, check=True)
    return json.loads(result.stdout)["status"]  # unauthenticated | locked | unlocked

def bw_logout() -> None:
    if bw_get_status() == "unauthenticated":
        print("Already logged out")
    else:
        subprocess.run([BW_CLI, "logout"], check=True)

def bw_login() -> None:
    if bw_get_status() == "unauthenticated":
        subprocess.run([BW_CLI, "login", "--apikey"], check=True)
    else:
        print("You are already logged in.")

def bw_unlock() -> None:
    status = bw_get_status()

    if status == "unauthenticated":
        print("You are not logged in and so you cannot unlock your vault.")
        return

    if status == "unlocked":
        print("Your vault is already unlocked.")
        return

    # status == "locked"
    result = subprocess.run(
        [BW_CLI, "unlock", "--raw"],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    os.environ["BW_SESSION"] = result.stdout.strip()
    print("Vault unlocked.")

def bw_lock() -> None:
    status = bw_get_status()
    if status == "unauthenticated":
        print("You are not logged in and so you cannot lock your vault.")
    elif status == "locked":
        print("Your vault is already locked.")
    else:
        subprocess.run([BW_CLI, "lock"], check=True)
