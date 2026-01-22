import json
import subprocess
from config import BW_CLI

def get_status():
    result = subprocess.run([str(BW_CLI), "status"], text = True, capture_output=True, check=True)

    # print(result.stdout) will be {"serverUrl":null,"lastSync":null,"status":"unauthenticated"}

    # "unauthenticated" or "locked" or "unlocked"
    return json.loads(result.stdout)["status"]

# def login():
#     if get_status() == "unauthenticated":
#         result = subprocess.run([str(BW_CLI), "login"], text = True, capture_output=True, check=True)
#     else:
#         print("You are already logged in")
        
def main():
    print(get_status())

if __name__ == "__main__":
    main()