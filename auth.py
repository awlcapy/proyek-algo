from utils import load_admin_credentials, save_admin_credentials
import getpass
import time
import sys

def print_header(title):
    print("\n\033[1;36m╔════════════════════════════════════════╗")
    print(f"║{' ' * ((40 - len(title))//2)}{title}{' ' * ((40 - len(title))//2)}║")
    print("╚════════════════════════════════════════╝\033[0m")

def animate_text(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def admin_login():
    credentials = load_admin_credentials()
    attempts = 3
    
    print_header("🔐 ADMIN LOGIN")
    animate_text("Please enter your credentials to continue...")
    
    while attempts > 0:
        print(f"\n\033[1;33mAttempts remaining: {attempts}\033[0m")
        
        try:
            username = input("\033[1;34m⌨ Username: \033[0m").strip()
            password = getpass.getpass("\033[1;34m🔒 Password: \033[0m").strip()
            
            if username == credentials['username'] and password == credentials['password']:
                print("\n\033[1;32m✓ Login successful! Redirecting...\033[0m")
                time.sleep(1.5)
                return True
            else:
                print("\n\033[1;31m✗ Invalid username or password!\033[0m")
                attempts -= 1
                if attempts > 0:
                    animate_text("Please try again...", 0.05)
                    time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\033[1;33m⚠ Login cancelled\033[0m")
            return False
    
    print("\n\033[1;31m⛔ Account locked after 3 failed attempts!\033[0m")
    time.sleep(2)
    return False

def change_admin_password():
    credentials = load_admin_credentials()
    
    print_header("🔑 CHANGE PASSWORD")
    animate_text("Please verify your current password first")
    
    # Verify current password
    current_pass = getpass.getpass("\033[1;34m🔒 Current Password: \033[0m").strip()
    if current_pass != credentials['password']:
        print("\n\033[1;31m✗ Password verification failed!\033[0m")
        time.sleep(1.5)
        return
    
    # Get new password
    while True:
        print("\n\033[1;37mPassword requirements:")
        print("- Minimum 3 characters")
        print("- Should be memorable for you\033[0m")
        
        new_pass = getpass.getpass("\033[1;34m✨ New Password: \033[0m").strip()
        confirm_pass = getpass.getpass("\033[1;34m🔄 Confirm Password: \033[0m").strip()
        
        if new_pass != confirm_pass:
            print("\n\033[1;31m✗ Passwords don't match!\033[0m")
        elif len(new_pass) < 3:
            print("\n\033[1;31m✗ Password too short!\033[0m")
        else:
            credentials['password'] = new_pass
            save_admin_credentials(credentials)
            print("\n\033[1;32m✓ Password changed successfully!\033[0m")
            time.sleep(1.5)
            break
        
        time.sleep(1.5)
        print("\n\033[1;33mPlease try again...\033[0m")