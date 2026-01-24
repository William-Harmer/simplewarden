from SLClient import SLClient
from BWClient import BWClient
from env import get_sl_api_key


def interactive_console():
    bw_client = BWClient()
    bw_client.login()
    bw_client.unlock()
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
            logins = bw_client.create_list_of_logins()
            for login in logins:
                print("-" * 40)
                for value in login.values():
                    print(value)
        else:
            print(f"Unknown command: {user_input}")

    return bw_client


def main():
    return interactive_console()


if __name__ == "__main__":
    bw_client = main()

    if bw_client:
        lock_err = None
        logout_err = None

        try:
            bw_client.lock()
        except Exception as e:
            lock_err = e

        try:
            bw_client.logout()
        except Exception as e:
            logout_err = e

        if lock_err:
            print(f"Cleanup: lock failed: {lock_err}")
        if logout_err:
            print(f"Cleanup: logout failed: {logout_err}")
