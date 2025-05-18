from utils import load_json, save_json, next_id, RUANGAN_FILE, CUSTOMER_FILE, HISTORY_FILE
from datetime import datetime, date
import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def manage_admin_account():
    from auth import change_admin_password
    change_admin_password()

def validate_date(input_date):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return None

def get_available_hours(history_list, ruangan_id, tanggal):
    booked_hours = [q['jam'] for q in history_list 
                   if q['ruangan_id'] == ruangan_id and q['tanggal'] == tanggal]
    return [h for h in range(7, 23) if h not in booked_hours]

def format_time_range(start_hour, duration):
    end_hour = start_hour + duration
    return f"{start_hour:02d}:00-{end_hour:02d}:00"

# --- RUANGAN OPERATIONS ---
def add_ruangan(ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*20 + "➕ TAMBAH RUANGAN")
    print("═"*50 + "\033[0m")
    
    print("\n\033[1;34mPilih Jenis Ruangan:\033[0m")
    print("\033[1;32m1. 🎮 Regular Room (Kapasitas: 2)\033[0m")
    print("\033[1;33m2. 💎 VIP Room (Kapasitas: 3)\033[0m")
    print("\033[1;35m3. ✨ VVIP Room (Kapasitas: 6)\033[0m")
    
    jenis_options = {1: 'Regular', 2: 'VIP', 3: 'VVIP'}
    while True:
        try:
            jenis_choice = int(input("\n\033[1;34m⌨ Pilih jenis ruangan (1-3): \033[0m"))
            if jenis_choice in jenis_options:
                jenis = jenis_options[jenis_choice]
                break
            else:
                print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 1-3.\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka!\033[0m")

    # Set default values based on room type
    if jenis == 'Regular':
        kapasitas = 2
        console_options = ['PS4', 'PS5']
    elif jenis == 'VIP':
        kapasitas = 3
        console_options = ['Nintendo Switch', 'PS5']
    else:  # VVIP
        kapasitas = 6
        console_options = ['Nintendo Switch', 'PS5']

    print("\n\033[1;34m🕹️ Console yang tersedia:\033[0m")
    for i, c in enumerate(console_options, 1):
        print(f"\033[1;33m{i}. {c}\033[0m")
    
    chosen_console = []
    while True:
        choices = input("\n\033[1;34m🎮 Pilih console (pisahkan dengan koma jika lebih dari satu): \033[0m")
        try:
            nums = [int(x.strip()) for x in choices.split(',') if x.strip()]
            valid = all(1 <= n <= len(console_options) for n in nums)
            if not valid:
                print("\033[1;31m❌ Pilihan tidak valid! Harap pilih angka yang tersedia.\033[0m")
                continue
            chosen_console = [console_options[n-1] for n in nums]
            break
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka! Pisahkan dengan koma jika memilih lebih dari satu.\033[0m")

    ruangan_id = next_id(ruangan_list)
    new_room = {
        'id': ruangan_id,
        'jenis': jenis,
        'kapasitas': kapasitas,
        'console': chosen_console
    }
    ruangan_list.append(new_room)
    save_json(RUANGAN_FILE, ruangan_list)
    
    print("\n\033[1;32m✓ Ruangan berhasil ditambahkan!\033[0m")
    print(f"\033[1;36mID Ruangan: {ruangan_id}")
    print(f"Jenis: {jenis}")
    print(f"Kapasitas: {kapasitas} orang")
    print(f"Console: {', '.join(chosen_console)}\033[0m\n")
    time.sleep(1.5)

def view_ruangan(ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*20 + "📋 DAFTAR RUANGAN")
    print("═"*50 + "\033[0m")
    
    if not ruangan_list:
        print("\n\033[1;31m⚠ Tidak ada ruangan yang tersedia!\033[0m\n")
        time.sleep(1)
        return
    
    print("\n\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
        "ID", "Jenis", "Kapasitas", "Console"))
    print("\033[1;34m" + "-"*52 + "\033[0m")
    
    for r in ruangan_list:
        console_str = ', '.join(r['console'])
        print("\033[1;32m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
            r['id'], r['jenis'], f"{r['kapasitas']} orang", console_str))
    
    print("\033[1;34m" + "-"*52 + "\033[0m\n")
    time.sleep(1)

