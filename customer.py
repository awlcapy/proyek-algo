# Import modul dan fungsi yang diperlukan
from utils import load_json, save_json, next_id, RUANGAN_FILE, CUSTOMER_FILE, HISTORY_FILE, ONLINE_FILE, QUEUE_FILE
from admin import add_to_history
from datetime import datetime, date
import os
import sys
import time
import random

# Fungsi untuk membersihkan layar console
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Fungsi untuk menampilkan teks dengan efek animasi ketik berwarna-warni
def animate_text(text, delay=0.03):
    colors = ['\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m', '\033[1;35m', '\033[1;36m']
    for char in text:
        sys.stdout.write(random.choice(colors) + char)  # Tulis karakter dengan warna acak
        sys.stdout.flush()  # Pastikan karakter langsung ditampilkan
        time.sleep(delay)   # Jeda antara karakter
    print('\033[0m')  # Reset warna setelah selesai

# Fungsi untuk menampilkan seni pixel CYBERNEST
def draw_pixel_art():
    pixel_art = [
        "  ╔═════════════════════════╗",
        "  ║ CYBERNEST GAMING CENTER ║",
        "  ╚═════════════════════════╝",
        "            \_(*-*)_/",
        "           ┌─┐ ┌─┐ ┌─┐",
        "           │S│ │S│ │R│",
        "           └─┘ └─┘ └─┘"
    ]
    for line in pixel_art:
        animate_text(line, 0.01)
        time.sleep(0.05)

# Fungsi untuk menampilkan animasi loading
def loading_animation(duration=2):
    frames = ['[■□□□□]', '[■■□□□]', '[■■■□□]', '[■■■■□]', '[■■■■■]']
    end_time = time.time() + duration
    while time.time() < end_time:
        for frame in frames:
            print(f"\r\033[1;35m{frame} Loading...\033[0m", end='')
            time.sleep(0.3)
    print('\r' + ' ' * 30 + '\r', end='')  # Bersihkan baris loading

# Fungsi untuk menampilkan efek fireworks (kembang api)
def fireworks():
    for _ in range(5):
        print(" " * random.randint(0, 50) + random.choice(["✨", "💥", "🌟"]))
        time.sleep(0.1)
    print("\033[5F")  # Gerakkan cursor ke atas 5 baris

# Fungsi untuk menampilkan banner sistem
def show_banner():
    animate_text("   🎮 CYBERNEST BOOKING SYSTEM 🎮")
    print("*"*50 + "\033[0m")

# Fungsi untuk validasi format tanggal
def validate_date(input_date):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return None

# Fungsi untuk mendapatkan jam yang tersedia pada ruangan tertentu di tanggal tertentu
def get_available_hours(history_list, ruangan_id, tanggal):
    # Ambil semua jam yang sudah dibooking untuk ruangan dan tanggal tertentu
    booked_hours = [q['jam'] for q in history_list 
                   if q['ruangan_id'] == ruangan_id 
                   and q['tanggal'] == str(tanggal)]
    # Kembalikan jam yang tersedia (7-23) kecuali yang sudah dibooking
    return [h for h in range(7, 23) if h not in booked_hours]

# Fungsi untuk menampilkan ruangan yang tersedia
def show_available_rooms(ruangan_list, history_list, booking_date=None):
    # Jika tanggal tidak disediakan, minta input dari user
    if booking_date is None:
        while True:
            clear_screen()
            show_banner()
            print("\n" + "="*50)
            animate_text("📅 MASUKKAN TANGGAL BOOKING")
            print("="*50)
            date_str = input("\n\033[1;33mFormat (YYYY-MM-DD): \033[0m").strip()
            booking_date = validate_date(date_str)
            if booking_date and booking_date >= date.today():
                break
            print("\n\033[1;31m❌ Tanggal tidak valid atau sudah lewat!\033[0m")
            time.sleep(1)
    
    loading_animation(1)
    
    # Tampilkan daftar ruangan dengan status ketersediaan
    print("\n" + "="*80)
    animate_text("🎮 DAFTAR RUANGAN CYBERNEST")
    print("="*80)
    print("\033[1;34mID    JENIS      KAPASITAS    KONSOLE                  STATUS\033[0m")
    print("-"*80)
    for room in ruangan_list:
        console = ', '.join(room.get('console', ['Tidak ada info']))
        available_hours = get_available_hours(history_list, room['id'], str(booking_date))
        status = "\033[1;32m✅ Tersedia\033[0m" if available_hours else "\033[1;31m❌ Penuh\033[0m"
        print(f"{room['id']:<5} {room['jenis']:<10} {room['kapasitas']:<12} {console:<20} {status}")
    print("="*80)
    
    # Minta user memilih ruangan
    while True:
        try:
            room_id = int(input("\n\033[1;33m🎮 Pilih ID Ruangan (0 untuk batal): \033[0m"))
            if room_id == 0:
                return None, None, None
            selected_room = next(r for r in ruangan_list if r['id'] == room_id)
            break
        except (ValueError, StopIteration):
            print("\033[1;31m❌ ID Ruangan tidak valid!\033[0m")
            time.sleep(0.5)
    
    available_hours = get_available_hours(history_list, room_id, str(booking_date))
    
    # Jika tidak ada jam tersedia
    if not available_hours:
        animate_text(f"\n❌ Ruangan {selected_room['jenis']} (ID: {room_id}) sudah penuh pada {booking_date}!")
        time.sleep(1.5)
        return None, None, None
    
    # Tampilkan slot waktu yang tersedia
    print(f"\n" + "="*50)
    animate_text(f"⏰ SLOT WAKTU TERSEDIA - {selected_room['jenis'].upper()}")
    print("="*50)
    for i, hour in enumerate(available_hours, 1):
        print(f"\033[1;33m{i}. 🕒 {hour:02d}:00-{hour+1:02d}:00\033[0m")
    print("="*50)
    
    return booking_date, room_id, available_hours

