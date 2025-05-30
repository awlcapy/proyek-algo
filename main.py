import time
from auth import admin_login
from admin import admin_menu, cleanup_queue_today
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

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar_length = 30
    filled_length = int(bar_length * progress // total)
    bar = '\033[92m' + '█' * filled_length + '\033[0m' + '-' * (bar_length - filled_length)
    print(f'\r|{bar}| {percent:.0f}%', end='\r')

def loading_animation(duration=2):
    animation = ['.  ', '.. ', '...']
    start_time = time.time()
    idx = 0
    while (time.time() - start_time) < duration:
        print(f"\r\033[1;36mLoading Customer Zone{animation[idx % len(animation)]}\033[0m", end='')
        idx += 1
        time.sleep(0.5)
    print()

def show_progress():
    total = 40
    for i in range(total + 1):
        progress_bar(i, total)
        time.sleep(0.04)
    print()  # pindah baris setelah selesai

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
                cleanup_queue_today()
                admin_menu()
        elif choice == '2':
            clear_screen()
            loading_animation(duration=2)
            show_progress()
            time.sleep(0.5)
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