def edit_ruangan(ruangan_list):
    view_ruangan(ruangan_list)
    if not ruangan_list:
        return
    
    try:
        ruangan_id = int(input("\n\033[1;34m⌨ Masukkan ID ruangan yang ingin diedit: \033[0m"))
    except ValueError:
        print("\033[1;31m❌ Input harus berupa angka!\033[0m")
        time.sleep(1)
        return
    
    room = next((r for r in ruangan_list if r['id'] == ruangan_id), None)
    if not room:
        print("\033[1;31m❌ Ruangan tidak ditemukan!\033[0m")
        time.sleep(1)
        return
    
    print(f"\n\033[1;36m✏ Mengedit Ruangan ID {ruangan_id}\033[0m")
    print("\033[1;35m" + "-"*50 + "\033[0m")
    
    jenis_options = ['Regular', 'VIP', 'VVIP']
    jenis_input = input(f"\033[1;34mJenis ruangan ({room['jenis']}) [kosongkan jika tidak berubah]: \033[0m").strip()
    if jenis_input:
        if jenis_input in jenis_options:
            room['jenis'] = jenis_input
            print("\033[1;32m✓ Jenis ruangan diperbarui\033[0m")
        else:
            print("\033[1;31m❌ Jenis ruangan tidak valid! (Regular/VIP/VVIP)\033[0m")

    kapasitas_input = input(f"\033[1;34mKapasitas ({room['kapasitas']}) [kosongkan jika tidak berubah]: \033[0m").strip()
    if kapasitas_input:
        try:
            k = int(kapasitas_input)
            if k > 0:
                room['kapasitas'] = k
                print("\033[1;32m✓ Kapasitas diperbarui\033[0m")
            else:
                print("\033[1;31m❌ Kapasitas harus lebih dari 0!\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka!\033[0m")

    console_input = input(f"\033[1;34mConsole ({', '.join(room['console'])}) [pisahkan dengan koma, kosongkan jika tidak berubah]: \033[0m").strip()
    if console_input:
        consoles = [c.strip() for c in console_input.split(',') if c.strip()]
        if consoles:
            room['console'] = consoles
            print("\033[1;32m✓ Console diperbarui\033[0m")
        else:
            print("\033[1;31m❌ Daftar console tidak boleh kosong!\033[0m")
    
    save_json(RUANGAN_FILE, ruangan_list)
    print("\n\033[1;32m✓ Data ruangan berhasil diperbarui!\033[0m")
    time.sleep(1.5)

def delete_ruangan(ruangan_list, history_list, customer_list):
    view_ruangan(ruangan_list)
    if not ruangan_list:
        return
    
    try:
        ruangan_id = int(input("\n\033[1;34m⌨ Masukkan ID ruangan yang ingin dihapus: \033[0m"))
    except ValueError:
        print("\033[1;31m❌ Input harus berupa angka!\033[0m")
        time.sleep(1)
        return
    
    room = next((r for r in ruangan_list if r['id'] == ruangan_id), None)
    if not room:
        print("\033[1;31m❌ Ruangan tidak ditemukan!\033[0m")
        time.sleep(1)
        return
    
    booked = any(q['ruangan_id'] == ruangan_id for q in history_list)
    if booked:
        print("\033[1;31m❌ Ruangan ini memiliki booking aktif dan tidak dapat dihapus!\033[0m")
        time.sleep(1.5)
        return
    
    # Confirmation
    print(f"\n\033[1;31m⚠ ANDA AKAN MENGHAPUS:\033[0m")
    print(f"\033[1;33mID: {room['id']}")
    print(f"Jenis: {room['jenis']}")
    print(f"Kapasitas: {room['kapasitas']} orang")
    print(f"Console: {', '.join(room['console'])}\033[0m")
    
    confirm = input("\n\033[1;31mApakah Anda yakin? (y/n): \033[0m").lower()
    if confirm != 'y':
        print("\033[1;33m🛑 Penghapusan dibatalkan\033[0m")
        time.sleep(1)
        return
    
    # Update customer bookings
    for cust in customer_list:
        cust['booking'] = [b for b in cust.get('booking', []) if b['ruangan_id'] != ruangan_id]
    
    ruangan_list.remove(room)
    save_json(RUANGAN_FILE, ruangan_list)
    save_json(CUSTOMER_FILE, customer_list)
    
    print("\n\033[1;32m✓ Ruangan berhasil dihapus!\033[0m")
    time.sleep(1.5)