# Fungsi untuk melakukan booking online
def online_booking(ruangan_list, history_list):
    clear_screen()
    draw_pixel_art()
    print("\n" + "="*50)
    animate_text("📅 BOOKING ONLINE")
    print("="*50)
    
    # Input data pelanggan
    print("\n" + "✧"*40)
    animate_text("👤 INFORMASI PELANGGAN")
    print("✧"*40)
    
    while True:
        name = input("\033[1;33m📝 Nama Lengkap: \033[0m").strip()
        if name:
            break
        print("\033[1;31m❌ Nama tidak boleh kosong!\033[0m")
    
    while True:
        phone = input("\033[1;33m📱 Nomor HP (min 10 digit): \033[0m").strip()
        if phone.isdigit() and len(phone) >= 10:
            break
        print("\033[1;31m❌ Nomor HP harus angka minimal 10 digit!\033[0m")

    # Input tanggal booking
    print("\n" + "✧"*40)
    animate_text("📅 TANGGAL BOOKING")
    print("✧"*40)
    while True:
        date_str = input("\033[1;33m📅 Format (YYYY-MM-DD): \033[0m").strip()
        booking_date = validate_date(date_str)
        if booking_date and booking_date >= date.today():
            break
        print("\033[1;31m❌ Tanggal tidak valid atau sudah lewat!\033[0m")

    customer_list = load_json(CUSTOMER_FILE)
    
    # Proses pemilihan ruangan
    while True:
        clear_screen()
        animate_text("🎮 MEMUAT DAFTAR RUANGAN...")
        loading_animation(1)
        
        # Tampilkan daftar ruangan
        print("\n" + "✧"*80)
        animate_text("🎮 DAFTAR RUANGAN TERSEDIA")
        print("✧"*80)
        print("\033[1;34mID    JENIS      KAPASITAS    KONSOLE                  STATUS\033[0m")
        print("-"*80)
        for room in ruangan_list:
            available_hours = get_available_hours(history_list, room['id'], str(booking_date))
            status = "\033[1;32m✅ Tersedia\033[0m" if available_hours else "\033[1;31m❌ Penuh\033[0m"
            console = ', '.join(room.get('console', ['Tidak ada info']))
            print(f"{room['id']:<5} {room['jenis']:<10} {room['kapasitas']:<12} {console:<20} {status}")
        print("✧"*80)
        
        try:
            room_id = int(input("\n\033[1;33m🎮 Pilih ID Ruangan (0 untuk batal): \033[0m"))
            if room_id == 0:
                return
            selected_room = next(r for r in ruangan_list if r['id'] == room_id)
            break
        except (ValueError, StopIteration):
            print("\033[1;31m❌ ID Ruangan tidak valid!\033[0m")
            time.sleep(0.5)

    available_hours = get_available_hours(history_list, room_id, str(booking_date))
    
    if not available_hours:
        animate_text(f"\n❌ Ruangan {selected_room['jenis']} (ID: {room_id}) sudah penuh pada {booking_date}!")
        time.sleep(1.5)
        return
    
    # Proses pemilihan waktu booking
    while True:
        print(f"\n" + "✧"*50)
        animate_text(f"⏰ PILIH WAKTU - {selected_room['jenis'].upper()}")
        print("✧"*50)
        for i, hour in enumerate(available_hours, 1):
            print(f"\033[1;33m{i}. 🕒 {hour:02d}:00-{hour+1:02d}:00\033[0m")
        print("✧"*50)
        
        try:
            slot_choice = int(input("\033[1;33m🎮 Pilih nomor slot (0 untuk ganti ruangan): \033[0m"))
            if slot_choice == 0:
                break
            elif 1 <= slot_choice <= len(available_hours):
                start_hour = available_hours[slot_choice-1]
                
                duration = int(input("\033[1;33m⏳ Durasi (1-4 jam): \033[0m"))
                duration = max(1, min(4, duration))  # Pastikan durasi antara 1-4 jam
                
                # Periksa ketersediaan untuk durasi yang diminta
                if all(h in available_hours for h in range(start_hour, start_hour + duration)):
                    animate_text("\n🔍 Memproses booking...")
                    loading_animation(2)
                    
                    # Buat ID customer baru
                    cust_id = next_id(customer_list)
                    
                    # Buat data customer baru
                    new_customer = {
                        'id': cust_id,
                        'nama': name,
                        'booking': [{
                            'ruangan_id': room_id,
                            'tanggal': str(booking_date),
                            'jam': hour,
                            'online': True,
                        } for hour in range(start_hour, start_hour + duration)]
                    }

                    # Simpan data customer
                    customer_list.append(new_customer)
                    save_json(CUSTOMER_FILE, customer_list)
                    
                    # Tambahkan ke history
                    for hour in range(start_hour, start_hour + duration):
                        add_to_history(history_list, cust_id, room_id, str(booking_date), hour, online=True)
                    save_json(HISTORY_FILE, history_list)

                    # Buat data booking online
                    online_booking_data = {
                        'customer_id': cust_id,
                        'nama': name,
                        'telepon': phone,
                        'ruangan_id': room_id,
                        'tanggal': str(booking_date),
                        'jam_mulai': start_hour,
                        'durasi': duration,
                        'status': 'not confirmed',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Simpan booking online
                    online_bookings = load_json(ONLINE_FILE)
                    online_bookings.append(online_booking_data)
                    save_json(ONLINE_FILE, online_bookings)

                    # Jika booking untuk hari ini, tambahkan ke antrian
                    today = datetime.now().strftime('%Y-%m-%d')
                    if str(booking_date) == today:
                        try:
                            queue_today = load_json(QUEUE_FILE)
                        except FileNotFoundError:
                            queue_today = []

                    new_booking = {
                        'customer_id': cust_id,
                        'ruangan_id': room_id,
                        'tanggal': str(booking_date),
                        'jam_mulai': start_hour,
                        'durasi': duration,
                        'status': 'belum_masuk',
                        'waktu_booking': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    queue_today.append(new_booking)
                    save_json(QUEUE_FILE, queue_today)

                    # Tampilkan konfirmasi booking
                    clear_screen()
                    print("\n" + "✧"*60)
                    animate_text("✨ BOOKING BERHASIL DIBUAT ✨")
                    print("✧"*60)
                    print(f"\033[1;34m{'📋 ID Booking:':<20} \033[1;33m{cust_id}")
                    print(f"\033[1;34m{'🎮 Ruangan:':<20} \033[1;33m{selected_room['jenis']} (ID: {room_id})")
                    print(f"\033[1;34m{'📅 Tanggal:':<20} \033[1;33m{booking_date}")
                    print(f"\033[1;34m{'⏰ Waktu:':<20} \033[1;33m{start_hour:02d}:00-{start_hour+duration:02d}:00")
                    print("✧"*60)
                    
                    # Tampilkan efek visual
                    fireworks()
                    for _ in range(3):
                        print("\n" + " ".join(random.choice(["🎮", "👾", "🕹️", "🎯"]) for _ in range(15)))
                        time.sleep(0.3)
                        print("\033[F" + " "*100 + "\033[F")
                    
                    return
                else:
                    animate_text("\n❌ Slot waktu tidak tersedia untuk durasi ini!")
                    time.sleep(1)
            else:
                print("\033[1;31m❌ Pilihan slot tidak valid!\033[0m")
                time.sleep(0.5)
        except ValueError:
            print("\033[1;31m❌ Input harus angka!\033[0m")
            time.sleep(0.5)

# Fungsi untuk memeriksa status booking
def check_booking_status():
    clear_screen()
    show_banner()
    print("\n" + "="*50)
    animate_text("🔍 CEK STATUS BOOKING")
    print("="*50)
    
    # Input data pelanggan
    print("\n" + "✧"*40)
    animate_text("👤 MASUKKAN DATA ANDA")
    print("✧"*40)
    
    name = input("\033[1;33m📝 Nama Lengkap: \033[0m").strip()
    phone = input("\033[1;33m📱 Nomor HP: \033[0m").strip()
    
    animate_text("\n🔍 Mencari data booking...")
    loading_animation(1.5)
    
    # Cari data booking online
    online_bookings = load_json(ONLINE_FILE)
    customer_bookings = [b for b in online_bookings 
                        if b['nama'].lower() == name.lower() 
                        and b['telepon'] == phone]
    
    # Jika tidak ditemukan
    if not customer_bookings:
        print("\n" + "✧"*60)
        animate_text("❌ TIDAK ADA DATA BOOKING DITEMUKAN!")
        print("✧"+"✧"*60)
        print("\n\033[1;33mPeriksa kembali nama dan nomor HP yang Anda masukkan.\033[0m")
        return
    
    ruangan_list = load_json(RUANGAN_FILE)
    
    # Tampilkan hasil pencarian
    clear_screen()
    print("\n" + "✧"*70)
    animate_text(f"📋 STATUS BOOKING UNTUK: {name.upper()}")
    print("✧"*70)
    
    for booking in customer_bookings:
        room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
        room_name = room['jenis'] if room else f"Ruangan ID {booking['ruangan_id']}"
        
        status = "\033[1;32m✅ TELAH DIKONFIRMASI\033[0m" if booking['status'] == 'confirmed' else "\033[1;33m⌛ MENUNGGU KONFIRMASI\033[0m"
        
        print(f"\n\033[1;34m🎮 Ruangan: \033[1;33m{room_name}")
        print(f"\033[1;34m📅 Tanggal: \033[1;33m{booking['tanggal']}")
        print(f"\033[1;34m⏰ Waktu: \033[1;33m{booking['jam_mulai']:02d}:00-{booking['jam_mulai']+booking['durasi']:02d}:00")
        print(f"\033[1;34m📞 No. HP: \033[1;33m{booking['telepon']}")
        print(f"\033[1;34m🔄 Status: {status}")
        print("-"*60)
    
    print("\n" + "✧"*70)
    input("\n\033[1;36m🎮 Tekan Enter untuk kembali...\033[0m")

#-----CUSTOMER MENU-----
def customer_menu():
    ruangan_list = load_json(RUANGAN_FILE)
    history_list = load_json(HISTORY_FILE)
    
    while True:
        clear_screen()
        show_banner()
        animate_text("🛎️  CUSTOMER MENU:")
        
        # ASCII menu box - aligned version
        print("""
\033[1;36m╔══════════════════════════════════════╗
║                                      ║
║   \033[1;33m1. 🔍  Lihat Ruangan Tersedia      \033[1;36m║
║   \033[1;33m2. 📅  Booking Online              \033[1;36m║
║   \033[1;33m3. 📋  Cek Status Booking          \033[1;36m║
║   \033[1;33m0. 🚪  Keluar                      \033[1;36m║
║                                      ║
╚══════════════════════════════════════╝
\033[0m""")

        
        # Blinking cursor effect
        for _ in range(2):
            print("\033[1;33m🎮 Pilih menu (0-3): \033[5m_\033[0m", end='\r')
            time.sleep(0.3)
            print(" " * 50, end='\r')
            time.sleep(0.3)
        
        choice = input("\033[1;33m🎮 Pilih menu (0-3): \033[0m")

        if choice == '1':
            clear_screen()
            animate_text("🔍 MEMUAT DAFTAR RUANGAN...")
            loading_animation(1)
            show_available_rooms(ruangan_list, history_list)
            input("\n\033[1;36m🎮 Tekan Enter untuk kembali...\033[0m")
            
        elif choice == '2':
            online_booking(ruangan_list, history_list)
            input("\n\033[1;36m🎮 Tekan Enter untuk kembali...\033[0m")
            
        elif choice == '3':
            check_booking_status()
            
        elif choice == '0':
            clear_screen()
            show_banner()
            print("\n" + "="*60)
            animate_text("🎉 Thank you for playing!")
            animate_text("      See you next round! 👋")
            print("="*60)
            
            # Game over animation
            for i in range(3):
                print(" " * i + "GAME OVER" + " " * (5-i))
                time.sleep(0.3)
                print("\033[F" + " " * 50 + "\033[F")
            
            # Final controller animation
            for i in range(5):
                print(" " * i + "🕹️" + " " * (10-i*2) + "🎮")
                time.sleep(0.2)
                if i < 4:
                    print("\033[F" + " " * 50 + "\033[F")
            
            time.sleep(2)
            break
            
        else:
            # Error flash effect
            for _ in range(3):
                print("\033[1;41m❌ Pilihan tidak valid!\033[0m", end='\r')
                time.sleep(0.2)
                print(" " * 50, end='\r')
                time.sleep(0.2)
            time.sleep(0.5)

if __name__ == "__main__":
    customer_menu()