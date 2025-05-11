import time
from auth import admin_login
from admin import admin_menu
from customer import customer_menu
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_banner():
    clear_screen()
    print("\033[1;36m")  # Cyan color
    typewriter(r"""
  ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███╗   ██╗███████╗███████╗████████╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗████╗  ██║██╔════╝██╔════╝╚══██╔══╝
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██╔██╗ ██║█████╗  ███████╗   ██║   
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝  ╚════██║   ██║   
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║ ╚████║███████╗███████║   ██║   
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   
    """)
    print("\033[1;35m")  # Purple color
    typewriter("═"*75)
    typewriter(" "*20 + "🎮 CYBERNEST MANAGEMENT SYSTEM v2.0 🕹️")
    typewriter("═"*75)
    print("\033[0m")  # Reset color
    time.sleep(1)

def main_menu():
    while True:
        clear_screen()

        print("\033[1;36m" + "═" * 60 + "\033[0m")
        print("🎮 \033[1;35mCYBERNEST SYSTEM v1.0\033[0m - \033[1;33mWhere Pixels Come to Play!\033[0m")
        print("⚡️\033[1;36m" + "═" * 57 + "\033[0m")

        print("\n\033[1;34m🕹️  MAIN MENU - Choose your adventure! 🎯\033[0m")
        print("\033[1;36m" + "-" * 50 + "\033[0m")
        print("\033[1;32m[1]\033[0m 🔐  Admin Panel")
        print("\033[1;32m[2]\033[0m 👾  Customer Zone")
        print("\033[1;32m[0]\033[0m 📴  Exit the Arcade Portal")
        print("\033[1;36m" + "-" * 50 + "\033[0m")

        choice = input("\033[1;33m🔸 Select your option (0-2): \033[0m")

        if choice == '1':
            clear_screen()
            print("\033[1;35m🔐 Authenticating admin privileges...\033[0m")
            time.sleep(1)
            if admin_login():
                clear_screen()
                admin_menu()
        elif choice == '2':
            clear_screen()
            print("\033[1;36m👾 Loading Customer Zone...\033[0m")
            time.sleep(1)
            clear_screen()
            customer_menu()
        elif choice == '0':
            print("\n\033[1;33m💤 Powering down CyberNest...\033[0m")
            time.sleep(1)
            print("\033[1;32m✔️ Thank you for playing! See you next round!\033[0m")
            print("\033[1;36m" + "═" * 50 + "\033[0m")
            break
        else:
            print("\n\033[1;31m❌ Invalid option! Try again, warrior!\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    try:
        show_banner()
        time.sleep(1.5)
        main_menu()

    except KeyboardInterrupt:
        print("\n\033[1;31m⚠️  Emergency shutdown initiated!\033[0m")
        time.sleep(1)
        print("\033[1;35mSee you in the cyberspace...\033[0m")