# --- CUSTOMER OPERATIONS ---
def add_customer(customer_list, ruangan_list, history_list):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*12 + "🌟 TAMBAH CUSTOMER BARU")
    print("═"*50 + "\033[0m")

    print("\n\033[1;34m📝 Masukkan Data Customer\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")

    while True:
        nama = input("\033[1;34m⌨ Nama Customer: \033[0m").strip()
        if not nama:
            print("\033[1;31m❌ Nama tidak boleh kosong!\033[0m")
            continue
        break
    
    # Input tanggal booking
    print("\n\033[1;34m📅 Pilih Tanggal Booking\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")
    while True:
        input_date = input("\033[1;34m⌨ Tanggal booking (YYYY-MM-DD): \033[0m").strip()
        booking_date = validate_date(input_date)
        if booking_date:
            if booking_date >= date.today():
                break
            print("\033[1;31m❌ Tanggal tidak boleh di masa lalu!\033[0m")
        else:
            print("\033[1;31m❌ Format tanggal salah. Gunakan YYYY-MM-DD.\033[0m")
    
    # Tampilkan ruangan tersedia
    view_ruangan(ruangan_list)
    
    try:
        ruangan_id = int(input("\nPilih ID ruangan untuk booking: "))
    except ValueError:
        print("Input harus angka.")
        return
    
    selected_room = next((r for r in ruangan_list if r['id'] == ruangan_id), None)
    if not selected_room:
        print("Ruangan tidak ditemukan.")
        return
    
    # Tampilkan jam tersedia dalam format menu
    available_hours = get_available_hours(history_list, ruangan_id, str(booking_date))
    
    if not available_hours:
        print(f"\nRuangan ini sudah penuh pada tanggal {booking_date}.")
        return
    
    print(f"\nJam tersedia pada {booking_date}:")
    print("="*40)
    for i, hour in enumerate(available_hours, 1):
        print(f"{i}. {hour:02d}:00-{hour+1:02d}:00")  # Format 07:00-08:00
    print("="*40)
    
    # Pilih jam dengan menu
    while True:
        try:
            choice = int(input("\n\033[1;34m⌨ Pilih nomor jam (contoh: 1): \033[0m"))
            if 1 <= choice <= len(available_hours):
                jam_mulai = available_hours[choice-1]
                break
            else:
                print(f"\033[1;31m❌ Harap pilih antara 1-{len(available_hours)}!\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka!\033[0m")
    
    # Input durasi
    print("\n\033[1;34m⏳ Pilih Durasi Booking\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")
    try:
        durasi = int(input("\033[1;34m⌨ Durasi (jam, max 4 jam): \033[0m"))
        durasi = min(durasi, 4)
    except ValueError:
        print("\033[1;31m❌ Input harus berupa angka!\033[0m")
        time.sleep(1)
        return

    if durasi < 1:
        print("\033[1;31m❌ Durasi minimal 1 jam!\033[0m")
        time.sleep(1)
        return

    selected_hours = range(jam_mulai, jam_mulai + durasi)
    for hour in selected_hours:
        if hour > 22:
            print("\033[1;31m❌ Melebihi jam operasional (22:00)!\033[0m")
            time.sleep(1)
            return
        if hour not in available_hours:
            print(f"\033[1;31m❌ Jam {hour}:00 sudah dipesan!\033[0m")
            time.sleep(1)
            return
    
    # Konfirmasi booking
    print("\n\033[1;34m🔍 Ringkasan Booking:\033[0m")
    print("\033[1;36m" + "─"*50 + "\033[0m")
    print(f"\033[1;33m• Nama     : {nama}")
    print(f"• Ruangan  : {selected_room['jenis']} (ID: {ruangan_id})")
    print(f"• Tanggal  : {booking_date}")
    print(f"• Jam      : {jam_mulai:02d}:00-{jam_mulai+durasi:02d}:00")
    print(f"• Durasi   : {durasi} jam\033[0m")
    print("\033[1;36m" + "─"*50 + "\033[0m")
    
    confirm = input("\n\033[1;34m🔎 Konfirmasi booking (y/n)? \033[0m").lower()
    if confirm != 'y':
        print("\033[1;33m⚠️ Booking dibatalkan\033[0m")
        time.sleep(1)
        return
    
    # Simpan data
    cust_id = next_id(customer_list)
    new_customer = {
        'id': cust_id,
        'nama': nama,
        'booking': [{
            'ruangan_id': ruangan_id,
            'tanggal': str(booking_date),
            'jam': hour,
            'online': False
        } for hour in selected_hours]
    }
    customer_list.append(new_customer)

    for hour in selected_hours:
        add_to_history(history_list, cust_id, ruangan_id, str(booking_date), hour, online=False)

    save_json(CUSTOMER_FILE, customer_list)
    save_json(HISTORY_FILE, history_list)
    
    print("\n\033[1;32m✅ BOOKING BERHASIL!\033[0m")
    print("\033[1;36m" + "═"*50 + "\033[0m")
    print(f"\033[1;33mID Customer : {cust_id}")
    print(f"Nama        : {nama}")
    print(f"Ruangan     : {selected_room['jenis']}")
    print(f"Tanggal     : {booking_date}")
    print(f"Jam         : {jam_mulai:02d}:00-{jam_mulai+durasi:02d}:00\033[0m")
    print("\033[1;36m" + "═"*50 + "\033[0m")
    time.sleep(2)

