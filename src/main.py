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
    print("Type 'sync' to sync the Bitwarden vault.")
    print("Type 'bwstatus' to print the Bitwarden vault status.")
    print("Type 'sllist' to list all SimpleLogin alias emails.")
    print("Type 'bwlist' to list all Bitwarden usernames.")
    print("Type 'bwsllist' to list all SimpleLogin emails in Bitwarden.")
    print("Type 'compare' to compare SimpleLogin and Bitwarden aliases.")

    while True:
        user_input = input("> ").strip().lower()

        if user_input == "logout":
            break
        elif user_input == "":
            continue
        elif user_input == "sllist":
            sl_client.create_emails()
            for email in sl_client.emails:
                print(email)
            sl_client.clear_emails()
        elif user_input == "bwlist":
            bw_client.create_usernames()
            for username in bw_client.usernames:
                print(username)
            bw_client.clear_usernames()
        elif user_input == "bwsllist":
            bw_client.create_usernames()
            bw_client.create_sl_emails()
            for email in bw_client.sl_emails:
                print(email)
            bw_client.clear_sl_emails()
            bw_client.clear_usernames()
        elif user_input == "compare":
            # Load both lists
            sl_client.create_emails()
            bw_client.create_usernames()
            bw_client.create_sl_emails()
            
            # Compare them
            differences = compare_aliases(sl_client.emails, bw_client.sl_emails)
            
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
            bw_client.clear_sl_emails()
            bw_client.clear_usernames()
        elif user_input == "lock":
            bw_client.lock()
        elif user_input == "unlock":
            bw_client.unlock()
        elif user_input == "sync":
            bw_client.sync()
        elif user_input == "bwstatus":
            print(bw_client.get_status())
        else:
            print(f"Unknown command: {user_input}")


def cleanup_bw_client(bw_client):
    """Cleanup function to lock and logout from Bitwarden."""
    if bw_client:
        try:
            bw_client.lock()
        except Exception:
            pass  # Error already printed by BWClient
        try:
            bw_client.logout()
        except Exception:
            pass  # Error already printed by BWClient


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
