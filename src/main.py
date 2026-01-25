from SLClient import SLClient
from BWClient import BWClient
from env import get_sl_api_key
from collections import Counter


def compare_aliases(sl_emails: Counter[str], bw_sl_emails: Counter[str]) -> dict:
    missing_in_bw = []
    missing_in_sl = []
    
    # Get all unique emails from both lists
    all_emails = set(sl_emails.keys()) | set(bw_sl_emails.keys())
    
    for email in all_emails:
        sl_count = sl_emails.get(email, 0)
        bw_count = bw_sl_emails.get(email, 0)
        
        if sl_count > bw_count:
            # SL has more entries than BW - problem is in BW
            missing_in_bw.append(email)
        elif bw_count > sl_count:
            # BW has more entries than SL - problem is in SL (BW has extras)
            missing_in_sl.append(email)
        elif sl_count == 0 and bw_count > 0:
            # Email is in BW but not in SL
            missing_in_sl.append(email)
        elif bw_count == 0 and sl_count > 0:
            # Email is in SL but not in BW
            missing_in_bw.append(email)
        # If counts match and both > 0, no problem - don't add to either list
    
    return {
        'missing_in_bw': missing_in_bw,
        'missing_in_sl': missing_in_sl
    }


def interactive_console(bw_client):
    sl_client = SLClient()

    print("Interactive mode started.")
    print("Type 'logout' to log out and exit.")
    print("Type 'lock' to lock the Bitwarden vault.")
    print("Type 'unlock' to unlock the Bitwarden vault.")

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
        elif user_input == "compare":
            # Load both lists
            sl_client.create_counter_of_alias_emails()
            bw_client.create_counter_of_usernames()
            bw_client.create_counter_of_slemails()
            
            # Compare them
            differences = compare_aliases(sl_client.emails, bw_client.slemails)
            
            # Display results
            if differences['missing_in_bw']:
                print("\nMissing in Bitwarden:")
                for email in differences['missing_in_bw']:
                    print(email)
            
            if differences['missing_in_sl']:
                print("\nMissing in SimpleLogin:")
                for email in differences['missing_in_sl']:
                    print(email)
            
            if not differences['missing_in_bw'] and not differences['missing_in_sl']:
                print("\nPerfect match!")
            
            print()
            
            # Cleanup
            sl_client.clear_emails()
            bw_client.clear_slemails()
            bw_client.clear_usernames()
        elif user_input == "lock":
            try:
                bw_client.lock()
            except Exception as e:
                print(f"Error locking vault: {e}")
        elif user_input == "unlock":
            try:
                bw_client.unlock()
            except Exception as e:
                print(f"Error unlocking vault: {e}")
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
