from SLClient import SLClient
from BWClient import BWClient
from env import get_sl_api_key


def interactive_console(bw_client):
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
            sl_client.create_counter_of_alias_emails()
            for email in sl_client.emails:
                print(email)
            sl_client.clear_emails()
        elif user_input == "bwlist":
            bw_client.create_counter_of_usernames()
            for username in bw_client.usernames:
                print(username)
            bw_client.clear_usernames()
        elif user_input == "bwsllist":
            bw_client.create_counter_of_usernames()
            bw_client.create_counter_of_slemails()
            for email in bw_client.slemails:
                print(email)
            bw_client.clear_slemails()
            bw_client.clear_usernames()
        else:
            print(f"Unknown command: {user_input}")


def cleanup_bw_client(bw_client):
    """Cleanup function to lock and logout from Bitwarden."""
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


def main():
    bw_client = None
    try:
        bw_client = BWClient()
        bw_client.login()
        bw_client.unlock()
        interactive_console(bw_client)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Cleaning up...")
    finally:
        cleanup_bw_client(bw_client)
    
    return bw_client


if __name__ == "__main__":
    main()