def view_customer(customer_list, ruangan_list):
    if not customer_list:
        print("\n\033[1;31mData customer kosong.\033[0m\n")
        return
    
    print("\n\033[1;36m╔══════════════════════════════════════════════════════════════════════╗")
    print("║" + " " * 26 + "📋 DAFTAR CUSTOMER" + " " * 26 + "║")
    print("╚══════════════════════════════════════════════════════════════════════╝\033[0m")
    
    # Header with color and fixed widths
    print("\033[1;35m{:<5} {:<20} {:<8} {:<15} {:<15} {:<10}\033[0m".format(
        "ID", "Nama", "Ruang ID", "Jenis Ruang", "Jam", "Status"
    ))
    print("\033[1;34m" + "─" * 78 + "\033[0m")
    
    for c in customer_list:
        # Customer ID and Name
        print("\033[1;32m{:<5}\033[0m \033[1;33m{:<20}\033[0m".format(c['id'], c['nama']), end="")
        
        bookings = c.get('booking', [])
        if not bookings:
            print("\033[1;31m{:<8} {:<15} {:<15} {:<10}\033[0m".format("-", "-", "-", "-"))
            print("\033[1;34m" + "─" * 78 + "\033[0m")
            continue
            
        # First booking details
        first_booking = bookings[0]
        room = next((r for r in ruangan_list if r['id'] == first_booking['ruangan_id']), None)
        
        # Perbaikan di sini - pastikan room adalah dictionary
        room_type = room['jenis'] if isinstance(room, dict) and 'jenis' in room else "Unknown"
        
        print("\033[1;36m{:<8}\033[0m {:<15} \033[1;35m{:<15}\033[0m \033[1;{}m{:<10}\033[0m".format(
            first_booking['ruangan_id'],
            room_type,
            f"{first_booking['jam']:02d}:00-{first_booking['jam']+1:02d}:00",
            '32' if first_booking.get('online', False) else '31',
            "Online" if first_booking.get('online', False) else "Offline"
        ))
        
        # Additional bookings
        for b in bookings[1:]:
            room = next((r for r in ruangan_list if r['id'] == b['ruangan_id']), None)
            
            # Perbaikan yang sama untuk booking tambahan
            room_type = room['jenis'] if isinstance(room, dict) and 'jenis' in room else "Unknown"
            
            print("{:<25} \033[1;36m{:<8}\033[0m {:<15} \033[1;35m{:<15}\033[0m \033[1;{}m{:<10}\033[0m".format(
                "",  # Empty space under name
                b['ruangan_id'],
                room_type,
                f"{b['jam']:02d}:00-{b['jam']+1:02d}:00",
                '32' if b.get('online', False) else '31',
                "Online" if b.get('online', False) else "Offline"
            ))
        
        print("\033[1;34m" + "─" * 78 + "\033[0m")

def edit_customer(customer_list, ruangan_list):
    """Edit customer data with enhanced UI/UX"""
    clear_screen()
    print("\033[1;36m" + "="*50)
    print(" "*18 + "✏️ EDIT CUSTOMER")
    print("="*50 + "\033[0m")
    
    # Tampilkan daftar customer dengan animasi
    print("\n\033[1;35mLoading customer data...\033[0m")
    time.sleep(0.5)
    view_customer(customer_list, ruangan_list)
    
    if not customer_list:
        print("\n\033[1;31m⚠️ Tidak ada data customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    try:
        print("\n\033[1;33m" + "─"*50 + "\033[0m")
        cust_id = int(input("\033[1;34m⌨ Masukkan ID customer yang ingin diedit: \033[0m"))
    except ValueError:
        print("\n\033[1;31m❌ Error: Input harus berupa angka!\033[0m")
        time.sleep(1.5)
        return
    
    cust = next((c for c in customer_list if c['id'] == cust_id), None)
    if not cust:
        print("\n\033[1;31m❌ Customer dengan ID tersebut tidak ditemukan!\033[0m")
        time.sleep(1.5)
        return
    
    print("\n\033[1;32m✓ Customer ditemukan:\033[0m")
    print(f"\033[1;33mNama saat ini: {cust['nama']}\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")
    
    new_name = input("\033[1;34m✨ Masukkan nama baru (kosongkan untuk batal): \033[0m").strip()
    
    if new_name:
        cust['nama'] = new_name
        save_json(CUSTOMER_FILE, customer_list)
        print("\n\033[1;32m✓ Data customer berhasil diperbarui!\033[0m")
        print(f"\033[1;36mID: {cust['id']} | Nama baru: {cust['nama']}\033[0m")
    else:
        print("\n\033[1;33m⚠️ Perubahan dibatalkan, nama tidak berubah.\033[0m")
    
    time.sleep(1.5)

def delete_customer(customer_list, history_list, ruangan_list=None):
    """Delete a customer with enhanced UI/UX and proper validation"""
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*18 + "🗑️ HAPUS CUSTOMER")
    print("═"*50 + "\033[0m")
    
    # Load room data if not provided
    if ruangan_list is None:
        ruangan_list = load_json(RUANGAN_FILE)
    
    # Show customer list with loading animation
    print("\n\033[1;33mMemuat data customer...\033[0m")
    time.sleep(0.5)
    view_customer(customer_list, ruangan_list)
    
    if not customer_list:
        print("\n\033[1;31m⚠️ Tidak ada customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    # Get customer ID to delete
    print("\n\033[1;35m" + "─"*50 + "\033[0m")
    try:
        cust_id = int(input("\033[1;34m⌨ Masukkan ID customer yang akan dihapus: \033[0m"))
    except ValueError:
        print("\n\033[1;31m❌ Error: ID harus berupa angka!\033[0m")
        time.sleep(1.5)
        return
    
    # Find customer
    cust = next((c for c in customer_list if c['id'] == cust_id), None)
    if not cust:
        print("\n\033[1;31m❌ Customer tidak ditemukan!\033[0m")
        time.sleep(1.5)
        return
    
    # Show customer details
    print("\n\033[1;31m⚠️ DATA CUSTOMER YANG AKAN DIHAPUS:\033[0m")
    print(f"\033[1;33mID     : {cust['id']}")
    print(f"Nama   : {cust['nama']}")
    
    # Show booking info if exists
    if cust.get('booking'):
        print("\n\033[1;36mBOOKING AKTIF:\033[0m")
        for booking in cust['booking']:
            room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
            room_type = room['jenis'] if room else "Unknown"
            print(f"- {room_type} | {booking['tanggal']} | {booking['jam']:02d}:00-{booking['jam']+1:02d}:00")
    
    print("\033[1;35m" + "─"*50 + "\033[0m")
    
    # Confirmation
    confirm = input("\033[1;31mApakah Anda yakin ingin menghapus? (y/n): \033[0m").lower()
    if confirm != 'y':
        print("\n\033[1;33m🛑 Penghapusan dibatalkan\033[0m")
        time.sleep(1)
        return
    
    # Perform deletion
    try:
        # Remove from queue
        history_list[:] = [q for q in history_list if q['customer_id'] != cust_id]
        
        # Remove customer
        customer_list.remove(cust)
        
        # Save changes
        save_json(CUSTOMER_FILE, customer_list)
        save_json(HISTORY_FILE, history_list)
        
        print("\n\033[1;32m✓ Customer berhasil dihapus!\033[0m")
        print(f"\033[1;36mID {cust_id} - {cust['nama']} telah dihapus dari sistem\033[0m")
        
    except Exception as e:
        print("\n\033[1;31m❌ Gagal menghapus customer:\033[0m")
        print(f"\033[1;33mError: {str(e)}\033[0m")
    
    time.sleep(1.5)

# --- HISTORY MANAGEMENT ---
def view_riwayat(history_list, customer_list, ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*80)
    print(" "*30 + "📋 DAFTAR BOOKING")
    print("═"*80 + "\033[0m")
    
    if not history_list:
        print("\n\033[1;31m⚠ Tidak ada riwayat booking yang tersedia!\033[0m\n")
        time.sleep(1)
        return
    
    # Urutkan riwayat berdasarkan tanggal dan jam
    sorted_queue = sorted(history_list, key=lambda x: (x['tanggal'], x['jam']))
    
    print("\n\033[1;35m{:<5} {:<12} {:<25} {:<15} {:<15} {:<10}\033[0m".format(
        "No", "Tanggal", "Customer", "Ruangan", "Jam", "Status"))
    print("\033[1;34m" + "─"*80 + "\033[0m")
    
    for idx, q in enumerate(sorted_queue, 1):
        cust_name = next((c['nama'] for c in customer_list if c['id'] == q['customer_id']), "Unknown")
        room_type = next((r['jenis'] for r in ruangan_list if r['id'] == q['ruangan_id']), "Unknown")
        
        status_color = "32" if q['online'] else "31"  # Green for online, red for offline
        status_text = "Online" if q['online'] else "Offline"
        
        print("{:<5} {:<12} \033[1;33m{:<25}\033[0m {:<15} {:<15} \033[1;{}m{:<10}\033[0m".format(
            idx,
            q['tanggal'],
            cust_name,
            room_type,
            f"{q['jam']:02d}:00-{q['jam']+1:02d}:00",
            status_color,
            status_text))
    
    print("\033[1;34m" + "─"*80 + "\033[0m")
    print(f"\n\033[1;36mTotal riwayat: {len(history_list)}\033[0m")
    time.sleep(1.5)

def add_to_history(history_list, customer_id, ruangan_id, tanggal, jam, online):
    # Cek apakah ruangan sudah dipesan di tanggal dan jam yang sama
    for q in history_list:
        if (q['ruangan_id'] == ruangan_id and 
            q['tanggal'] == tanggal and 
            q['jam'] == jam):
            print("\033[1;31m❌ Ruangan sudah dipesan pada jam tersebut!\033[0m")
            return False
    
    history_list.append({
        'customer_id': customer_id,
        'ruangan_id': ruangan_id,
        'tanggal': tanggal,
        'jam': jam,
        'online': online,
        'waktu_booking': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(HISTORY_FILE, history_list)
    print("\033[1;32m✓ Booking berhasil ditambahkan ke riwayat!\033[0m")
    return True

# --- SEARCH & SORT FUNCTIONS ---
def search_sort_ruangan(ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*60)
    print(" "*20 + "🔍 CARI & URUTKAN RUANGAN")
    print("═"*60 + "\033[0m")
    
    if not ruangan_list:
        print("\n\033[1;31m⚠ Tidak ada data ruangan yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    print("\n\033[1;34mPilih Menu:\033[0m")
    print("\033[1;32m1. Cari berdasarkan Jenis Ruangan\033[0m")
    print("\033[1;33m2. Urutkan berdasarkan Kapasitas\033[0m")
    print("\033[1;31m0. Kembali ke Menu Utama\033[0m")
    
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-2): \033[0m")
        
        if choice == '1':
            keyword = input("\n\033[1;34m⌨ Masukkan jenis ruangan (Regular/VIP/VVIP): \033[0m").lower()
            hasil = [r for r in ruangan_list if r['jenis'].lower() == keyword]
            
            if not hasil:
                print("\n\033[1;31m❌ Tidak ada ruangan dengan jenis tersebut!\033[0m")
            else:
                print("\n\033[1;32m✓ Hasil Pencarian:\033[0m")
                print("\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
                    "ID", "Jenis", "Kapasitas", "Console"))
                print("\033[1;34m" + "─"*60 + "\033[0m")
                for r in hasil:
                    print("\033[1;36m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
                        r['id'], r['jenis'], f"{r['kapasitas']} orang", ', '.join(r['console'])))
            break
            
        elif choice == '2':
            print("\n\033[1;34mPilih Urutan:\033[0m")
            print("\033[1;32m1. Kapasitas Terkecil ke Terbesar\033[0m")
            print("\033[1;33m2. Kapasitas Terbesar ke Terkecil\033[0m")
            
            sort_choice = input("\n\033[1;34m⌨ Pilihan Anda (1-2): \033[0m")
            
            if sort_choice == '1':
                sorted_ruangan = sorted(ruangan_list, key=lambda r: r['kapasitas'])
                print("\n\033[1;32m✓ Urutkan dari Kapasitas Terkecil:\033[0m")
            elif sort_choice == '2':
                sorted_ruangan = sorted(ruangan_list, key=lambda r: r['kapasitas'], reverse=True)
                print("\n\033[1;32m✓ Urutkan dari Kapasitas Terbesar:\033[0m")
            else:
                print("\033[1;31m❌ Pilihan tidak valid!\033[0m")
                continue
                
            print("\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
                "ID", "Jenis", "Kapasitas", "Console"))
            print("\033[1;34m" + "─"*60 + "\033[0m")
            for r in sorted_ruangan:
                print("\033[1;36m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
                    r['id'], r['jenis'], f"{r['kapasitas']} orang", ', '.join(r['console'])))
            break
            
        elif choice == '0':
            return
            
        else:
            print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 0-2.\033[0m")
    
    time.sleep(1.5)

def search_sort_customer(customer_list):
    clear_screen()
    print("\033[1;36m" + "═"*60)
    print(" "*20 + "🔍 CARI & URUTKAN CUSTOMER")
    print("═"*60 + "\033[0m")
    
    if not customer_list:
        print("\n\033[1;31m⚠ Tidak ada data customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    print("\n\033[1;34mPilih Menu:\033[0m")
    print("\033[1;32m1. Cari berdasarkan Nama\033[0m")
    print("\033[1;33m2. Urutkan dari A-Z\033[0m")
    print("\033[1;35m3. Urutkan dari Z-A\033[0m")
    print("\033[1;31m0. Kembali ke Menu Utama\033[0m")
    
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-3): \033[0m")
        
        if choice == '1':
            keyword = input("\n\033[1;34m⌨ Masukkan nama customer: \033[0m").lower()
            hasil = [c for c in customer_list if keyword in c['nama'].lower()]
            
            if not hasil:
                print("\n\033[1;31m❌ Customer tidak ditemukan!\033[0m")
            else:
                print("\n\033[1;32m✓ Hasil Pencarian:\033[0m")
                print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
                print("\033[1;34m" + "─"*40 + "\033[0m")
                for c in hasil:
                    print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(c['id'], c['nama']))
            break
            
        elif choice == '2':
            sorted_cust = sorted(customer_list, key=lambda c: c['nama'].lower())
            print("\n\033[1;32m✓ Urutkan dari A-Z:\033[0m")
            print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
            print("\033[1;34m" + "─"*40 + "\033[0m")
            for c in sorted_cust:
                print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(c['id'], c['nama']))
            break
            
        elif choice == '3':
            sorted_cust = sorted(customer_list, key=lambda c: c['nama'].lower(), reverse=True)
            print("\n\033[1;32m✓ Urutkan dari Z-A:\033[0m")
            print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
            print("\033[1;34m" + "─"*40 + "\033[0m")
            for c in sorted_cust:
                print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(c['id'], c['nama']))
            break
            
        elif choice == '0':
            return
            
        else:
            print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 0-3.\033[0m")
    
    time.sleep(1.5)

def admin_menu():
    ruangan_list = load_json(RUANGAN_FILE)
    customer_list = load_json(CUSTOMER_FILE)
    history_list = load_json(HISTORY_FILE)

    while True:
        clear_screen()
        print("\033[1;35m" + "="*50)
        print(" "*18 + "🔒 ADMIN DASHBOARD")
        print("="*50 + "\033[0m")
        
        print("\n\033[1;34m🛠️  MAIN MENU\033[0m")
        print("\033[1;36m1. 🏠 Kelola Ruangan Gaming")
        print("2. 👥 Kelola Data Customer")
        print("3. 📋 Lihat Riwayat Booking")
        print("4. 🔍 Cari/Urutkan Data")
        print("5. 🔐 Ubah Password Admin")
        print("0. 🚪 Logout\033[0m")
        print("\033[1;35m" + "="*50 + "\033[0m")
        
        choice = input("\n\033[1;33m🔹 Pilih menu (0-5): \033[0m")

        if choice == '1':
            while True:
                clear_screen()
                print("\033[1;36m" + "="*50)
                print(" "*18 + "🏠 MANAGE ROOMS")
                print("="*50 + "\033[0m")
                
                print("\n1. ➕ Tambah Ruangan Baru")
                print("2. 👀 Lihat Daftar Ruangan")
                print("3. ✏️  Edit Data Ruangan")
                print("4. ❌ Hapus Ruangan")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    add_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    view_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '3':
                    edit_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '4':
                    delete_ruangan(ruangan_list, history_list, customer_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '2':
            while True:
                clear_screen()
                print("\033[1;36m" + "="*50)
                print(" "*18 + "👥 MANAGE CUSTOMERS")
                print("="*50 + "\033[0m")
                
                print("\n1. ➕ Tambah Customer Baru")
                print("2. 👀 Lihat Daftar Customer")
                print("3. ✏️  Edit Data Customer")
                print("4. ❌ Hapus Customer")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    add_customer(customer_list, ruangan_list, history_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    view_customer(customer_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '3':
                    edit_customer(customer_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '4':
                    delete_customer(customer_list, history_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '3':
            clear_screen()
            print("\033[1;36m" + "="*50)
            print(" "*18 + "📋 BOOKING QUEUE")
            print("="*50 + "\033[0m")
            view_riwayat(history_list, customer_list, ruangan_list)
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")

        elif choice == '4':
            while True:
                clear_screen()
                print("\033[1;36m" + "="*50)
                print(" "*18 + "🔍 SEARCH & SORT")
                print("="*50 + "\033[0m")
                
                print("\n1. 🔎 Cari/Urutkan Ruangan")
                print("2. 🔎 Cari/Urutkan Customer")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    search_sort_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    search_sort_customer(customer_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '5':
            clear_screen()
            print("\033[1;36m" + "="*50)
            print(" "*18 + "🔐 CHANGE PASSWORD")
            print("="*50 + "\033[0m")
            manage_admin_account()
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
        
        elif choice == '0':
            print("\n\033[1;32m✔️ Logging out...\033[0m")
            time.sleep(1)
            break
            
        else:
            print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
            time.sleep(1)
        
        # Save changes after each operation
        save_json(RUANGAN_FILE, ruangan_list)
        save_json(CUSTOMER_FILE, customer_list)
        save_json(HISTORY_FILE, history_list)